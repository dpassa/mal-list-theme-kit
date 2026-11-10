/*
 * MAL list theme – in-page check.
 *
 * Run it on a MyAnimeList modern list page (https://myanimelist.net/animelist/<user>):
 *   - by an agent, through a browser tool that executes JavaScript in the page, or
 *   - by a person, pasted into the browser DevTools console.
 *
 * Optional inputs, set BEFORE running this script:
 *   window.MAL_CHECK = {
 *     css: "...",              // candidate CSS: previewed in THIS TAB ONLY, nothing is saved
 *     expectFont: "Nunito",    // first font family the text should use
 *     minContrast: 4.5         // WCAG AA for normal text (large text uses 3)
 *   };
 *
 * It returns (and logs) a JSON report: { pass, failures[], warnings[], manual[], info }.
 * Undo the preview with window.__malCheckRestore() or by reloading the page.
 *
 * Nothing here talks to MAL's servers or changes account settings. The only
 * interaction is opening/closing the search box, which is local UI.
 */
(async () => {
  const opts = Object.assign({ css: null, expectFont: null, minContrast: 4.5 }, window.MAL_CHECK || {});
  const failures = [], warnings = [], manual = [], info = {};
  const fail = (check, detail) => failures.push({ check, detail });
  const warn = (check, detail) => warnings.push({ check, detail });

  if (!document.body.classList.contains('ownlist') || !document.querySelector('.list-table')) {
    return { pass: false, failures: [{ check: 'page', detail: 'Not a modern MAL list page (body.ownlist + .list-table not found). Classic lists are not supported.' }] };
  }

  // ---------- 1. Preview the candidate CSS in place of the saved custom CSS ----------
  // On the list page MAL inlines: <style>(base list style)</style><style>(user custom CSS)</style>
  // and only THEN links the site stylesheet. The custom CSS therefore loses ties against the site
  // stylesheet, which is why !important is needed. We insert the candidate at the same position
  // so the preview behaves like the real thing.
  // Undo a previous preview FIRST, so the page is back to its saved state
  // before we look for the saved custom <style>.
  window.__malCheckRestore?.();
  const siteLink = document.querySelector('link[href*="/static/assets/css/pc/style-"]');
  const inlineBefore = [...document.querySelectorAll('head style:not(#mal-check-preview)')].filter(s =>
    siteLink && (s.compareDocumentPosition(siteLink) & Node.DOCUMENT_POSITION_FOLLOWING));
  const savedCustom = inlineBefore.slice(1); // [0] is the base list style
  info.savedCustomCssLength = savedCustom.reduce((n, s) => n + s.textContent.length, 0);
  if (opts.css) {
    savedCustom.forEach(s => { s.dataset.malCheckMedia = s.media || ''; s.media = 'not all'; });
    const st = document.createElement('style');
    st.id = 'mal-check-preview';
    st.textContent = opts.css;
    (savedCustom[0] || siteLink).before(st);
    window.__malCheckRestore = () => {
      st.remove();
      savedCustom.forEach(s => { s.media = s.dataset.malCheckMedia; delete s.dataset.malCheckMedia; });
      delete window.__malCheckRestore;
    };
    info.previewing = 'candidate CSS (saved custom CSS disabled in this tab only)';
    // let @import fonts load
    await new Promise(r => setTimeout(r, 1500));
    try { await document.fonts.ready; } catch (_) {}
  } else {
    info.previewing = 'saved custom CSS as it is on the page';
  }

  const visible = el => {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && +cs.opacity !== 0;
  };
  const firstFamily = ff => ff.split(',')[0].trim().replace(/^["']|["']$/g, '');
  const label = el => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') +
    (typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\s+/).join('.') : '');

  // ---------- 2. Icons (Font Awesome 6) ----------
  const iconEls = [...document.querySelectorAll('i[class*="fa-"]')];
  const iconFonts = [...document.fonts].filter(f => /font awesome/i.test(f.family));
  info.iconCount = iconEls.length;
  let iconsChecked = 0;
  for (const el of iconEls) {
    if (!visible(el)) continue;
    iconsChecked++;
    const ff = getComputedStyle(el).fontFamily;
    const before = getComputedStyle(el, '::before');
    if (!/font awesome/i.test(ff) || !/font awesome/i.test(before.fontFamily)) {
      fail('icon-font', `${label(el)} uses "${firstFamily(ff)}" instead of Font Awesome: it shows as an empty square`);
    } else if (!before.content || before.content === 'none' || before.content === 'normal' || before.content === '""') {
      fail('icon-glyph', `${label(el)} has no glyph (::before content is empty)`);
    }
  }
  info.iconsChecked = iconsChecked;
  if (iconFonts.length && !iconFonts.some(f => f.status === 'loaded')) fail('icon-font', 'Font Awesome is declared but never loaded');
  for (const sel of ['#search-button i', '.list-status-title .stats i']) {
    const el = document.querySelector(sel);
    if (!el) warn('icon-missing', `${sel} not found (MAL markup may have changed)`);
    else if (!visible(el)) fail('icon-hidden', `${sel} is not visible`);
  }

  // ---------- 3. Search box opens ----------
  const btn = document.querySelector('#search-button');
  const box = document.querySelector('#search-box');
  if (btn && box) {
    const wasOpen = box.classList.contains('open');
    if (!wasOpen) btn.click();
    await new Promise(r => setTimeout(r, 300));
    // The box opens with a width transition, which does not advance in a
    // background tab: switch the transition off just to measure the end state.
    const t = box.style.transition;
    box.style.transition = 'none';
    const w = box.getBoundingClientRect().width;
    box.style.transition = t;
    if (!box.classList.contains('open')) fail('search', 'clicking the search button did not open the search box');
    else if (w < 40) fail('search', `search box opens but is only ${Math.round(w)}px wide`);
    if (!wasOpen) btn.click();
  } else warn('search', '#search-button / #search-box not found');

  // ---------- 4. Sort arrows ----------
  const sortIcons = [...document.querySelectorAll('.list-table-header [class*="fa-arrow"], .list-table-header .sort-icon')];
  if (!sortIcons.some(visible)) manual.push('Sort arrow: it only shows on the sorted column. Click a column header (e.g. Score) and check the arrow is a glyph, not a square.');

  // ---------- 5. Fonts left on Verdana/Avenir ----------
  const scopes = '.header, .list-container, .list-menu-float, #advanced-options, #footer-block';
  const stuck = new Map();
  for (const el of document.querySelectorAll(`${scopes}, :is(${scopes}) *`)) {
    if (el.matches('i, svg, svg *, [class*="fa-"], script, style')) continue;
    const hasText = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (!hasText || !visible(el)) continue;
    const fam = firstFamily(getComputedStyle(el).fontFamily);
    if (opts.expectFont ? fam.toLowerCase() !== opts.expectFont.toLowerCase() && /verdana|avenir|arial|tahoma/i.test(fam)
                        : false) {
      const key = label(el).split('.').slice(0, 3).join('.');
      if (!stuck.has(key)) stuck.set(key, fam);
    }
  }
  if (opts.expectFont) {
    const loaded = [...document.fonts].some(f => f.family.replace(/["']/g, '').toLowerCase() === opts.expectFont.toLowerCase() && f.status === 'loaded');
    if (!loaded) warn('font-load', `"${opts.expectFont}" is not loaded: the @import may be blocked or misspelled; the fallback font is used`);
    for (const [el, fam] of stuck) fail('font-pinned', `${el} is still in ${fam}: add its selector to the font rule`);
  }

  // ---------- 6. Contrast ----------
  const parse = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); return { r: p[0], g: p[1], b: p[2], a: p[3] ?? 1 }; };
  const lum = ({ r, g, b }) => [r, g, b].map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }).reduce((s, v, i) => s + v * [0.2126, 0.7152, 0.0722][i], 0);
  const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
  const blend = (top, bottom) => ({ r: top.r * top.a + bottom.r * (1 - top.a), g: top.g * top.a + bottom.g * (1 - top.a), b: top.b * top.a + bottom.b * (1 - top.a), a: 1 });
  // Background candidates behind an element: solid colors and every stop of a gradient.
  const backgrounds = el => {
    const layers = [];
    for (let n = el; n; n = n.parentElement) {
      const cs = getComputedStyle(n);
      const img = cs.backgroundImage;
      if (img && img !== 'none' && /gradient/.test(img)) {
        const stops = (img.match(/rgba?\([^)]+\)/g) || []).map(parse).filter(Boolean);
        if (stops.length) return { layers, stops };
      }
      if (img && /url\(/.test(img) && n !== document.body) return { layers, image: true };
      const bg = parse(cs.backgroundColor);
      if (bg && bg.a > 0) { layers.push(bg); if (bg.a >= 1) return { layers, stops: [] }; }
    }
    return { layers, stops: [{ r: 255, g: 255, b: 255, a: 1 }] };
  };
  const targets = [
    ['header text', '.header .header-menu .btn-menu'],
    ['inactive tabs', '.status-menu-container .status-menu .status-button:not(.on)'],
    ['active tab', '.status-menu-container .status-menu .status-button.on'],
    ['section title', '.list-unit .list-status-title .text'],
    ['column header (sortable)', '.list-table .list-table-header .header-title .link'],
    ['column header (plain text)', '.list-table .list-table-header .header-title.tags, .list-table .list-table-header .header-title.number'],
    ['anime title', '.list-table .list-table-data .data.title .link'],
    ['row cells', '.list-table .list-table-data .data.type, .list-table .list-table-data .data.progress'],
    ['tag edit link', '.list-table .list-table-data .tags .edit'],
    ['footer', '#footer-block #copyright'],
  ];
  info.contrast = [];
  for (const [name, sel] of targets) {
    const el = [...document.querySelectorAll(sel)].find(visible);
    if (!el) { warn('contrast', `${name}: ${sel} not found/visible`); continue; }
    const cs = getComputedStyle(el);
    const fg = parse(cs.color);
    if (!fg) continue;
    const { layers, stops, image } = backgrounds(el);
    if (image) { manual.push(`${name}: text over an image, check readability on the screenshot`); continue; }
    const bases = (stops && stops.length ? stops : [{ r: 255, g: 255, b: 255, a: 1 }]);
    let worst = Infinity;
    for (const base of bases) {
      let bg = { ...base, a: 1 };
      for (const l of [...layers].reverse()) bg = blend(l, bg);
      worst = Math.min(worst, ratio(fg.a < 1 ? blend(fg, bg) : fg, bg));
    }
    const size = parseFloat(cs.fontSize), bold = +cs.fontWeight >= 700;
    const need = (size >= 24 || (bold && size >= 18.66)) ? 3 : opts.minContrast;
    const r2 = Math.round(worst * 100) / 100;
    info.contrast.push({ name, ratio: r2, need });
    if (worst < need) (worst < 3 ? fail : warn)('contrast', `${name} (${sel.split(',')[0]}): ${r2}:1, needs ${need}:1`);
  }

  // ---------- 7. Logo still there ----------
  const logo = document.querySelector('.header .header-title');
  if (logo) {
    const img = getComputedStyle(logo).backgroundImage;
    if (!/logo/i.test(img) || !visible(logo)) fail('logo', `MyAnimeList logo image is gone (background-image: ${img.slice(0, 60)})`);
  }

  // ---------- 8. Status column keeps its colors ----------
  const statusColors = {};
  for (const el of document.querySelectorAll('.list-table-data .data.status')) {
    const st = [...el.classList].find(c => !['data', 'status'].includes(c));
    if (st && !statusColors[st]) statusColors[st] = getComputedStyle(el).backgroundColor;
  }
  info.statusColors = statusColors;
  const rowBg = (() => { const d = document.querySelector('.list-table-data .data.title'); return d && getComputedStyle(d).backgroundColor; })();
  for (const [st, c] of Object.entries(statusColors)) {
    if (c === rowBg || /rgba\(0, 0, 0, 0\)|transparent/.test(c)) fail('status-column', `status column for "${st}" lost its color (${c}): use .data:not(.status) for row backgrounds`);
  }

  // ---------- 9. Things only a human/hover can judge ----------
  manual.push('Hover the left floating menu: each tooltip label (Quick Add, Statistics, ...) must be readable.');
  manual.push('Open Filters (advanced options): text, selects and Apply/Clear buttons readable.');
  manual.push('Look at the screenshot: overall harmony, nothing overlapping the logo or the cover image.');
  if (document.documentElement.classList.contains('dark-mode')) info.note = 'MAL site dark mode is ON for this account (html.dark-mode). The list page uses its own list style, but check pages with and without it if the theme targets html.dark-mode.';

  const report = { pass: failures.length === 0, failures, warnings, manual, info };
  console.log('[mal-check]', JSON.stringify(report, null, 2));
  return report;
})();
