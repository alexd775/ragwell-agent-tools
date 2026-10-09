"""Reject private project material in built wheel and source archives."""

from __future__ import annotations

import argparse
import tarfile
from collections.abc import Iterable
from pathlib import Path, PurePosixPath
from zipfile import ZipFile


def check_members(names: Iterable[str]) -> None:
    for name in names:
        path = PurePosixPath(name)
        parts = tuple(part.casefold() for part in path.parts)
        if (
            path.is_absolute()
            or ".." in parts
            or "\\" in name
            or "private" in parts
            or any(
                parts[index : index + 2] == ("docs", "project")
                for index in range(len(parts))
            )
        ):
            raise SystemExit("Release archive contains a non-public path.")


def single_archive(directory: Path, pattern: str) -> Path:
    files = list(directory.glob(pattern))
    if len(files) != 1:
        raise SystemExit("Select the exact release files with --wheel and --sdist.")
    return files[0]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path)
    parser.add_argument("--sdist", type=Path)
    args = parser.parse_args()
    directory = Path(__file__).resolve().parents[1] / "dist"
    wheel = args.wheel or single_archive(directory, "*.whl")
    sdist = args.sdist or single_archive(directory, "*.tar.gz")
    with ZipFile(wheel) as archive:
        check_members(archive.namelist())
    with tarfile.open(sdist) as source:
        check_members(source.getnames())
    print("Wheel and source distribution contain no private project paths.")


if __name__ == "__main__":
    main()
