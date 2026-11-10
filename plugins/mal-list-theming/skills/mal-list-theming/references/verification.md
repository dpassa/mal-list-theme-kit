# Verification

Two layers. Do both before delivering a theme. This skill ships no code: you
check the CSS by reading it, and the page with your own browser tool.

## 1. Review checklist (always possible)

Read the whole file once per group below. Every line must pass. Details and the
right code are in `pitfalls.md` under the same id.

**Fonts and icons**
- [ ] MAL-001: no `font-family` on `*` or on selectors that reach every element.
- [ ] MAL-002: no `font-family` on `i`, `.fa*`, `[class*=fa]` or on icon `::before`/`::after`.
- [ ] MAL-010: the font is on `body` **and** on every Verdana-pinned selector listed in `selectors.md`.

**Selectors**
- [ ] MAL-003: no classic-list selectors (`table.list-table thead`, `tr.table-header`, `td.header_title`, `.borderClass`, `.td1`).
- [ ] MAL-004: `.header-title` is always scoped (`.header .header-title` or `.list-table-header .header-title`).
- [ ] MAL-011: every class and id appears in `selectors.md` or was confirmed on the live page.

**Backgrounds**
- [ ] MAL-005: no `background`/`background-image` on the logo (`.header .header-title`).
- [ ] MAL-006: no gradient on column-header cells.
- [ ] MAL-014: column headers use `background-color`, not the `background` shorthand.
- [ ] MAL-008: row backgrounds target `.data:not(.status)`.

**Cascade and file**
- [ ] MAL-007: `@import` is the very first rule.
- [ ] MAL-012: imports use `https://`.
- [ ] MAL-009: every override of a property the base sets with `!important` (see `selectors.md`) also has `!important`.
- [ ] MAL-013: scrollbar styling has both `scrollbar-color` and `::-webkit-scrollbar`.
- [ ] MAL-016: the file is ASCII only; `content` strings use CSS escapes, with two spaces after an escape when a space must stay.
- [ ] MAL-015: the visible footer credit and the final credit comment are present.

**Contrast** (WCAG, at least 4.5:1)
- [ ] `--mal-on-band` on `--mal-band-1` and `--mal-band-2`, at every gradient stop.
- [ ] `--mal-text`, `--mal-link`, `--mal-muted`, `--mal-accent` on `--mal-surface`, `--mal-surface-alt`, `--mal-hover`.
- [ ] The footer credit color on the footer background.

Compute ratios with the WCAG formula (relative luminance of each sRGB color,
then `(L1 + 0.05) / (L2 + 0.05)`); do not guess them by eye.

## 2. In-page check (needs the list page and a browser tool)

1. Open `https://myanimelist.net/animelist/<user>`. The list must be public, or the
   person is signed in to their own browser. Never sign in for them.
2. **Preview, reversibly.** MAL puts the saved custom CSS in an inline `<style>`
   placed before the site stylesheet (`link[href*="/static/assets/css/pc/style-"]`);
   the first inline style there is MAL's own base. Disable the saved custom style
   (for example `media="not all"`) and insert the candidate as a new `<style>` at
   the same position, so it has the same cascade order as when saved. Remember
   what you changed so you can undo it at the end.
3. Walk through the checks and fix the CSS for each failure, then preview again:

| Check | What to look at |
|---|---|
| Icons render | every visible `i[class*=fa-]` still uses the Font Awesome family and its `::before` has a glyph (not an empty square) |
| Search works | click the lens: `#search-box` gets the `open` class and its full width (measure with transitions off); close it |
| Font everywhere | no visible text left in Verdana, Avenir, Arial or Tahoma; the expected font is loaded (`document.fonts`) |
| Contrast | computed color and background of header, tabs (also inactive), section title, both header kinds, titles, cells, tag links and footer; for gradients check every stop |
| Logo | `.header .header-title` still has its background image |
| Status column | each `.data.status.*` keeps its own status color |
| Tooltips | hover one icon of `.list-menu-float` and read the computed style of its `.text`: readable color, opacity 1, the theme font |

4. Take a screenshot and judge it: harmony, nothing overlapping the logo or cover.
5. Remove the preview and re-enable the saved style. Nothing is sent to MAL,
   nothing is saved.

Tips:
- Screenshots may time out while the tab is in the background: rely on computed styles.
- Some tools pass long strings badly: strip comments from the CSS before inserting it.

### Without a browser tool
Ask the person to paste the CSS on MAL's Customize page and press **Preview**
(not Save), then send a screenshot of the list, with a tooltip open and the search
box open. Tell them what to look for: square icons, unreadable text, a missing logo,
rows that lost their status color.

## What cannot be fully automated

- **Taste.** Whether the palette is pretty is the person's call: show screenshots.
- **The sort arrow** only exists on the sorted column. Sorting changes the page URL.
  Ask the person to click a column header, or check it on a page already sorted.
- **Saving.** Pasting into *Add Custom CSS* and pressing Save is always done by the person.
- **The Filters panel and the "More" panel** are opened by MAL's own page code. Open them by clicking, then look.
- **Future MAL changes.** New markup makes rules go dead silently. Check again
  after MAL updates, and treat MAL-011 lines as hints.
- **Other browsers.** The check runs in the browser you use. Firefox ignores `::-webkit-scrollbar`.
- **Classic lists** (the older table layout) are a different page: this skill does not support them.
