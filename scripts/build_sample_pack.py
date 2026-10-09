"""Build or check the small, deterministic ordinary-user sample archive."""

from __future__ import annotations

import argparse
import io
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo

NAMES = (
    "handbook.md",
    "travel-policy-2025.md",
    "travel-policy-2026.md",
    "project-decisions.md",
)


def archive_bytes(root: Path) -> bytes:
    output = io.BytesIO()
    with ZipFile(output, "w", compression=ZIP_STORED) as archive:
        for name in NAMES:
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            # Canonical LF keeps Windows checkouts byte-identical to the pack.
            content = (root / "examples" / "sample-knowledge" / name).read_bytes()
            archive.writestr(info, content.replace(b"\r\n", b"\n"))
    return output.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    target = root / "examples" / "starter" / "starter-documents.zip"
    expected = archive_bytes(root)
    if args.check:
        if not target.is_file() or target.read_bytes() != expected:
            raise SystemExit("Stale sample pack; run scripts/build_sample_pack.py.")
        print("Sample pack matches its four canonical fictional documents.")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(expected)
        print("Built the four-document ordinary-user sample pack.")


if __name__ == "__main__":
    main()
