from __future__ import annotations

import importlib.util
import io
import subprocess
import sys
import tarfile
from pathlib import Path
from zipfile import ZipFile

import pytest


def check_archives(
    directory: Path, wheel_member: str, source_member: str
) -> subprocess.CompletedProcess[str]:
    wheel = directory / "fixture.whl"
    source = directory / "fixture.tar.gz"
    with ZipFile(wheel, "w") as archive:
        archive.writestr(wheel_member, "fictional-package")
    with tarfile.open(source, "w:gz") as archive:
        body = b"fictional-package"
        member = tarfile.TarInfo(source_member)
        member.size = len(body)
        archive.addfile(member, io.BytesIO(body))
    script = Path(__file__).resolve().parents[1] / "scripts/check_public_artifacts.py"
    return subprocess.run(
        [sys.executable, str(script), "--wheel", str(wheel), "--sdist", str(source)],
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_public_code_and_user_docs_are_allowed(tmp_path: Path) -> None:
    result = check_archives(
        tmp_path, "ragwell_agent_tools/tools.py", "fixture/docs/connect/codex.md"
    )
    assert result.returncode == 0, result.stderr
    assert "no private project paths" in result.stdout


@pytest.mark.parametrize(
    ("wheel_member", "source_member"),
    [
        ("private/participant-record.md", "fixture/README.md"),
        ("ragwell_agent_tools/tools.py", "fixture/private/participant-record.md"),
        ("ragwell_agent_tools/tools.py", "fixture/docs/project/participant-record.md"),
        ("ragwell_agent_tools/tools.py", "fixture/Private/participant-record.md"),
        ("../participant-record.md", "fixture/README.md"),
        ("/participant-record.md", "fixture/README.md"),
        ("private\\participant-record.md", "fixture/README.md"),
    ],
)
def test_non_public_archive_paths_fail_without_echoing_private_names(
    tmp_path: Path, wheel_member: str, source_member: str
) -> None:
    result = check_archives(tmp_path, wheel_member, source_member)
    assert result.returncode != 0
    assert "non-public path" in result.stderr
    assert "participant-record" not in result.stdout + result.stderr


@pytest.mark.parametrize(
    "target",
    [
        "../private/participant-record.md",
        "../private%2Fparticipant-record.md",
        "../docs/project/participant-record.md",
        "https://github.com/alexd775/ragwell-agent-tools/blob/main/private/participant-record.md",
        "https://github.com/alexd775/ragwell-agent-tools/blob/main/docs/project/participant-record.md",
    ],
)
def test_public_links_cannot_reach_internal_material(
    tmp_path: Path, target: str
) -> None:
    script = Path(__file__).resolve().parents[1] / "scripts/check_documents.py"
    spec = importlib.util.spec_from_file_location("document_checker", script)
    assert spec is not None and spec.loader is not None
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    page = tmp_path / "docs/start.md"
    with pytest.raises(SystemExit, match="private project material"):
        checker.check_link(tmp_path, page, target)
