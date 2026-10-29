"""Record installed dependency license declarations, including explicit metadata gaps."""

from __future__ import annotations

import argparse
import json
import re
from importlib.metadata import distributions
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--source-commit", required=True)
    arguments = parser.parse_args()
    if re.fullmatch(r"[0-9a-f]{40}", arguments.source_commit) is None:
        parser.error("--source-commit must be the full committed source revision")
    packages = []
    missing = []
    for distribution in sorted(
        distributions(), key=lambda item: item.metadata["Name"].casefold()
    ):
        metadata = distribution.metadata
        expression = next(iter(metadata.get_all("License-Expression", [])), None)
        license_text = next(iter(metadata.get_all("License", [])), None)
        classifiers = [
            value
            for value in metadata.get_all("Classifier", [])
            if value.startswith("License ::")
        ]
        files = metadata.get_all("License-File", [])
        name = metadata["Name"]
        if not any((expression, license_text, classifiers, files)):
            missing.append(name)
        packages.append(
            {
                "name": name,
                "version": distribution.version,
                "license_expression": expression,
                "license": license_text,
                "license_classifiers": classifiers,
                "declared_license_files": files,
            }
        )
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(
            {
                "source_commit": arguments.source_commit,
                "scope": "installed locked development environment; runtime and development",
                "packages": packages,
                "missing_license_metadata": missing,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"License metadata: {len(packages)} packages; {len(missing)} missing declarations."
    )


if __name__ == "__main__":
    main()
