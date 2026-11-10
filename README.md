# mal-list-theme-kit

Theme your **MyAnimeList list** with the help of Claude, without breaking it.

MyAnimeList lets you paste your own CSS into your list (*Profile → List Style →
Add Custom CSS*). It's easy to end up with broken icons, an invisible logo,
unreadable headers or rules that do nothing. This kit gives an AI agent everything
it needs to get it right the first time:

- **A Claude skill** (`skill/mal-list-theming/`) with a map of MAL's list markup, the
  known pitfalls and a step-by-step workflow.
- **Four ready-made themes** inspired by Japanese colors and patterns.
- **Automatic checks** that the agent runs on its own before handing you the CSS:
  - a linter for dangerous rules
  - an in-browser check of icons, fonts, contrast, the logo, status colors and search

## Themes

| Theme | Look | Font |
|---|---|---|
| [`cherry-blossom.css`](skill/mal-list-theming/themes/cherry-blossom.css) | Sakura: soft pink rows, magenta and marsala bands | Nunito |
| [`matcha.css`](skill/mal-list-theming/themes/matcha.css) | Green tea on washi paper, deep tea-green bands | Zen Maru Gothic |
| [`momiji.css`](skill/mal-list-theming/themes/momiji.css) | Autumn maple: warm paper, vermilion torii bands, gold accents | M PLUS Rounded 1c |
| [`aizome.css`](skill/mal-list-theming/themes/aizome.css) | Indigo dyeing, **dark**, seigaiha wave pattern | Zen Kaku Gothic New |

To use one as is:
1. Open the file and copy all of it.
2. On MyAnimeList go to *Profile → List Style* (modern list) → *Add Custom CSS*.
3. Paste the CSS and press *Submit*.

To change the colors, edit only the `:root { --mal-... }` block at the top.

## Use the skill

**Claude Code:** copy `skill/mal-list-theming` into `~/.claude/skills/`, or into
`.claude/skills/` inside a project. Then ask, for example:

> Make me a MyAnimeList list theme in dark purple with a Japanese night-sky feel.

**Claude apps:** zip the `mal-list-theming` folder and add it as a skill in your
settings, where skills are available.

The agent starts from the closest theme and changes the palette and font. It runs the
linter and, if it has a browser tool and your list URL, previews the theme on your list
**in its own tab only**. It never saves anything to your account: pasting the CSS is up to you.

## The checks

```bash
python skill/mal-list-theming/scripts/lint_css.py my-theme.css --strict
```

The linter needs Python 3 and nothing else. It catches, among other things:
- fonts forced on `*` or on icons, which turns icons into empty squares
- selectors from the old classic list
- a `background` that deletes the MAL logo
- gradients that look patchy on column headers
- row colors that hide the status bar
- missing `!important`
- a misplaced `@import`

`skill/mal-list-theming/scripts/browser_check.js` runs on your list page. An agent's
browser tool can run it, or you can paste it into the DevTools console. See
[verification.md](skill/mal-list-theming/references/verification.md) for what it
checks and what still needs human eyes.

## Tests

```bash
python tests/run_tests.py
```

The tests check that every bundled theme lints clean and that `tests/fixtures/bad.css`
triggers every rule it is meant to.

## Notes

- This works with the **modern** MyAnimeList list only, not the classic list.
- This project is not affiliated with MyAnimeList. Themes only override MAL's styles:
  no MAL stylesheet is redistributed here.
- Fonts come from Google Fonts under their own open licenses.

## License

[MIT](LICENSE)
