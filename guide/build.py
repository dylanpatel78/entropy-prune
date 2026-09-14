"""Emit the field-guide builds: artifact fragment and standalone document."""

import pathlib

HEAD = (
    '<!doctype html>\n<html lang="en">\n<head>\n'
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    '<meta name="description" content="Field guide to spectral context pruning: '
    "embeddings, cosine similarity, SVD, Shannon entropy and submodular "
    'selection, with self-test questions.">\n'
    "<style>:root{color-scheme:light dark}body{margin:0}"
    "img{max-width:100%}[hidden]{display:none!important}</style>\n"
    "</head>\n<body>\n"
)
TAIL = "\n</body>\n</html>\n"


def main() -> None:
    """Write both guide variants from the single source file."""
    here = pathlib.Path(__file__).parent
    root = here.parent
    body = (here / "guide.src.html").read_text()
    targets = {
        root / "docs" / "guide.html": HEAD + body + TAIL,
        here / "artifact.html": body,
    }
    for path, text in targets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        print(f"{path.relative_to(root)}: {len(text) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
