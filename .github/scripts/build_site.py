#!/usr/bin/env python3
"""Build a static GitHub Pages showcase from this repo's notebooks.

Converts every .ipynb (excluding checkpoints) to HTML with nbconvert,
preserving relative paths, and writes an index.html linking to them all.
Does NOT re-execute notebooks - it renders whatever outputs are already saved.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "_site"
REPO_NAME = ROOT.name


def find_notebooks():
    return sorted(
        p for p in ROOT.rglob("*.ipynb")
        if ".ipynb_checkpoints" not in p.parts and "_site" not in p.parts
    )


def convert(nb_path: Path) -> Path:
    rel = nb_path.relative_to(ROOT)
    out_dir = SITE / rel.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable, "-m", "nbconvert", "--to", "html",
            "--output-dir", str(out_dir),
            str(nb_path),
        ],
        check=True,
    )
    return out_dir / (nb_path.stem + ".html")


def main():
    SITE.mkdir(exist_ok=True)
    notebooks = find_notebooks()
    if not notebooks:
        print("No notebooks found.")
    html_files = [convert(nb) for nb in notebooks]

    readme = ROOT / "README.md"
    tagline = ""
    if readme.exists():
        for line in readme.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("!["):
                tagline = line
                break

    links = "\n".join(
        f'<li><a href="{f.relative_to(SITE).as_posix()}">{f.stem}</a> '
        f'<span class="path">{nb.relative_to(ROOT).as_posix()}</span></li>'
        for nb, f in zip(notebooks, html_files)
    )

    index_html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{REPO_NAME}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; max-width: 760px; margin: 3rem auto; padding: 0 1.5rem; color: #1a1a1a; }}
  h1 {{ font-size: 1.6rem; }}
  p.tagline {{ color: #555; }}
  ul {{ list-style: none; padding: 0; }}
  li {{ padding: 0.75rem 1rem; margin-bottom: 0.5rem; border: 1px solid #e2e2e2; border-radius: 8px; }}
  li a {{ font-weight: 600; text-decoration: none; color: #2563eb; }}
  li a:hover {{ text-decoration: underline; }}
  .path {{ display: block; font-size: 0.8rem; color: #888; margin-top: 0.25rem; font-family: monospace; }}
  footer {{ margin-top: 2rem; font-size: 0.85rem; color: #999; }}
</style>
</head>
<body>
<h1>{REPO_NAME}</h1>
<p class="tagline">{tagline}</p>
<ul>
{links}
</ul>
<footer>Rendered notebooks - outputs shown as originally run, not re-executed. <a href="https://github.com/Bosaj/{REPO_NAME}">Source on GitHub</a></footer>
</body>
</html>
"""
    (SITE / "index.html").write_text(index_html, encoding="utf-8")
    print(f"Built {len(html_files)} notebook page(s) + index.html into {SITE}")


if __name__ == "__main__":
    main()
