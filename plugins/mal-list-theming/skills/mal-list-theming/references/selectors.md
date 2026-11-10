# MAL modern list: selector map

Verified on a live modern list (anime) in November 2026. MAL can change its markup:
when a selector here matches nothing on the page, trust the page, and update this file.

## Page structure

```
body.ownlist.anime                       (manga list: body.ownlist.manga)
├─ .header                               site band: logo + "Viewing <user>'s Anime List"
│  ├─ a.header-title                     the LOGO (background-image, text-indent:-9999px)
│  └─ .header-menu > .btn-menu           "Viewing Your Anime List" (.username = "Your" or the name)
├─ .list-menu-float                      fixed left icon menu
│  └─ .icon-menu.<item>                  one per menu item (see the item list below)
│     ├─ svg.icon                        SVG icon: style with `fill`
│     └─ .text                           tooltip label, shown on :hover (width 0 → 94px)
├─ .list-container
│  ├─ .cover-block .image-container      the person's cover image (chosen in MAL settings, not CSS)
│  │  └─ .btn-list-setting               "camera" button on hover (contains i.fa-camera)
│  ├─ .status-menu-container             tabs bar (becomes .fixed when scrolling)
│  │  ├─ .status-menu .status-button(.on)  All Anime / Currently Watching / ...  (:after = underline)
│  │  └─ .search-container #search-button > i.fa-magnifying-glass ; #search-box(.open) > input
│  └─ .list-block .list-unit
│     ├─ .list-status-title              "ALL ANIME" band
│     │  ├─ .text
│     │  └─ .stats  a#show-stats-button > i.fa-chart-column ; a#advanced-options-button > i.fa-filter
│     ├─ .list-stats                     stats panel (toggled by Stats)
│     └─ table.list-table
│        ├─ tr.list-table-header > th.header-title.<column>
│        │     sortable:   a.link.sort (+ i.fa-arrow-down-short-wide / -wide-short on the sorted column)
│        │     plain text: #, Premiered, Tags, Studios, Licensors (no link)
│        ├─ tr.list-table-data > td.data.<column>
│        │     .data.status.<status>     4px color bar (see the status list below)
│        │     .data.number  .data.image .image  .data.title .link  .add-edit-more  .content-status
│        │     .data.score .link (.score-label.score-N)  .data.type  .data.progress  .data.tags .edit
│        └─ tr.more-info .more-content   expandable "More" panel
├─ #advanced-options                     Filters / sort panel (.sort-widget, .filter-widget, .btn-apply, .btn-clear)
└─ #footer-block  #copyright  #recaptcha-terms
```

Floating menu items (class next to `.icon-menu`): profile, quick-add, anime-list,
manga-list, statistics, history, the list download item, the settings item, logout.
Read the exact class of the last three on the live page before styling them one by one.

Status classes (next to `.data.status`): watching, completed, onhold, dropped,
plantowatch, and on manga lists reading and plantoread.

Column classes (next to `th.header-title` and `td.data`): status, number, image,
title, score, type, progress, started, finished, tags, studio, licensor, mal_score,
airing-started and airing-finished. Manga lists add chapters and volumes. Others
(days, priority, rated, retail, storage) appear when the person enables those columns.

## Selectors MAL pins to Verdana/Avenir

A font on `body` does **not** reach these. Each needs its own override, and it is safe:
none of them is an icon element.

```
#advanced-options
#advanced-options .sort-widget .widget-header
#advanced-options .filter-widget .widget-header
#footer-block                                   (Avenir)
.list-menu-float .icon-menu .text               (tooltips)
.cover-block .image-container .btn-list-setting
.status-menu-container .status-menu .status-button   (tabs)
.list-unit .list-status-title .text
.list-table .list-table-data .tags .edit
```

## Icons

- **Font Awesome 6** (`<i class="fa-solid fa-...">`, family "Font Awesome 6 Pro"): search,
  stats, filter, sort arrows, camera, "+" episode buttons. Color them with `color`, never
  change their `font-family`.
- **SVG** (`svg.icon`) in the floating menu: color them with `fill`.

## Places where MAL's base CSS uses `!important`

`body` (background-color, color), `.list-container`, `.status-menu-container`,
`.list-menu-float .icon-menu` (background-color), `.list-table .list-table-data .data a`
and `a:not(.edit-disabled):hover` (color), `.list-unit .list-status-title` (border).
An override without `!important` does nothing there.

## Hardcoded colors that leak into a new theme

| Element | Base color | Why it matters |
|---|---|---|
| `.list-table .list-table-data .tags .edit` | `#A6E7C4` mint | unreadable on light themes |
| `th.header-title` plain-text headers | `#7D6A6A` | unreadable on a dark header band |
| `.add-edit-more`, `.icon-add-episode` | `#dd7d7d` | clashes with any non-pink palette |
| `.data.title .content-status`, `.rewatching` | `#7D6A6A` | low contrast on dark themes |
| `a.edit-disabled` | `#F7EDEB` | invisible on light themes |
| `.list-menu-float .icon-menu:hover` | `#333` | tooltip band on hover |
| `.data.status.*` | mint/blue/yellow/red/grey | keep: it is information |
