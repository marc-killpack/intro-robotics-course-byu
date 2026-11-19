"""Copy an explicit allowlist and strip answers without editing faculty files."""

import argparse
import ast
import hashlib
import json
import posixpath
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path("release_tools/release_manifest.json")
BEGIN = "# BEGIN SOLUTION"
END = "# END SOLUTION"


def strip_solutions(text, name="<text>"):
    """Reject malformed marker pairs before returning a stripped copy."""
    output = []
    inside = False
    count = 0
    for number, line in enumerate(text.splitlines(keepends=True), 1):
        marker = line.strip()
        if marker == BEGIN:
            if inside:
                raise ValueError(f"{name}:{number}: nested solution marker")
            inside = True
            count += 1
        elif marker == END:
            if not inside:
                raise ValueError(f"{name}:{number}: unmatched end marker")
            inside = False
        elif not inside:
            output.append(line)
    if inside:
        raise ValueError(f"{name}: missing end marker")
    return "".join(output), count


def safe_path(root, relative):
    """Keep manifest paths inside their root and reject symlink inputs."""
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise ValueError(f"Invalid manifest path: {relative}")
    path = root / relative
    if any(part.is_symlink() for part in [path, *path.parents] if part != root.parent):
        raise ValueError(f"Symlink paths are not release inputs: {relative}")
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Path leaves its root: {relative}")
    return path


def git_text(root, *arguments):
    return subprocess.check_output(
        ["git", "-C", str(root), *arguments], text=True, encoding="utf-8"
    ).strip()


def check_local_links(files):
    """Check student-facing Markdown against the actual selected copy."""
    for name, data in files.items():
        if not name.endswith(".md"):
            continue
        for target in re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", data.decode("utf-8")):
            link = urlsplit(target)
            if link.scheme or not link.path:
                continue
            path = posixpath.normpath(
                posixpath.join(posixpath.dirname(name), unquote(link.path))
            )
            if path not in files:
                raise ValueError(f"Broken student link in {name}: {target}")


def prepare_release(root):
    """Read and validate every selected file before creating a destination."""
    manifest_bytes = (root / MANIFEST).read_bytes()
    manifest = json.loads(manifest_bytes)
    prepared = {}
    hashes = {}
    blocks = 0
    for source, target in manifest["files"].items():
        source_path = safe_path(root, source)
        safe_path(root, target)
        source_parts = Path(source).parts
        if (
            any(
                part in {"instructor", "release_tools", ".git"} for part in source_parts
            )
            or ("tests" in source_parts and source_parts[:2] != ("tests", "public"))
            or source_parts[:2] == ("docs", "homework")
        ):
            raise ValueError(f"Faculty source selected for release: {source}")
        parts = Path(target).parts
        if any(part in {"instructor", "release_tools", ".git"} for part in parts) or (
            "tests" in parts and parts[:2] != ("tests", "public")
        ):
            raise ValueError(f"Faculty path selected for release: {target}")
        if target.endswith((".tex", ".ipynb")) or "_key" in target:
            raise ValueError(f"Unreviewed document or key selected: {target}")
        if target in prepared:
            raise ValueError(f"Duplicate destination: {target}")
        data = source_path.read_bytes()
        hashes[source] = hashlib.sha256(data).hexdigest()
        if source_path.suffix == ".py":
            text, removed = strip_solutions(data.decode("utf-8"), source)
            ast.parse(text, filename=target)
            if BEGIN in text or END in text:
                raise ValueError(f"Solution marker remains in {target}")
            data = text.encode("utf-8")
            blocks += removed
        prepared[target] = data
    check_local_links(prepared)
    report = {
        "source_commit": git_text(root, "rev-parse", "HEAD"),
        "source_dirty": bool(git_text(root, "status", "--porcelain")),
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "scope": manifest["scope"],
        "files": len(prepared),
        "removed_solution_blocks": blocks,
        "input_sha256": hashes,
    }
    return prepared, report


def write_release(root, destination, allow_dirty=False):
    root = Path(root).resolve()
    destination = Path(destination).resolve()
    if destination.exists():
        raise FileExistsError(f"Use a new release directory: {destination}")
    if destination == root or destination in root.parents:
        raise ValueError("A release cannot replace the source or its parents")
    if destination.is_relative_to(root) and not destination.is_relative_to(
        root / "release_output"
    ):
        raise ValueError("Use release_output/ for a review copy inside this repository")
    prepared, report = prepare_release(root)
    if report["source_dirty"] and not allow_dirty:
        raise ValueError(
            "Review and commit the source first; use --dry-run for a dirty preview"
        )
    for target in prepared:
        safe_path(destination, target)
    destination.mkdir(parents=True)
    for target, data in prepared.items():
        path = destination / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", nargs="?")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        if args.dry_run:
            if args.destination:
                parser.error("--dry-run does not accept a destination")
            preview_root = ROOT / "release_output"
            preview_root.mkdir(exist_ok=True)
            with tempfile.TemporaryDirectory(
                prefix="preview-", dir=preview_root
            ) as temporary:
                report = write_release(
                    ROOT, Path(temporary) / "student", allow_dirty=True
                )
            report["preview_discarded"] = True
        else:
            if not args.destination:
                parser.error("provide a new destination or use --dry-run")
            destination = Path(args.destination).resolve()
            report_path = destination.with_name(destination.name + "-report.json")
            if report_path.exists():
                raise FileExistsError(f"Report already exists: {report_path}")
            report = write_release(ROOT, destination)
            report_path.write_text(
                json.dumps(report, indent=2) + "\n", encoding="utf-8"
            )
        print(json.dumps(report, indent=2))
    except (ValueError, FileNotFoundError, FileExistsError) as error:
        parser.exit(1, f"Release stopped: {error}\n")


if __name__ == "__main__":
    main()
