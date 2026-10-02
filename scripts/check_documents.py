"""Check local guide links and parse credential-free host templates."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    paths = [
        root / "README.md",
        root / "CONTRIBUTING.md",
        *root.glob("docs/**/*.md"),
        *root.glob("examples/**/*.md"),
    ]
    for path in paths:
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            relative = target.split("#", 1)[0]
            if not (path.parent / relative).exists():
                raise SystemExit(
                    f"Missing local link in {path.relative_to(root)}: {target}"
                )
    for path in root.glob("integrations/**/*.json"):
        json.loads(path.read_text())
    for path in root.glob("integrations/**/*.toml"):
        tomllib.loads(path.read_text())
    print("Local document links and host configuration syntax passed.")


if __name__ == "__main__":
    main()
