"""Install the built wheel into a fresh environment and test outside the checkout."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--wheel", type=Path, help="Built wheel; otherwise use dist's single wheel"
    )
    parser.add_argument(
        "--python", help="Interpreter for qualification; defaults to this Python"
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    wheels = (
        [args.wheel.resolve()] if args.wheel else list((root / "dist").glob("*.whl"))
    )
    if len(wheels) != 1:
        raise SystemExit("Provide exactly one built wheel with --wheel")
    with tempfile.TemporaryDirectory(prefix="ragwell-tools-wheel-") as directory:
        sandbox = Path(directory)
        venv = sandbox / "venv"
        subprocess.run(
            ["uv", "venv", "--python", args.python or sys.executable, str(venv)],
            check=True,
        )
        python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        subprocess.run(
            [
                "uv",
                "pip",
                "install",
                "--python",
                str(python),
                str(wheels[0]),
                "pytest==9.1.1",
            ],
            check=True,
        )
        shutil.copytree(
            root / "tests",
            sandbox / "tests",
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        shutil.copytree(
            root / "scripts",
            sandbox / "scripts",
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)
        subprocess.run(
            [
                str(python),
                "-c",
                "import pathlib,sys,ragwell_agent_tools; assert pathlib.Path(ragwell_agent_tools.__file__).resolve().is_relative_to(pathlib.Path(sys.prefix).resolve())",
            ],
            cwd=sandbox,
            env=env,
            check=True,
        )
        executable = python.parent / (
            "ragwell-agent-tools.exe" if os.name == "nt" else "ragwell-agent-tools"
        )
        subprocess.run([str(executable), "--version"], cwd=sandbox, env=env, check=True)
        subprocess.run(
            [
                str(python),
                "-m",
                "pytest",
                "tests",
                "--import-mode=importlib",
                "-p",
                "no:cacheprovider",
                "-q",
                "-W",
                "error",
            ],
            cwd=sandbox,
            env=env,
            check=True,
        )
    print("Installed-wheel qualification passed outside the source checkout.")


if __name__ == "__main__":
    main()
