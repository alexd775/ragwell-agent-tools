"""Expose and install the bundled Ragwell knowledge skill."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

_SKILL_NAME = "ragwell-knowledge"
_AGENT_FOLDERS = {"codex": ".agents", "claude-code": ".claude"}
SUPPORTED_AGENTS = tuple(_AGENT_FOLDERS)


def _skill_bytes() -> bytes:
    package = Path(__file__).resolve().parent
    skill = package / "SKILL.md"
    if not skill.is_file() and package.parent.name == "src":
        # Direct runs from a source checkout use the canonical copy.
        skill = package.parent.parent / "skills" / _SKILL_NAME / "SKILL.md"
    return skill.read_bytes()


def run_skill_command(agent: str | None) -> int:
    try:
        skill = _skill_bytes()
    except OSError:
        print("The bundled Ragwell skill is unavailable.", file=sys.stderr)
        return 1

    if agent is None:
        sys.stdout.buffer.write(skill)
        return 0

    try:
        skill_dir = Path.home() / _AGENT_FOLDERS[agent] / "skills" / _SKILL_NAME
        skill_dir.mkdir(parents=True, exist_ok=True)
        target = skill_dir / "SKILL.md"
        with TemporaryDirectory(prefix=".ragwell-install-", dir=skill_dir) as stage:
            download = Path(stage) / target.name
            download.write_bytes(skill)
            try:
                # Publish the complete file without replacing a concurrent install.
                os.link(download, target)
            except FileExistsError:
                if (
                    target.is_symlink()
                    or not target.is_file()
                    or target.read_bytes() != skill
                ):
                    print(
                        f"A different skill already exists at {target}. Review it before replacing it.",
                        file=sys.stderr,
                    )
                    return 1
                print(f"Ragwell skill already installed at {target}.")
                return 0
    except (OSError, RuntimeError):
        print("Could not write to the agent's skill directory.", file=sys.stderr)
        return 1

    print(f"Installed the Ragwell skill at {target}.")
    return 0
