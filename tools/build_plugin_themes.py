"""Copy themes/*.css into the plugin as Markdown files.

The Claude plugin directory accepts only Markdown, text, JSON, YAML and images
from non-verified publishers, so the plugin carries each theme as a .md file
with the CSS in a code block. themes/*.css stays the single source of truth.

    python tools/build_plugin_themes.py           # write the .md files
    python tools/build_plugin_themes.py --check   # exit 1 if they are stale
"""
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "themes")
DST = os.path.join(ROOT, "plugins", "mal-list-theming", "skills", "mal-list-theming", "themes")


def render(name, css):
    if "```" in css:
        raise SystemExit(f"{name}.css contains a code fence; cannot embed it")
    title = name.replace("-", " ").title()
    return (
        f"# {title} theme\n\n"
        f"Generated from `themes/{name}.css` in the repository; edit that file, not this one.\n\n"
        f"The theme is the content of the code block below, exactly as written. Copy it\n"
        f"into a new `.css` file before changing it.\n\n"
        f"```css\n{css.rstrip()}\n```\n"
    )


def main():
    check = "--check" in sys.argv[1:]
    os.makedirs(DST, exist_ok=True)
    stale = []
    wanted = set()
    for path in sorted(glob.glob(os.path.join(SRC, "*.css"))):
        name = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf-8") as fh:
            text = render(name, fh.read())
        out = os.path.join(DST, name + ".md")
        wanted.add(out)
        current = open(out, encoding="utf-8").read() if os.path.exists(out) else None
        if current != text:
            stale.append(out)
            if not check:
                with open(out, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(text)
    extra = [p for p in glob.glob(os.path.join(DST, "*")) if p not in wanted]
    if check:
        for p in stale + extra:
            print("stale:", os.path.relpath(p, ROOT))
        sys.exit(1 if stale or extra else 0)
    for p in extra:
        os.remove(p)
    print(f"{len(wanted)} theme(s) written, {len(stale)} changed, {len(extra)} removed")


if __name__ == "__main__":
    main()
