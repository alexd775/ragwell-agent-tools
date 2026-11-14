"""Freeze the local MCP entry point into a single executable for this machine."""

from __future__ import annotations

import argparse
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("dist/binary"))
    args = parser.parse_args()
    if (sys.platform, platform.machine()) not in {
        ("linux", "x86_64"),
        ("darwin", "arm64"),
    }:
        parser.error("building Ragwell requires Linux x86_64 or macOS arm64")

    output_dir = args.output_dir.resolve()
    root = Path(__file__).resolve().parents[1]
    skill = root / "skills" / "ragwell-knowledge" / "SKILL.md"
    with tempfile.TemporaryDirectory(prefix="ragwell-binary-build-") as directory:
        work = Path(directory)
        launcher = work / "ragwell_binary_entry.py"
        launcher.write_text(
            "from ragwell_agent_tools.stdio import main\n"
            "if __name__ == '__main__':\n"
            "    main()\n",
            encoding="utf-8",
        )
        subprocess.run(
            [
                sys.executable,
                "-m",
                "PyInstaller",
                "--clean",
                "--noconfirm",
                "--onefile",
                "--console",
                "--noupx",
                "--name",
                "ragwel-cli",
                "--distpath",
                str(output_dir),
                "--workpath",
                str(work / "build"),
                "--specpath",
                str(work),
                "--copy-metadata",
                "ragwell",
                "--copy-metadata",
                "mcp",
                "--collect-data",
                "certifi",
                "--add-data",
                f"{skill}:ragwell_agent_tools",
                str(launcher),
            ],
            check=True,
            cwd=work,
            env={**os.environ, "PYINSTALLER_CONFIG_DIR": str(work / "cache")},
        )


if __name__ == "__main__":
    main()
