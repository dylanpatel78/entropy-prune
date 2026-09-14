"""Inline the precomputed data payload and emit the demo builds.

Two outputs from one source:
  docs/index.html   full standalone document, served by GitHub Pages
  web/artifact.html body-only fragment, for hosts that supply their own skeleton
"""

import pathlib

HEAD = (
    '<!doctype html>\n<html lang="en">\n<head>\n'
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    '<meta name="description" content="Interactive demo: context pruning driven '
    'by the eigenvalue spectrum of a sentence-embedding matrix.">\n'
    "<style>:root{color-scheme:light dark}body{margin:0}"
    "img{max-width:100%}[hidden]{display:none!important}</style>\n"
    "</head>\n<body>\n"
)
TAIL = "\n</body>\n</html>\n"


def main() -> None:
    """Build both demo variants from ``demo.src.html`` and ``data.js``."""
    web = pathlib.Path(__file__).parent
    root = web.parent
    body = (
        (web / "demo.src.html")
        .read_text()
        .replace("__DATA__", (web / "data.js").read_text())
    )
    if "__DATA__" in body:
        raise RuntimeError("data injection point not replaced")

    targets = {
        root / "docs" / "index.html": HEAD + body + TAIL,
        web / "artifact.html": body,
    }
    for path, text in targets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        print(f"{path.relative_to(root)}: {len(text) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
