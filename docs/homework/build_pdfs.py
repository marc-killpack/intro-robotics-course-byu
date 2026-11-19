"""Build selected LaTeX handouts into an ignored faculty output directory."""

import argparse
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent


def build(homework, render=False):
    if not re.fullmatch(r"hw\d{2}", homework):
        raise ValueError("Use homework directory names such as hw01")
    source = ROOT / homework / "homework.tex"
    if not source.is_file():
        raise FileNotFoundError(source)
    compiler = shutil.which("pdflatex")
    if compiler is None:
        raise RuntimeError(
            "Install TeX Live or another distribution providing pdflatex"
        )
    output = ROOT / "build" / homework
    output.mkdir(parents=True, exist_ok=True)
    name = f"homework_{homework[2:]}"
    command = [
        compiler,
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        f"-output-directory={output}",
        f"-jobname={name}",
        source.name,
    ]
    for _ in range(2):
        result = subprocess.run(
            command, cwd=source.parent, capture_output=True, text=True, errors="replace"
        )
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
    pdf = output / f"{name}.pdf"
    if render:
        renderer = shutil.which("pdftoppm")
        if renderer is None:
            raise RuntimeError(
                "Install Poppler (pdftoppm) to render the handout for review"
            )
        subprocess.run(
            [renderer, "-scale-to", "1500", "-png", str(pdf), str(output / "page")],
            check=True,
        )
    return pdf


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("homework", nargs="*", default=["hw01"])
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    for homework in args.homework:
        print(build(homework, render=args.render))
