#!/usr/bin/env python3
"""Self-test for the linter: themes must be clean, the bad fixture must trip every rule."""
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import lint_css  # noqa: E402

failed = 0


def check(cond, msg):
    global failed
    print(("ok   " if cond else "FAIL ") + msg)
    failed += 0 if cond else 1


themes = sorted(glob.glob(os.path.join(ROOT, "themes", "*.css")))
check(len(themes) >= 4, f"{len(themes)} bundled themes found")
for path in themes:
    with open(path, encoding="utf-8") as fh:
        css = fh.read()
    findings = lint_css.lint(path, css)
    bad = [f for f in findings if f.severity in ("error", "warning")]
    check(not bad, f"{os.path.basename(path)} lints clean" + (f": {[(f.rule, f.line) for f in bad]}" if bad else ""))
    check("@import" in css and css.index("@import") < css.index(":root {"),
          f"{os.path.basename(path)} has @import before :root")
    check("github.com/dpassa/mal-list-theme-kit" in css.strip().splitlines()[-2],
          f"{os.path.basename(path)} ends with the credit comment")
    check("#footer-block::after" in css and "github.com/dpassa/mal-list-theme-kit\";" in css,
          f"{os.path.basename(path)} has the visible footer credit")
    check(all(ord(c) < 128 for c in css), f"{os.path.basename(path)} is ASCII-only (MAL corrupts other characters)")

import subprocess  # noqa: E402

sync = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_plugin_themes.py"), "--check"],
                      capture_output=True, text=True)
check(sync.returncode == 0, "plugin Markdown themes match themes/*.css" + (": " + sync.stdout.strip() if sync.returncode else ""))

# The plugin directory only accepts Markdown, text, JSON, YAML and images from non-verified publishers.
ALLOWED = {".md", ".txt", ".json", ".yaml", ".yml", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}
plugin_dir = os.path.join(ROOT, "plugins", "mal-list-theming")
for dirpath, _, files in os.walk(plugin_dir):
    for f in files:
        full = os.path.join(dirpath, f)
        rel = os.path.relpath(full, plugin_dir)
        ext = os.path.splitext(f)[1].lower()
        with open(full, "rb") as fh:
            data = fh.read()
        image = ext in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}
        ok = ext in ALLOWED
        if not image:
            ok = ok and not data.startswith(b"#!") and b"\x00" not in data
            try:
                data.decode("utf-8")
            except UnicodeDecodeError:
                ok = False
        check(ok, f"plugin file allowed by the directory: {rel}")

with open(os.path.join(ROOT, "tests", "fixtures", "bad.css"), encoding="utf-8") as fh:
    rules = {f.rule for f in lint_css.lint("bad.css", fh.read())}
for expected in ["MAL-001", "MAL-002", "MAL-003", "MAL-004", "MAL-005", "MAL-006",
                 "MAL-007", "MAL-008", "MAL-009", "MAL-016"]:
    check(expected in rules, f"bad.css triggers {expected}")

# body font without the pinned selectors must warn (the bug that left the tabs in Verdana)
partial = "@import url('https://x');\nbody { font-family: X !important; }\n"
check(any(f.rule == "MAL-010" for f in lint_css.lint("partial.css", partial)), "body-only font triggers MAL-010")

# attribute selectors with * must not be mistaken for the universal selector
attr = "[class*=title] { font-family: X !important; }\n"
check(not any(f.rule == "MAL-001" for f in lint_css.lint("attr.css", attr)), "[class*=...] is not the universal selector")

print(f"\n{'all passed' if not failed else f'{failed} failed'}")
sys.exit(1 if failed else 0)
