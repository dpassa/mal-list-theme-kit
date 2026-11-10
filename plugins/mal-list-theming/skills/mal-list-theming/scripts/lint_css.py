#!/usr/bin/env python3
"""Lint a MyAnimeList (modern list) custom CSS file for known pitfalls.

Usage:
    python lint_css.py theme.css [more.css ...] [--json] [--strict]

Exit code: 0 = no errors, 1 = at least one error (or warning with --strict),
2 = usage / file problem. Standard library only, no dependencies.

Every rule here comes from a real breakage on a MAL list. See
references/pitfalls.md for the explanation and the fix of each rule id.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, asdict, field

# ---------------------------------------------------------------------------
# Knowledge about MAL's modern list markup
# ---------------------------------------------------------------------------

# Selectors the base list CSS pins to Verdana/Avenir. Setting a font on `body`
# alone does NOT reach these: each one needs its own override.
FONT_PINNED_SELECTORS = [
    "#advanced-options",
    "#advanced-options .sort-widget .widget-header",
    "#advanced-options .filter-widget .widget-header",
    "#footer-block",
    ".list-menu-float .icon-menu .text",
    ".cover-block .image-container .btn-list-setting",
    ".status-menu-container .status-menu .status-button",
    ".list-unit .list-status-title .text",
    ".list-table .list-table-data .tags .edit",
]

# Markup of the old "classic" list (or of old userstyles). On a modern list
# these selectors match nothing, so the rule silently does nothing.
LEGACY_PATTERNS = [
    (r"table\.list-table\s+thead", "table.list-table thead"),
    (r"tr\.table-header", "tr.table-header"),
    (r"td\.header_title", "td.header_title"),
    (r"\.anime-menu\b", ".anime-menu"),
    (r"\.table_header\b", ".table_header"),
    (r"\.borderClass\b", ".borderClass"),
    (r"\.td[12]\b", ".td1/.td2"),
    (r"\.header_(cw|completed|onhold|dropped|ptw)\b", ".header_cw/..."),
    (r"\.category_totals\b", ".category_totals"),
    (r"#list_surround\b", "#list_surround"),
]

# Selectors that target icon glyphs (Font Awesome 6 <i class="fa-solid fa-...">).
ICON_SELECTOR = re.compile(
    r"(::?before|::?after|(^|[\s>+~])i(?=$|[\s.#:\[>+~])|\.fa\b|\.fa-|\[class[*^|~]?=\s*[\"']?fa"
    r"|\.sort-icon\b|\[class[*^|~]?=\s*[\"']?icon)"
)

# Classes/ids known to exist on the modern list. Anything else is reported as
# info: it may be fine (MAL adds markup over time) but often it is a typo or a
# selector copied from another site.
KNOWN_TOKENS = set("""
ownlist anime manga header header-title header-menu header-info btn-menu list-menu username
cover-block image-container btn-list-setting hide fa-camera icon-plus-circle
list-container list-block list-unit list-status-title text stats list-stats loading-space
status-menu-container status-menu status-button on fixed search-container search-button search-box open
all_anime all_manga watching reading completed onhold dropped plantowatch plantoread
list-table list-table-header list-table-data data more-info more-content more
status number image title score type progress started finished tags studio licensor mal_score
chapters volumes days priority rated retail storage season premiered aired
link sort sort-icon hover_info edit edit-disabled icon-watch icon-watch-pv icon-add-episode
list-menu-float icon-menu icon profile quick-add anime-list manga-list statistics history export
login logout setting icon-quick-add icon-anime-list icon-manga-list icon-statistics icon-history
icon-export icon-login icon-logout icon-setting link-list-setting link-style-setting
advanced-options advanced-options-header advanced-options-button description sort-widget
filter-widget widget-header btn-apply btn-clear aired-season magazine published-date
publishing-status year day
footer-block copyright recaptcha-terms grecaptcha-badge
dark-mode appearance-none
fa fa-solid fa-magnifying-glass fa-chart-column fa-filter fa-arrow-down-short-wide
fa-arrow-down-wide-short fa-circle-plus fa-angle-right
add-edit-more content-status rewatching rereading
""".split())

PROPS_FONT = ("font-family", "font")
PROPS_BG = ("background", "background-color", "background-image")

# Places where the base CSS already uses !important. Without !important the
# custom rule loses and nothing changes on screen.
BASE_IMPORTANT = [
    (re.compile(r"^body$"), ("background", "background-color", "color")),
    (re.compile(r"\.list-table-data\s+(\.data\s+)?a\b"), ("color",)),
    (re.compile(r"\.list-menu-float(\s+\.icon-menu)?$"), ("background", "background-color")),
    (re.compile(r"\.list-unit\s+\.list-status-title$"), ("border", "border-color")),
    (re.compile(r"(^|\s)\.(list-container|status-menu-container)$"), ("background", "background-color")),
]


@dataclass
class Finding:
    file: str
    line: int
    rule: str
    severity: str  # error | warning | info
    message: str
    selector: str = ""


@dataclass
class Rule:
    selectors: list[str]
    decls: list[tuple[str, str, bool]]  # (prop, value, important)
    line: int
    at_context: str = ""


# ---------------------------------------------------------------------------
# Minimal CSS parser (good enough for userstyles: rules, @media, @import)
# ---------------------------------------------------------------------------

def strip_comments(css: str) -> str:
    # keep newlines so line numbers stay right
    return re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), css, flags=re.S)


def parse(css: str):
    css = strip_comments(css)
    rules: list[Rule] = []
    imports: list[tuple[int, str]] = []
    first_rule_line: int | None = None
    i, n = 0, len(css)
    stack: list[str] = []
    buf_start = 0

    def line_of(pos: int) -> int:
        return css.count("\n", 0, pos) + 1

    while i < n:
        c = css[i]
        if c in "\"'":
            j = css.find(c, i + 1)
            i = n if j == -1 else j + 1
            continue
        if c == ";" and not stack or (c == ";" and stack and stack[-1].startswith("@")):
            stmt = css[buf_start:i].strip()
            if stmt.startswith("@import"):
                imports.append((line_of(buf_start + css[buf_start:i].find("@")), stmt))
            elif stmt.startswith("@") and first_rule_line is None and not stmt.startswith("@charset"):
                pass
            buf_start = i + 1
        elif c == "{":
            prelude = css[buf_start:i].strip()
            if prelude.startswith("@"):
                if first_rule_line is None and not prelude.startswith(("@charset",)):
                    first_rule_line = line_of(buf_start + css[buf_start:i].find("@"))
                stack.append(prelude)
                buf_start = i + 1
            else:
                end = css.find("}", i)
                if end == -1:
                    end = n
                body = css[i + 1:end]
                ln = line_of(buf_start + len(css[buf_start:i]) - len(css[buf_start:i].lstrip()))
                if first_rule_line is None:
                    first_rule_line = ln
                sels = [s.strip() for s in split_top(prelude) if s.strip()]
                decls = []
                for d in body.split(";"):
                    if ":" not in d:
                        continue
                    p, v = d.split(":", 1)
                    imp = bool(re.search(r"!\s*important", v, re.I))
                    v = re.sub(r"!\s*important", "", v, flags=re.I).strip()
                    decls.append((p.strip().lower(), v, imp))
                rules.append(Rule(sels, decls, ln, " ".join(stack)))
                i = end + 1
                buf_start = i
                continue
        elif c == "}":
            if stack:
                stack.pop()
            buf_start = i + 1
        i += 1
    return rules, imports, first_rule_line


def split_top(sel: str) -> list[str]:
    out, depth, cur = [], 0, ""
    for ch in sel:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return out


def norm(sel: str) -> str:
    return re.sub(r"\s+", " ", sel.strip())


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def is_universal(sel: str) -> bool:
    # `*`, `body *`, `*::before`, `div > *` ... but not attribute operators like [class*=x]
    s = re.sub(r"\[[^\]]*\]", "", sel)
    return bool(re.search(r"(^|[\s>+~])\*", s))


def lint(path: str, css: str) -> list[Finding]:
    rules, imports, first_rule_line = parse(css)
    f: list[Finding] = []
    add = lambda line, rule, sev, msg, sel="": f.append(Finding(path, line, rule, sev, msg, sel))

    # MAL-001 / MAL-002: fonts on universal or icon selectors
    for r in rules:
        font_decls = [d for d in r.decls if d[0] in PROPS_FONT]
        if not font_decls:
            continue
        for s in r.selectors:
            if is_universal(s):
                sev = "error" if any(d[2] for d in font_decls) else "warning"
                add(r.line, "MAL-001", sev,
                    "font set on a universal selector: it also replaces the Font Awesome icon font "
                    "(search lens, stats, filter, sort arrows become empty squares). Set the font on "
                    "body + the font-pinned selectors instead.", s)
            elif ICON_SELECTOR.search(s):
                add(r.line, "MAL-002", "error",
                    "font set on an icon selector (<i>, .fa-*, ::before/::after, .sort-icon): the "
                    "glyph will render as an empty square.", s)

    # MAL-003: legacy markup
    for r in rules:
        for s in r.selectors:
            for pat, label in LEGACY_PATTERNS:
                if re.search(pat, s):
                    add(r.line, "MAL-003", "error",
                        f"'{label}' is old/classic list markup: on a modern list this rule matches "
                        "nothing. Use the selectors in references/selectors.md.", s)

    # MAL-004 / 005 / 006: the two meanings of .header-title
    for r in rules:
        props = {d[0] for d in r.decls}
        for s in r.selectors:
            if ".header-title" not in s:
                continue
            ns = norm(s)
            scoped_logo = re.search(r"\.header\s+(>\s*)?(a)?\.header-title", ns)
            scoped_cols = ".list-table-header" in ns or ".list-table" in ns
            if not scoped_logo and not scoped_cols:
                add(r.line, "MAL-004", "error",
                    ".header-title is both the MAL logo (.header .header-title) and every column "
                    "header cell (.list-table-header .header-title). Scope the selector to one of them.", s)
            if scoped_logo and props & {"background", "background-image"}:
                vals = " ".join(d[1] for d in r.decls if d[0] in ("background", "background-image"))
                if "url(" not in vals:
                    add(r.line, "MAL-005", "error",
                        "background/background-image on the logo (.header .header-title) removes the "
                        "MyAnimeList logo image. Style .header instead, or use background-color only.", s)
            if scoped_cols and any("gradient" in d[1] for d in r.decls if d[0] in PROPS_BG):
                add(r.line, "MAL-006", "warning",
                    "gradient on column header cells: it is redrawn inside EACH cell, so narrow and wide "
                    "columns get different-looking patches. Use a solid color.", s)
            if scoped_cols and any(d[0] == "background" for d in r.decls):
                add(r.line, "MAL-014", "info",
                    "'background' shorthand on column headers also removes MAL's 1px column separator "
                    "image. Fine if intended; use background-color to keep it.", s)

    # MAL-007: @import must come first
    for ln, stmt in imports:
        if first_rule_line is not None and ln > first_rule_line:
            add(ln, "MAL-007", "error",
                "@import after other rules is ignored by the browser: move it to the very top.", stmt[:80])
        if "http://" in stmt:
            add(ln, "MAL-012", "warning", "http:// import is blocked as mixed content on MAL (https).", stmt[:80])

    # MAL-008: status column background
    for r in rules:
        if not any(d[0] in PROPS_BG for d in r.decls):
            continue
        for s in r.selectors:
            ns = norm(s)
            if re.search(r"\.list-table-data\b.*\.data\b(?![\w-])", ns) and ":not(.status)" not in ns \
                    and ".status" not in ns and not re.search(r"\.data\.(?!status)[\w-]+", ns):
                add(r.line, "MAL-008", "warning",
                    "background on every .data cell also paints the thin status column (green=watching, "
                    "blue=completed...). Use .data:not(.status).", s)

    # MAL-009: missing !important where base uses it
    for r in rules:
        for s in r.selectors:
            ns = norm(s)
            for pat, props in BASE_IMPORTANT:
                if pat.search(ns):
                    for p, v, imp in r.decls:
                        if p in props and not imp:
                            add(r.line, "MAL-009", "warning",
                                f"MAL's base CSS sets '{p}' here with !important: without !important "
                                "this declaration has no effect.", s)

    # MAL-010: body font set but pinned selectors not covered
    body_font = any(d[0] in PROPS_FONT for r in rules for s in r.selectors if norm(s) == "body" for d in r.decls)
    if body_font:
        covered = {norm(s) for r in rules if any(d[0] in PROPS_FONT for d in r.decls) for s in r.selectors}
        missing = [p for p in FONT_PINNED_SELECTORS if p not in covered]
        if missing:
            add(1, "MAL-010", "warning",
                "font set on body, but these selectors are pinned to Verdana/Avenir by MAL and will "
                "not inherit it: " + "; ".join(missing))

    # MAL-011: unknown classes/ids (info)
    seen = set()
    for r in rules:
        for s in r.selectors:
            for tok in re.findall(r"[.#]([A-Za-z_][\w-]*)", re.sub(r"\[[^\]]*\]", "", s)):
                if tok not in KNOWN_TOKENS and tok not in seen:
                    seen.add(tok)
                    add(r.line, "MAL-011", "info",
                        f"'{tok}' is not in the documented MAL list markup: check it exists on the page.", s)

    # MAL-016: non-ASCII characters (MAL's Custom CSS field mangles them: "·" -> "Â·")
    for n, line in enumerate(css.splitlines(), 1):
        bad = sorted({c for c in line if ord(c) > 127})
        if bad:
            in_comment_only = not re.sub(r"/\*.*?\*/", "", line).strip() or \
                all(c not in re.sub(r"/\*.*?\*/", "", line) for c in bad)
            esc = " ".join("%s -> \\%06X" % (c, ord(c)) for c in bad)
            add(n, "MAL-016", "warning" if in_comment_only else "error",
                "non-ASCII characters are corrupted when MAL saves the CSS (e.g. '·' shows as 'Â·'). "
                "Inside strings use CSS escapes (" + esc + "); in comments use plain ASCII.")

    # MAL-015: visible credit for the kit (themes made with the skill keep it)
    if not any("mal-list-theme-kit" in d[1] for r in rules for s in r.selectors
               if "#footer-block" in s and "::after" in s for d in r.decls if d[0] == "content"):
        add(1, "MAL-015", "warning",
            "the visible credit is missing: end the theme with the #footer-block::after credit "
            "from SKILL.md (remove it only if the person asked to).")

    # MAL-013: webkit scrollbar only
    if any("::-webkit-scrollbar" in s for r in rules for s in r.selectors) and \
            not any(d[0] == "scrollbar-color" for r in rules for d in r.decls):
        add(1, "MAL-013", "info", "::-webkit-scrollbar only styles Chromium/Safari: add scrollbar-color for Firefox.")

    f.sort(key=lambda x: (x.file, x.line))
    return f


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    as_json, strict = "--json" in argv, "--strict" in argv
    if not args:
        print(__doc__)
        return 2
    findings: list[Finding] = []
    for p in args:
        try:
            with open(p, encoding="utf-8") as fh:
                findings += lint(p, fh.read())
        except OSError as e:
            print(f"cannot read {p}: {e}", file=sys.stderr)
            return 2
    errors = sum(x.severity == "error" for x in findings)
    warnings = sum(x.severity == "warning" for x in findings)
    if as_json:
        print(json.dumps({"errors": errors, "warnings": warnings, "findings": [asdict(x) for x in findings]}, indent=2))
    else:
        for x in findings:
            sel = f"  [{x.selector}]" if x.selector else ""
            print(f"{x.file}:{x.line}: {x.severity.upper()} {x.rule} {x.message}{sel}")
        print(f"\n{errors} error(s), {warnings} warning(s), {len(findings) - errors - warnings} info")
    return 1 if errors or (strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
