# Verification

Two layers. Run both before delivering a theme.

## 1. Static lint (always possible)

```bash
python scripts/lint_css.py my-theme.css --strict
python scripts/lint_css.py my-theme.css --json      # machine-readable
```

Exit code 1 means there are errors (with `--strict`, warnings too). It catches every
rule in pitfalls.md that has an id. It cannot see colors on the page, hover states
or MAL markup changes.

## 2. In-page check (needs the list page)

`scripts/browser_check.js` runs inside the list page. It **previews** the candidate
CSS in that tab only: it disables the saved custom CSS, inserts the candidate at the
same position in the cascade, and keeps everything reversible with
`window.__malCheckRestore()`. Nothing is sent to MAL, nothing is saved.

What it checks automatically:

| Check | How |
|---|---|
| Icons render | every visible `i[class*=fa-]` uses Font Awesome and has a non-empty `::before` glyph |
| Search works | clicks the lens, verifies `#search-box.open` reaches its open width, closes it |
| Font applied everywhere | no visible text left in Verdana/Avenir/Arial/Tahoma; the expected font is loaded |
| Contrast | WCAG ratio for header, tabs, section title, both header kinds, titles, cells, tag link and footer; gradients are checked at every stop |
| Logo | `.header .header-title` still has the logo background image |
| Status column | each `.data.status.*` keeps its own color |

### Agent with a browser tool
1. Open `https://myanimelist.net/animelist/<user>`. The list must be public, or the
   person is signed in to their own browser. Never sign in for them.
2. Execute JavaScript:
   `window.MAL_CHECK = { css: <theme file text>, expectFont: 'Nunito' }`. Then run
   the content of `browser_check.js`. It returns the JSON report.
3. Fix every entry in `failures`, then run it again.
4. **Tooltips:** hover one icon of `.list-menu-float` with the mouse tool. Then read
   `getComputedStyle(document.querySelector('.list-menu-float .icon-menu:hover .text'))`.
   Check color, opacity 1 and the font, plus the background of the hovered `.icon-menu`.
5. Take a screenshot and judge it: harmony, nothing overlapping the logo or cover.
6. `window.__malCheckRestore()`.

Tips:
- Run the check again after each change: it resets the previous preview itself.
- Some tools pass long strings badly: strip comments from the CSS first.
- Screenshots may time out while the tab is in the background: rely on the JSON report.

### Person without an agent browser
1. Open your list, press F12 → Console.
2. Paste `window.MAL_CHECK = { css: \`...theme...\`, expectFont: 'Nunito' }`.
   The backticks matter. Remove any backtick from the CSS comments first.
3. Paste the content of `browser_check.js`, press Enter, copy the JSON back to the agent.

## What cannot be fully automated

- **Taste.** Whether the palette is pretty is the person's call: show screenshots.
- **The sort arrow** only exists on the sorted column. Sorting changes the page URL.
  Ask the person to click a column header, or check it on a page already sorted.
- **Saving.** Pasting into *Add Custom CSS* and pressing Submit is always done by the person.
- **The Filters panel and the "More" panel** are opened by MAL scripts. Open them by clicking, then look.
- **Future MAL changes.** New markup makes rules go dead silently. Re-run the check
  after MAL updates, and treat linter MAL-011 infos as hints.
- **Other browsers.** The check runs in the browser you use. Firefox ignores `::-webkit-scrollbar`.
- **Classic lists** (the older table layout) are a different page: these tools do not support them.
