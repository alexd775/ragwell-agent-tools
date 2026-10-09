"""Check public guide links and credential-free host templates."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


def is_private_link(target: str) -> bool:
    parts = tuple(part.casefold() for part in PurePosixPath(unquote(target)).parts)
    return "private" in parts or any(
        parts[index : index + 2] == ("docs", "project") for index in range(len(parts))
    )


def check_link(root: Path, path: Path, target: str) -> None:
    parsed = urlsplit(target)
    if parsed.scheme or target.startswith("#"):
        if (
            parsed.netloc.casefold() == "github.com"
            and parsed.path.casefold().startswith("/alexd775/ragwell-agent-tools/")
            and is_private_link(parsed.path)
        ):
            raise SystemExit("Public guide links to private project material.")
        return
    resolved = (path.parent / unquote(parsed.path)).resolve()
    if not resolved.is_relative_to(root):
        raise SystemExit("Public guide link escapes the repository.")
    if is_private_link(resolved.relative_to(root).as_posix()):
        raise SystemExit("Public guide links to private project material.")
    if not resolved.exists():
        raise SystemExit(f"Missing local link in {path.relative_to(root)}.")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    if (root / "docs" / "project").exists():
        raise SystemExit("Internal project documents belong in ignored private/.")
    paths = [
        *(
            root / name
            for name in ("README.md", "CONTRIBUTING.md", "SECURITY.md", "AGENTS.md")
        ),
        *root.glob("docs/**/*.md"),
        *root.glob("examples/**/*.md"),
        *root.glob("skills/**/*.md"),
    ]
    for path in paths:
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            check_link(root, path, target)
    for path in root.glob("integrations/**/*.json"):
        json.loads(path.read_text())
    for path in root.glob("integrations/**/*.toml"):
        tomllib.loads(path.read_text())
    print("Public document links and host configuration syntax passed.")


if __name__ == "__main__":
    main()
