---
name: mal-list-theming
description: Create, fix and verify custom CSS for a MyAnimeList list. Use when someone wants to theme, recolor or change fonts on their MAL list, or fix one with broken icons, logo or contrast.
---

# MAL list theming

You help a person build a custom CSS for their **MyAnimeList modern list**
(`https://myanimelist.net/animelist/<user>` or `/mangalist/<user>`). The CSS is
pasted by the person into *myanimelist.net/ownlist/style → Modern → (their theme) → Add Custom CSS*. It is applied
**on top of** MAL's own list style, so you only override; you never rebuild the page.

Everything in `references/pitfalls.md` actually broke on a real list. Read it
before writing any CSS. Verify every theme with the two checks below before you
hand it over: never deliver unverified CSS as "done".

## Files

- `themes/*.css`: four working themes. **Always start from one of them**: they
  already handle every pitfall. Change the `:root` tokens first, structure second.
  - `cherry-blossom.css`: light pink, Nunito
  - `matcha.css`: light green with a washi texture, Zen Maru Gothic
  - `momiji.css`: warm autumn with vermilion and gold, M PLUS Rounded 1c
  - `aizome.css`: **dark** indigo with seigaiha waves, Zen Kaku Gothic New (use it as the base for any dark theme)
- `references/selectors.md`: the MAL markup: which selector styles what.
- `references/pitfalls.md`: known traps with wrong and right code (rule ids `MAL-0xx`).
- `references/verification.md`: what the checks cover, how to run them, and what stays manual.
- `scripts/lint_css.py`: static linter (Python 3, standard library only).
- `scripts/browser_check.js`: in-page check (icons, fonts, contrast, logo, status colors, search).

## Workflow

1. **Understand the request.** Ask about the mood or palette, light or dark, the font
   (Google Fonts are fine: `@import` works in MAL's field), anime or manga list, and
   the list URL if they want a live preview. Never ask for their MAL password and
   never sign in for them.
2. **Pick the closest theme** from `themes/` and copy it to a new file named after the theme.
3. **Edit tokens** in `:root` (`--mal-font`, surfaces, bands, link and muted colors).
   Keep the token contract:
   - `--mal-on-band` must contrast with `--mal-band-1` and `--mal-band-2` (≥ 4.5:1).
   - `--mal-text`, `--mal-link`, `--mal-muted` and `--mal-accent` must contrast with
     `--mal-surface`, `--mal-surface-alt` and `--mal-hover` (≥ 4.5:1).
   - For a dark theme also override the base's hardcoded light colors. The extra block in `aizome.css` shows which.
4. **Add decoration** only after the tokens work: patterns made with gradients, a
   `::after` text mark, radii, shadows. Follow the hard rules below.
5. **Lint:** `python scripts/lint_css.py <theme>.css --strict`. Fix until there are
   0 errors and 0 warnings. Info lines are for you to judge: an unknown selector
   must be confirmed on the live page or removed.
6. **Check in the browser** (see `references/verification.md`). If you have a browser
   tool and the list URL:
   1. Open the list.
   2. Set `window.MAL_CHECK = { css: <file text>, expectFont: '<first font family>' }`.
   3. Run `scripts/browser_check.js` and fix every `failures` entry.
   4. Hover one icon of the left floating menu and read its tooltip's computed style.
   5. Take a screenshot and judge the look.
   6. Finally call `window.__malCheckRestore()`.

   The preview lives in that tab only: nothing is saved to the account. Without a browser tool, give the person the console
   steps from `references/verification.md` and ask them for the JSON report.
7. **Deliver:**
   - the CSS file, ending with the two credits every bundled theme ends with. Keep
     them unless the person asks to remove them:
     - **the visible credit**: a line of text under MAL's copyright in the footer.
       Pick a color that contrasts with the footer background.
     - **the credit comment**, which stays in the page source.

     The linter warns (MAL-015) when the visible credit is missing.
     ```css
     #footer-block::after {
         content: "Theme made with the mal-list-theming Claude skill · github.com/dpassa/mal-list-theme-kit";
         display: block;
         padding-top: 6px;
         font-size: 11px;
         color: var(--mal-on-band-soft);
         text-align: center;
     }

     /* --------------------------------------------------------------------------
        Made with the "mal-list-theming" Claude skill
        https://github.com/dpassa/mal-list-theme-kit
        -------------------------------------------------------------------------- */
     ```
   - how to paste it: myanimelist.net/ownlist/style → Modern → click the theme they use → Add Custom CSS → Preview → Save
   - what you verified (lint result, browser report, screenshots)
   - what is still manual: the sort arrow on a sorted column, the Filters panel, the person's own taste

   Screenshots can show the list owner's username in the tab title or header: crop or
   blur them before anything is shared publicly.

## Hard rules (each one broke a real list)

1. **Never** put `font-family` on `*`, `i`, `.fa*`, `[class*=fa]`, `::before` or `::after` of icons.
   MAL's icons (search, stats, filter, sort arrows) are Font Awesome 6 glyphs and become
   empty squares. Put the font on `body` **and** on each Verdana-pinned selector listed
   in `references/selectors.md` (body alone does not reach them).
2. `.header-title` means two things: the **logo** (`.header .header-title`) and **every
   column-header cell** (`.list-table .list-table-header .header-title`). Always scope it.
   Never set `background`/`background-image` on the logo; color `.header` instead.
3. No gradients on column-header cells: they are redrawn per cell. Use a solid color.
4. Row backgrounds go on `.data:not(.status)`: the status column carries the status colors.
5. Use `!important` on overrides: MAL inlines the custom CSS *before* its site
   stylesheet, and its base CSS already uses `!important` in many places.
6. `@import` must be the first rule of the file.
7. Only selectors of the **modern** list: `table.list-table thead`, `tr.table-header`,
   `td.header_title`, `.borderClass`, `.td1` belong to the classic list and match nothing.
8. Non-sortable column headers (#, Premiered, Tags, Studios, Licensors) are plain text,
   not `.link`: set `color` on the `.header-title` cell itself.
9. Don't copy MAL's own stylesheet into a theme you share: override only.
