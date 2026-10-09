from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest

NAMES = (
    "handbook.md",
    "travel-policy-2025.md",
    "travel-policy-2026.md",
    "project-decisions.md",
)


def run_builder(root: Path, *, check: bool = False) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(root / "scripts/build_sample_pack.py")]
    if check:
        command.append("--check")
    return subprocess.run(command, capture_output=True, text=True, timeout=10)


def prepare_samples(root: Path) -> None:
    scripts = root / "scripts"
    scripts.mkdir()
    source = Path(__file__).resolve().parents[1] / "scripts/build_sample_pack.py"
    shutil.copyfile(source, scripts / source.name)
    samples = root / "examples/sample-knowledge"
    samples.mkdir(parents=True)
    for name in NAMES:
        (samples / name).write_bytes(f"# {name}\n\nFictional café policy.\n".encode())
    (samples / "injection-exercise.md").write_bytes(b"Excluded hostile fixture.\n")
    result = run_builder(root)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("line_endings", ["lf", "crlf", "mixed"])
def test_sample_archive_is_identical_across_checkout_line_endings(
    tmp_path: Path, line_endings: str
) -> None:
    prepare_samples(tmp_path)
    target = tmp_path / "examples/starter/starter-documents.zip"
    original = target.read_bytes()
    samples = tmp_path / "examples/sample-knowledge"
    for name in NAMES:
        path = samples / name
        data = path.read_bytes()
        if line_endings == "crlf":
            data = data.replace(b"\n", b"\r\n")
        elif line_endings == "mixed":
            data = data.replace(b"\n", b"\r\n", 1)
        path.write_bytes(data)

    result = run_builder(tmp_path, check=True)
    assert result.returncode == 0, result.stderr
    result = run_builder(tmp_path)
    assert result.returncode == 0, result.stderr
    assert target.read_bytes() == original
    with ZipFile(target) as archive:
        assert archive.namelist() == list(NAMES)
        assert archive.testzip() is None
        for name in NAMES:
            assert (
                archive.read(name) == f"# {name}\n\nFictional café policy.\n".encode()
            )


def test_sample_check_still_rejects_substantive_document_changes(
    tmp_path: Path,
) -> None:
    prepare_samples(tmp_path)
    document = tmp_path / "examples/sample-knowledge/handbook.md"
    document.write_bytes(
        document.read_bytes() + b"New fictional leave entitlement.\r\n"
    )
    result = run_builder(tmp_path, check=True)
    assert result.returncode != 0
    assert "Stale sample pack" in result.stderr
    assert run_builder(tmp_path).returncode == 0
    assert run_builder(tmp_path, check=True).returncode == 0
