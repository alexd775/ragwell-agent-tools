"""Collect distribution notices for a frozen Ragwell release asset."""

from __future__ import annotations

import argparse
import re
import tarfile
from hashlib import file_digest
from importlib.metadata import distributions
from pathlib import Path, PurePosixPath
from sysconfig import get_path

PYTHON_BUILD_TAG = "20260901"
PYTHON_BUILD_SOURCE_SHA256 = (
    "bf4776e7bdb751a58fa6879d280b678f60b955b62b19ec98a32903fd82cee1c6"
)
LICENSE_NAME = re.compile(r"^(license|licence|copying|notice|copyright)([._-]|$)", re.I)


def python_build_licenses(source: Path) -> list[tuple[str, str]]:
    with source.open("rb") as stream:
        if file_digest(stream, "sha256").hexdigest() != PYTHON_BUILD_SOURCE_SHA256:
            raise ValueError("the Python build source archive hash did not match")

    licenses = []
    with tarfile.open(source, "r:gz") as archive:
        for entry in archive:
            path = PurePosixPath(entry.name)
            if (
                entry.isfile()
                and path.parent.name == f"python-build-standalone-{PYTHON_BUILD_TAG}"
                and LICENSE_NAME.match(path.name)
            ):
                content = archive.extractfile(entry)
                if content is None:
                    raise ValueError(f"missing license contents for {path.name}")
                with content:
                    licenses.append((path.name, content.read().decode("utf-8")))
    return sorted(licenses)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python-build-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    python_license = Path(get_path("stdlib")) / "LICENSE.txt"
    sections = [
        "Ragwell Open Source Notices\n"
        "The files below accompany the Ragwell executable. The list includes "
        "licenses for installed build inputs as well as the bundled runtime.\n",
        f"CPython\n{python_license.read_text(encoding='utf-8')}",
    ]
    source_url = (
        "https://github.com/astral-sh/python-build-standalone/tree/" + PYTHON_BUILD_TAG
    )
    for name, content in python_build_licenses(args.python_build_source):
        sections.append(f"Python Build Standalone {name}\n{source_url}\n\n{content}")

    for package in sorted(
        distributions(), key=lambda distribution: distribution.metadata["Name"].lower()
    ):
        name = package.metadata["Name"]
        licenses = [
            path for path in package.files or () if LICENSE_NAME.match(path.name)
        ]
        if not licenses:
            raise ValueError(f"no distribution notices found for {name}")
        sections.append(
            f"{name} {package.version}\n"
            f"https://pypi.org/project/{name}/{package.version}/"
        )
        for path in sorted(licenses):
            content = package.locate_file(path).read_text()
            sections.append(f"{path}\n\n{content}")

    args.output.write_text("\n\n".join(sections) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
