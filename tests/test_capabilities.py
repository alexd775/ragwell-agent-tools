from __future__ import annotations

import asyncio
from uuid import UUID

import httpx
import pytest
from mcp import Client
from mcp.shared.exceptions import MCPError
from ragwell.types import MachineCapabilitiesResponse

from ragwell_agent_tools.sdk_operations import SdkOperations
from ragwell_agent_tools.tools import SearchRuntime, build_server

from .helpers import (
    FakeOperations,
    capabilities_body,
    result_data,
    settings,
    source_arguments,
)


@pytest.mark.parametrize(
    "scopes,project,expected",
    [
        (["retrieval:search"], 1, ["ragwell_search"]),
        (
            ["retrieval:search", "document:read"],
            1,
            ["ragwell_search", "ragwell_fetch_source"],
        ),
        (["document:read", "document:list"], 1, []),
        (["retrieval:search", "document:read"], 99, []),
    ],
)
def test_visible_tools_intersect_only_configured_project(
    scopes: list[str], project: int, expected: list[str]
) -> None:
    async def scenario() -> None:
        operations = FakeOperations()
        operations.capability_response = MachineCapabilitiesResponse.from_dict(
            capabilities_body(project_id=UUID(int=project), scopes=scopes)
        )
        async with Client(build_server(settings(), operations)) as client:
            assert [t.name for t in (await client.list_tools()).tools] == expected
        assert operations.capability_calls == 1
        assert not operations.requests and not operations.source_requests

    asyncio.run(scenario())


def test_cached_advertisement_cannot_dispatch_after_grant_loss() -> None:
    async def scenario() -> None:
        operations = FakeOperations()
        async with Client(build_server(settings(), operations)) as client:
            assert len((await client.list_tools()).tools) == 2
            await client.call_tool("ragwell_search", {"query": "x"})
            operations.capability_response = MachineCapabilitiesResponse.from_dict(
                capabilities_body(scopes=["retrieval:search"])
            )
            denied = await client.call_tool("ragwell_fetch_source", source_arguments())
            assert result_data(denied)["code"] == "access_denied"
            assert not operations.source_requests
            assert [t.name for t in (await client.list_tools()).tools] == [
                "ragwell_search"
            ]
            operations.capability_response = MachineCapabilitiesResponse.from_dict(
                capabilities_body(project_id=UUID(int=99))
            )
            denied = await client.call_tool("ragwell_search", {"query": "x"})
            assert result_data(denied)["code"] == "access_denied"
            assert not (await client.list_tools()).tools
        assert len(operations.requests) == 1

    asyncio.run(scenario())


@pytest.mark.parametrize(
    "status,code",
    [
        (401, "authentication_failed"),
        (403, "access_denied"),
        (404, "discovery_unavailable"),
        (503, "discovery_unavailable"),
    ],
)
def test_failed_discovery_never_falls_back_or_searches(status: int, code: str) -> None:
    async def scenario() -> None:
        calls: list[httpx.Request] = []

        def respond(request: httpx.Request) -> httpx.Response:
            calls.append(request)
            assert (
                request.method == "GET"
                and request.url.path == "/v1/machine/capabilities"
            )
            assert not request.url.query and not request.content
            assert (
                request.headers["Authorization"] == "Bearer synthetic-test-credential"
            )
            assert "Cookie" not in request.headers
            return httpx.Response(
                status, json={"error": {"code": "raw", "message": "secret-upstream"}}
            )

        async with SdkOperations(
            settings(), transport=httpx.MockTransport(respond)
        ) as operations:
            async with SearchRuntime(settings(), operations) as runtime:
                result = await runtime.call(
                    "ragwell_search", {"query": "private-query"}
                )
                assert result_data(result)["code"] == code
                assert not result_data(result)["usage_may_have_been_recorded"]
                assert "secret-upstream" not in result.model_dump_json()
                assert "private-query" not in result.model_dump_json()
        # SDK safe reads may retry; every wire request remains discovery.
        assert len(calls) == (3 if status == 503 else 1)

    asyncio.run(scenario())


@pytest.mark.parametrize(
    "kind",
    ["empty", "oversized", "duplicate_projects", "duplicate_scopes", "empty_scopes"],
)
def test_malformed_snapshot_is_rejected_as_a_whole(kind: str) -> None:
    async def scenario() -> None:
        raw = capabilities_body()
        if kind == "empty":
            raw["projects"] = []
        elif kind == "oversized":
            raw["projects"] = [
                capabilities_body(project_id=UUID(int=n))["projects"][0]
                for n in range(1, 102)
            ]
        elif kind == "duplicate_projects":
            raw["projects"] *= 2
        elif kind == "duplicate_scopes":
            raw["projects"][0]["scopes"] = ["retrieval:search"] * 2
        else:
            raw["projects"][0]["scopes"] = []
        operations = FakeOperations()
        operations.capability_response = MachineCapabilitiesResponse.from_dict(raw)
        async with Client(build_server(settings(), operations)) as client:
            with pytest.raises(MCPError) as error:
                await client.list_tools()
            assert "safely represented" in str(error.value)
        assert not operations.requests

    asyncio.run(scenario())


def test_discovery_failure_and_recovery_clear_previously_issued_sources() -> None:
    async def scenario() -> None:
        operations = FakeOperations()
        async with SearchRuntime(settings(), operations) as runtime:
            await runtime.call("ragwell_search", {"query": "x"})
            operations.capability_error = RuntimeError("secret-failure")
            failed = await runtime.available_tools()
            assert not isinstance(failed, frozenset)
            assert result_data(failed)["code"] == "discovery_unavailable"
            operations.capability_error = None
            denied = await runtime.call("ragwell_fetch_source", source_arguments())
            assert result_data(denied)["code"] == "source_reference_unavailable"
        assert not operations.source_requests

    asyncio.run(scenario())


def test_discovery_timeout_consumes_no_search_attempt_and_can_be_cancelled() -> None:
    async def scenario() -> None:
        class Slow(FakeOperations):
            async def capabilities(self) -> MachineCapabilitiesResponse:
                await asyncio.Event().wait()
                raise AssertionError("unreachable")

        async with SearchRuntime(
            settings(timeout_seconds=0.01, max_searches=1), Slow()
        ) as runtime:
            task = asyncio.create_task(runtime.call("ragwell_search", {"query": "x"}))
            await asyncio.sleep(0)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            result = await runtime.call("ragwell_search", {"query": "x"})
            assert result_data(result)["code"] == "discovery_timeout"
            assert not result_data(result)["usage_may_have_been_recorded"]
            assert runtime._attempts == 0

    asyncio.run(scenario())
