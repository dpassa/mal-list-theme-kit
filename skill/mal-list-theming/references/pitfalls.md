# Known pitfalls

Each entry has the linter rule id (`scripts/lint_css.py`) when it can be detected
statically, what you see on the page, and the fix. All of them happened on a real list.

## MAL-001: font on the universal selector breaks the icons
**Symptom:** the search lens, the stats chart, the filter funnel and the sort arrows become empty squares ("tofu").
**Cause:** those icons are Font Awesome glyphs. `* { font-family: X !important }`
beats Font Awesome's own class rule, so the glyph is looked up in X, which lacks it.
```css
/* wrong */
* { font-family: 'Nunito', sans-serif !important; }

/* right: body + the selectors MAL pins to Verdana (see selectors.md) */
body,
.status-menu-container .status-menu .status-button,
.list-unit .list-status-title .text /* , ... */ {
    font-family: 'Nunito', sans-serif !important;
}
```

## MAL-002: font on an icon selector
Same symptom, narrower cause: `font-family` on `i`, `.fa-*`, `[class*="fa"]`,
`::before`/`::after` of icons, or `.sort-icon`. Change their `color`, never their font.

## MAL-003: selectors from the classic list
**Symptom:** "my CSS does nothing" for that part of the page.
`table.list-table thead th`, `tr.table-header`, `td.header_title`, `.anime-menu`,
`.borderClass`, `.td1/.td2`, `.header_cw` come from the old/classic list or old
userstyles. The modern list uses `.list-table-header .header-title`,
`.list-table-data .data`, `.status-menu .status-button`...

## MAL-004: unscoped `.header-title`
`.header-title` is the **logo** (`.header .header-title`) *and* every **column-header
cell** (`.list-table .list-table-header .header-title`). An unscoped rule hits both.

## MAL-005: background on the logo deletes it
The logo is a `background-image` on `.header .header-title`. Any `background:` or
`background-image:` there replaces it. Color the band with `.header { background: ... }`.

## MAL-006: gradient on column headers looks patchy
**Symptom:** the column-header row looks like a quilt: narrow columns (`#`, Score) show a hard color jump, wide ones a soft fade.
**Cause:** the gradient is drawn per cell, not per row.
**Fix:** a solid `background-color`.
To blend with the section band above, give that band a **vertical** gradient that
ends on the same color as the headers.

## MAL-007: `@import` not first
The browser ignores an `@import` that follows any rule: the font silently falls back.

## MAL-008: row backgrounds hide the status colors
`.list-table-data .data { background: ... }` also paints `.data.status`, the thin bar
that says watching (green), completed (blue), on hold (yellow), dropped (red).
Use `.data:not(.status)`.

## MAL-009: missing `!important`
MAL inlines the custom CSS **before** its site stylesheet, and the base list CSS uses
`!important` on body, containers, links (see selectors.md). Without `!important`
the override loses. Use `!important` on every override; it is the norm for MAL themes.

## MAL-010: font only on body
**Symptom:** most text is in the new font, but the tabs, the section title, the tooltips and the footer are still in Verdana.
**Fix:** add every selector of the "pinned" list in selectors.md to the font rule.

## MAL-011: unknown selector (info)
A class that is not in the documented markup. It may be new MAL markup (fine) or a
typo or a selector copied from another site (dead rule). Confirm it on the live page.

## MAL-012: http:// imports
MAL is served over https: an `http://` font or image is blocked as mixed content.

## MAL-013: scrollbar only for Chromium
`::-webkit-scrollbar` does nothing in Firefox: add `html { scrollbar-color: thumb track; }`.

## MAL-014: `background` shorthand on column headers (info)
It also removes MAL's 1px column separator image. Fine if intended.

## Not detectable by the linter (the browser check covers them)

- **White header on a light page.** The logo and "Viewing … List" are white with no
  background. Once the page is light they disappear. Give `.header` a dark band.
- **Logo against the edge.** With a colored band, the "M" touches the left edge: add
  `.header .header-title { left: 16px !important }` and `.header .header-menu { right: 16px !important }`.
- **Plain-text column headers.** `#`, Premiered, Tags, Studios and Licensors are text inside `th.header-title`, not
  `.link`. Coloring only `.link` leaves them in the base `#7D6A6A`.
- **Leaking base colors.** Examples: the mint "Edit" tag link and the pink "Add/Edit/More". See the table in selectors.md.
- **Dark themes.** Override inputs, `.more-info`, `.tags textarea`, `a.edit-disabled` and
  `.content-status`. The base assumes a light page.
- **The account's dark mode.** The site can be in dark mode (`html.dark-mode`) while the list keeps its own style.
  Don't rely on `html.dark-mode` unless the person wants the theme to follow it.
- **Hover-only states** (tooltips, row hover, sort hover) need a real hover to check.
