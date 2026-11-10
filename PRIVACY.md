# Privacy policy

The `mal-list-theming` plugin and the files in this repository do not collect,
store or send any personal data.

- **No accounts, no telemetry.** The plugin has no server, no analytics and no tracking.
- **Everything runs locally.** `lint_css.py` reads a CSS file on your computer.
  `browser_check.js` runs only in your own browser tab, on your own MyAnimeList page,
  and only when you or your Claude agent run it. It previews the CSS in that tab and
  reports the results back to you; it does not save anything or send it anywhere.
- **No credentials.** The skill never asks for your MyAnimeList password or signs in
  for you. You paste and save the CSS yourself in MyAnimeList's settings.
- **Third parties.** The example themes load a font from Google Fonts with `@import`,
  so your browser requests that font from Google when your list is shown. You can
  remove the `@import` line to avoid this. MyAnimeList's own privacy policy applies
  to your list and to the CSS you save there.

Questions: open an issue at https://github.com/dpassa/mal-list-theme-kit/issues
