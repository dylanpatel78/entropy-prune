"""Inline the data payload and emit both demo builds."""
import pathlib

here = pathlib.Path(__file__).parent
src = (here / "demo.src.html").read_text()
data = (here / "data.js").read_text()
body = src.replace("__DATA__", data)

# 1) artifact build: body content only (the Artifact tool supplies the skeleton)
(here / "artifact.html").write_text(body)

# 2) standalone build: full document, drop-in for a personal website
standalone = (
    "<!doctype html>\n<html lang=\"en\">\n<head>\n"
    "<meta charset=\"utf-8\">\n"
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
    "<style>:root{color-scheme:light dark}body{margin:0}"
    "img{max-width:100%}[hidden]{display:none!important}</style>\n"
    "</head>\n<body>\n" + body + "\n</body>\n</html>\n"
)
(here / "context-pruner.html").write_text(standalone)

for name in ("artifact.html", "context-pruner.html"):
    print(f"{name}: {(here/name).stat().st_size/1024:.1f} KB")
