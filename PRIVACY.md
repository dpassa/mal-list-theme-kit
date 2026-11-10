# Privacy policy

The `mal-list-theming` plugin and the files in this repository do not collect,
store or send any personal data.

- **No accounts, no telemetry.** The plugin has no server, no analytics and no tracking.
- **No code is shipped.** The plugin is instructions, reference notes and CSS
  themes. When Claude previews a theme, it does so in your own browser tab, on your
  own MyAnimeList page, with your own browser tool; the preview is not saved and
  nothing is sent anywhere.
- **Optional helpers.** The repository's `tools/` folder (not installed with the
  plugin) has a linter that reads a CSS file on your computer and an in-page check
  you can paste into your browser console. Neither sends data anywhere.
- **No credentials.** The skill never asks for your MyAnimeList password or signs in
  for you. You paste and save the CSS yourself in MyAnimeList's settings.
- **Third parties.** The example themes load a font from Google Fonts with `@import`,
  so your browser requests that font from Google when your list is shown. You can
  remove the `@import` line to avoid this. MyAnimeList's own privacy policy applies
  to your list and to the CSS you save there.

Questions: open an issue at https://github.com/dpassa/mal-list-theme-kit/issues
