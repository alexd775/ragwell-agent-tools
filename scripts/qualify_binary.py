"""Exercise a frozen executable against a synthetic Ragwell HTTP peer."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import tempfile
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from uuid import UUID

PROJECT = str(UUID(int=1))
DOCUMENT = str(UUID(int=2))
VERSION = str(UUID(int=3))
GENERATION = str(UUID(int=4))
SOURCE = str(UUID(int=5))
QUERY = "Who approves travel?"
PASSAGE = "Ask your manager before booking travel."
KEY = "synthetic-binary-fixture"
SEARCH_PATH = f"/v1/projects/{PROJECT}/search"
SOURCE_PATH = f"/v1/projects/{PROJECT}/documents/{DOCUMENT}/generations/{GENERATION}/sources/{SOURCE}"


class FixtureHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass

    def respond(self, body: dict[str, Any], status: int = 200) -> None:
        encoded = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        if self.headers.get("Authorization") != f"Bearer {KEY}":
            self.respond({"error": {"code": "unauthorized", "message": "fixture"}}, 401)
        elif self.path == "/v1/machine/capabilities":
            self.respond(
                {
                    "projects": [
                        {
                            "project_id": PROJECT,
                            "scopes": ["retrieval:search", "document:read"],
                        }
                    ]
                }
            )
        elif self.path == f"/v1/projects/{PROJECT}/agent-description":
            self.respond({"project_id": PROJECT, "description": "Travel policies."})
        elif self.path == f"{SOURCE_PATH}?offset=0&limit=1500":
            self.respond(
                {
                    "document_id": DOCUMENT,
                    "document_version_id": VERSION,
                    "generation_id": GENERATION,
                    "source_id": SOURCE,
                    "coordinate_kind": "text",
                    "source_ordinal": 0,
                    "page_number": None,
                    "character_count": len(PASSAGE),
                    "start_offset": 0,
                    "end_offset": len(PASSAGE),
                    "content": PASSAGE,
                    "next_offset": None,
                }
            )
        else:
            self.respond({"error": {"code": "not_found", "message": "fixture"}}, 404)

    def do_POST(self) -> None:
        if self.headers.get("Authorization") != f"Bearer {KEY}":
            self.respond({"error": {"code": "unauthorized", "message": "fixture"}}, 401)
            return
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.path != SEARCH_PATH or body != {"query": QUERY, "k": 1}:
            self.respond(
                {"error": {"code": "invalid_request", "message": "fixture"}}, 400
            )
            return
        print("fixture_search", flush=True)
        self.respond(
            {
                "retrieval_id": str(UUID(int=6)),
                "retrieval_version": "hybrid-v1",
                "profile_id": None,
                "items": [
                    {
                        "rank": 1,
                        "chunk_id": str(UUID(int=7)),
                        "document_id": DOCUMENT,
                        "document_version_id": VERSION,
                        "generation_id": GENERATION,
                        "source_filename": "travel-policy.md",
                        "content": PASSAGE,
                        "representation_version": "source-parts-v1",
                        "citation": None,
                        "scores": {"final": 0.7, "text": None, "vector": None},
                        "parts": [
                            {
                                "kind": "evidence",
                                "text": PASSAGE,
                                "source_id": SOURCE,
                                "start_line": 3,
                                "end_line": 3,
                                "span": {
                                    "source_ordinal": 0,
                                    "start_offset": 18,
                                    "end_offset": 18 + len(PASSAGE),
                                },
                            }
                        ],
                    }
                ],
            }
        )


def configuration(port: int) -> dict[str, str]:
    return {
        "RAGWELL_BASE_URL": f"http://127.0.0.1:{port}",
        "RAGWELL_PROJECT_ID": PROJECT,
        "RAGWELL_API_KEY": KEY,
        "RAGWELL_ALLOW_LOCAL_HTTP": "true",
    }


@contextmanager
def fixture() -> Iterator[int]:
    with ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield server.server_port
        finally:
            server.shutdown()
            thread.join()


def assert_citation(result: dict[str, Any], *, can_expand: bool) -> None:
    assert result["status"] == "ok", result.get("code")
    assert result["project_id"] == PROJECT
    assert result["source_text_is_untrusted"] is True
    assert result["source_expansion_available"] is can_expand
    (match,) = result["matches"]
    assert match["source_filename"] == "travel-policy.md"
    assert match["document_version_id"] == VERSION
    assert match["generation_id"] == GENERATION
    (part,) = match["parts"]
    assert part["kind"] == "evidence" and part["text"] == PASSAGE
    assert (part["start_line"], part["end_line"]) == (3, 3)
    assert (part["span"]["start_offset"], part["span"]["end_offset"]) == (
        18,
        18 + len(PASSAGE),
    )


async def qualify_mcp(binary: Path, directory: Path, env: dict[str, str]) -> None:
    from mcp import Client, StdioServerParameters

    parameters = StdioServerParameters(command=str(binary), cwd=directory, env=env)
    async with Client(parameters, mode="legacy", read_timeout_seconds=20) as client:
        listing = await client.list_tools()
        assert [tool.name for tool in listing.tools] == [
            "ragwell_search",
            "ragwell_fetch_source",
        ]
        result = await client.call_tool("ragwell_search", {"query": QUERY, "k": 1})
        assert not result.is_error and result.structured_content is not None
        assert_citation(result.structured_content, can_expand=True)
        source = await client.call_tool(
            "ragwell_fetch_source",
            {
                "document_id": DOCUMENT,
                "document_version_id": VERSION,
                "generation_id": GENERATION,
                "source_id": SOURCE,
            },
        )
        assert not source.is_error and source.structured_content is not None
        assert source.structured_content["content"] == PASSAGE


def run(
    command: list[str],
    *,
    input_data: str | None = None,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> str:
    return subprocess.run(
        command,
        input=input_data,
        capture_output=True,
        text=True,
        check=True,
        timeout=90,
        cwd=cwd,
        env=env,
    ).stdout.strip()


def qualify_native(binary: Path) -> None:
    with fixture() as port, tempfile.TemporaryDirectory() as workdir:
        directory = Path(workdir)
        env = configuration(port)
        clean_env = {"PATH": "/usr/bin:/bin", **env}
        debug_file = directory / "debug.jsonl"
        assert run([str(binary), "--version"], cwd=directory, env=clean_env)
        status = json.loads(
            run(
                [str(binary), "--check"],
                cwd=directory,
                env={**clean_env, "RAGWELL_DEBUG_LOG": str(debug_file)},
            )
        )
        assert status["status"] == "ready" and status["searches"] == 0
        diagnostic = json.loads(debug_file.read_text())
        assert diagnostic["mcp"] and diagnostic["ragwell_sdk"]
        evidence = json.loads(
            run(
                [str(binary), "search", "--query-stdin", "--k", "1"],
                cwd=directory,
                env=clean_env,
                input_data=QUERY,
            )
        )
        assert_citation(evidence, can_expand=False)
        asyncio.run(qualify_mcp(binary, directory, env))
    print("Standalone JSON and MCP reproduced the original source citation.")


def qualify_sandbox(binary: Path, image: str, peer_image: str) -> None:
    docker = ["docker", "run", "--rm", "--platform", "linux/amd64"]
    peer = run(
        [
            *docker,
            "--detach",
            "--network",
            "none",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--mount",
            f"type=bind,source={Path(__file__).resolve()},target=/fixture.py,readonly",
            peer_image,
            "python",
            "/fixture.py",
            "--serve-fixture",
        ]
    )
    try:
        for _ in range(50):
            if "fixture_ready" in run(["docker", "logs", peer]):
                break
            time.sleep(0.1)
        else:
            raise RuntimeError("The synthetic peer did not start.")
        env_flags = [
            flag
            for name, value in configuration(8080).items()
            for flag in ("--env", f"{name}={value}")
        ]
        output = run(
            [
                *docker,
                "--interactive",
                "--network",
                f"container:{peer}",
                "--read-only",
                "--tmpfs",
                "/tmp:rw,exec,nosuid,nodev",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges",
                *env_flags,
                "--mount",
                f"type=bind,source={binary},target=/ragwel-cli,readonly",
                image,
                "/bin/sh",
                "-ec",
                "for tool in python python3 uv; do "
                'if command -v "$tool" >/dev/null; then exit 1; fi; done\n'
                "/ragwel-cli --check\n"
                "exec /ragwel-cli search --query-stdin --k 1",
            ],
            input_data=QUERY,
        )
        status, result = map(json.loads, output.splitlines())
        assert status["status"] == "ready" and status["searches"] == 0
        assert_citation(result, can_expand=False)
        assert run(["docker", "logs", peer]).splitlines().count("fixture_search") == 1
    finally:
        run(["docker", "stop", "--time", "1", peer])
    print(
        "Linux x86-64 Docker sandbox without Python or uv returned travel-policy.md, line 3."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path)
    parser.add_argument("--sandbox-image")
    parser.add_argument("--peer-image")
    parser.add_argument("--serve-fixture", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.serve_fixture:
        with ThreadingHTTPServer(("127.0.0.1", 8080), FixtureHandler) as server:
            print("fixture_ready", flush=True)
            server.serve_forever()
        return
    if args.binary is None or bool(args.sandbox_image) != bool(args.peer_image):
        parser.error("provide --binary and optionally both Docker image arguments")
    os.environ.pop("PYTHONPATH", None)
    binary = args.binary.resolve(strict=True)
    if args.sandbox_image:
        qualify_sandbox(binary, args.sandbox_image, args.peer_image)
    else:
        qualify_native(binary)


if __name__ == "__main__":
    main()
