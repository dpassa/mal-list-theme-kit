# mal-list-theme-kit

Theme your **MyAnimeList list** with the help of Claude, without breaking it.

MyAnimeList lets you add your own CSS to your list. It's easy to end up with broken
icons, an invisible logo, unreadable headers or rules that do nothing. This kit
gives Claude everything it needs to get it right the first time:

- **A Claude skill** (`mal-list-theming`) with a map of MAL's list markup, the
  known pitfalls and a step-by-step workflow. It is packaged as a Claude Code plugin.
- **Four ready-made themes** inspired by Japanese colors and patterns.
- **Automatic checks** that Claude runs on its own before handing you the CSS:
  - a linter for dangerous rules
  - an in-browser check of icons, fonts, contrast, the logo, status colors and search

## Themes

| Theme | Look | Font |
|---|---|---|
| [Sakura](themes/sakura.css) | Cherry blossom: soft pink rows, magenta and marsala bands | Nunito |
| [Matcha](themes/matcha.css) | Green tea on washi paper, deep tea-green bands | Zen Maru Gothic |
| [Momiji](themes/momiji.css) | Autumn maple: warm paper, vermilion torii bands, gold accents | M PLUS Rounded 1c |
| [Aizome](themes/aizome.css) | Indigo dyeing, **dark**, seigaiha wave pattern | Zen Kaku Gothic New |

---

## Getting started

Pick the path that fits you. You only need **one**.

### A. Just use a theme (no Claude needed)

1. Open one of the theme files above, click **Raw**, select all and copy.
2. Open your CSS settings on MyAnimeList, signed in (see [Apply a CSS to your list](#apply-a-css-to-your-list)).
3. Paste, press **Preview** to look at it, then **Save**.

To change the colors, edit only the `:root { --mal-... }` block at the top of the file.

### B. Claude Code (recommended: Claude does the work and the checks)

You need [Claude Code](https://code.claude.com) installed.

1. In a terminal, add this repository as a plugin marketplace and install the plugin:
   ```bash
   claude plugin marketplace add dpassa/mal-list-theme-kit
   ```
   ```bash
   claude plugin install mal-list-theming@mal-list-theme-kit
   ```
   You can also run the same steps inside a Claude Code session with
   `/plugin marketplace add dpassa/mal-list-theme-kit`, then `/plugin install mal-list-theming@mal-list-theme-kit`.
2. Start Claude Code (`claude`) and ask, for example:
   > Make me a MyAnimeList list theme in dark purple with a Japanese night-sky feel. My list is https://myanimelist.net/animelist/YOUR_NAME
3. Claude will:
   - ask about colors, font and light or dark
   - start from the closest theme
   - review it against the known pitfalls
   - preview it on your list if it has a browser tool

   It then gives you the CSS file.
4. Apply it as described in [Apply a CSS to your list](#apply-a-css-to-your-list).

Update later with `claude plugin update mal-list-theming@mal-list-theme-kit`.

**Live preview on your list:** Claude needs a browser tool, for example the
Claude in Chrome extension. The preview happens in one tab
only and is never saved to your account. Without a browser tool Claude still reviews the CSS
and tells you what to look at when you press Preview on MAL.

### C. Claude apps (claude.ai, desktop)

1. Download this repository: green **Code** button → **Download ZIP**, then extract it.
2. Go into `plugins/mal-list-theming/skills/` and zip the `mal-list-theming` folder
   itself, so the ZIP contains `mal-list-theming/SKILL.md`.
3. In Claude open **Customize → Skills** ([claude.ai/customize/skills](https://claude.ai/customize/skills))
   and upload the ZIP. Code execution must be enabled in your settings.
4. In a new chat ask for a theme, as in B. The app cannot open your list in a browser, so the
   in-page check is up to you. See [Run the checks yourself](#run-the-checks-yourself).

---

## Apply a CSS to your list

You must be signed in to MyAnimeList.

1. Open **List Style Design**: [myanimelist.net/ownlist/style](https://myanimelist.net/ownlist/style).
   From your list you can also use the gear icon in the left floating menu → **Style Settings**.
2. Make sure **Modern** is selected under *Switch Template*. These themes do not work on the Classic list.
3. Click the theme you use as a base, for example **Default Theme**.
4. On the *Customize* page, paste the CSS into **Add Custom CSS**.
5. Press **Preview** to check it, then **Save**.

To undo, empty the **Add Custom CSS** field and press **Save**, or use **Reset to Default**.

## Run the checks yourself

The plugin itself ships no scripts. If you download this repository, the
[`tools/`](tools) folder has two optional helpers you can run by hand.

**Lint** (needs Python 3):
```bash
python tools/lint_css.py my-theme.css --strict
```
It catches, among other things:
- fonts forced on `*` or on icons, which turns icons into empty squares
- selectors from the classic list
- a `background` that deletes the MAL logo
- gradients that look patchy on column headers
- row colors that hide the status bar
- missing `!important`
- a misplaced `@import`

**In-page check:**
1. Open your list and press F12 → **Console**.
2. Paste `window.MAL_CHECK = { css: \`...your CSS...\`, expectFont: 'Nunito' }`.
3. Paste the content of [`browser_check.js`](tools/browser_check.js).

It previews the CSS in that tab only and returns a pass/fail report. See
[verification.md](plugins/mal-list-theming/skills/mal-list-theming/references/verification.md)
for details and for what still needs human eyes.

## Troubleshooting

| Problem | Fix |
|---|---|
| Nothing changes | You are on the **Classic** template, or you saved the CSS on a theme you are not using. Check *Switch Template → Modern* and paste into the theme your list uses. |
| Icons became squares | A rule changes the font of icons, usually `* { font-family: ... }`. Run the linter (MAL-001). |
| The font doesn't change everywhere | The tabs, section titles and tooltips need their own font rule. See [selectors.md](plugins/mal-list-theming/skills/mal-list-theming/references/selectors.md). |
| The logo disappeared | A `background` was set on the logo. Color `.header` instead (MAL-005). |

## Repository layout

```
.claude-plugin/marketplace.json          this repo is a Claude Code plugin marketplace
plugins/mal-list-theming/
├─ .claude-plugin/plugin.json
└─ skills/mal-list-theming/
   ├─ SKILL.md                            workflow and hard rules for Claude
   ├─ references/                         selector map, pitfalls, verification guide
   └─ themes/                             the four themes as Markdown (generated, do not edit)
themes/                                   the four themes as .css files (source of truth)
tools/                                    optional helpers, not part of the plugin: lint_css.py, browser_check.js,
                                          build_plugin_themes.py (copies themes/*.css into the plugin as Markdown)
tests/                                    linter self-tests: python tests/run_tests.py
```

## Notes

- This project is not affiliated with MyAnimeList. Themes only override MAL's styles:
  no MAL stylesheet is redistributed here.
- Fonts come from Google Fonts under their own open licenses.
- Every theme ends with a small credit line in the page footer. You're free to remove it.

## License

[MIT](LICENSE)
