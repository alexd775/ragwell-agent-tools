from __future__ import annotations

import asyncio
import inspect
from typing import Any

import httpx
import jsonschema
import pytest
from mcp import Client
from ragwell.types import DocumentSourcePreview, RetrievalItemResponse

from ragwell_agent_tools.evidence import result_bytes
from ragwell_agent_tools.operations import FetchSourceInput
from ragwell_agent_tools.sdk_operations import SdkOperations
from ragwell_agent_tools.source import project_source
from ragwell_agent_tools.tools import SearchRuntime, build_server

from .helpers import (
    DOCUMENT_ID,
    GENERATION_ID,
    PROJECT_ID,
    SOURCE_ID,
    FakeOperations,
    result_data,
    search_body,
    settings,
    source_arguments,
    source_body,
)


@pytest.mark.parametrize(
    "overrides",
    [
        {"offset": -1},
        {"offset": 2_147_483_647},
        {"offset": True},
        {"limit": 0},
        {"limit": 4001},
        {"limit": "1"},
        {"document_id": "bad"},
        {"source_id": 5},
        {"project_id": str(PROJECT_ID)},
        {"base_url": "https://other.invalid"},
    ],
)
def test_invalid_source_arguments_never_dispatch(overrides: dict[str, Any]) -> None:
    async def scenario() -> None:
        operations = FakeOperations()
        async with SearchRuntime(settings(), operations) as runtime:
            await runtime.call("ragwell_search", {"query": "x"})
            result = await runtime.call(
                "ragwell_fetch_source", source_arguments(**overrides)
            )
            assert result_data(result)["code"] == "invalid_arguments"
            assert not operations.source_requests

    asyncio.run(scenario())


def test_source_references_must_have_been_returned_in_this_connection() -> None:
    async def scenario() -> None:
        operations = FakeOperations()
        async with SearchRuntime(settings(), operations) as runtime:
            denied = await runtime.call("ragwell_fetch_source", source_arguments())
            assert result_data(denied)["code"] == "source_reference_unavailable"
            await runtime.call("ragwell_search", {"query": "x"})
            substituted = await runtime.call(
                "ragwell_fetch_source",
                source_arguments(document_version_id=str(PROJECT_ID)),
            )
            assert result_data(substituted)["code"] == "source_reference_unavailable"
            assert not operations.source_requests

    asyncio.run(scenario())


def test_search_without_generation_remains_usable_but_cannot_expand() -> None:
    async def scenario() -> None:
        body = search_body()
        del body["items"][0]["generation_id"]
        calls: list[httpx.Request] = []

        def respond(request: httpx.Request) -> httpx.Response:
            calls.append(request)
            return httpx.Response(200, json=body)

        async with SdkOperations(
            settings(), transport=httpx.MockTransport(respond)
        ) as operations:
            async with SearchRuntime(settings(), operations) as runtime:
                result = await runtime.call("ragwell_search", {"query": "x"})
                if (
                    "generation_id"
                    in inspect.signature(RetrievalItemResponse).parameters
                ):
                    # Newer SDK contracts require the updated API before adoption.
                    assert result_data(result)["code"] == "invalid_response"
                else:
                    assert not result.is_error
                    assert result_data(result)["source_expansion_available"] is False
                    assert "generation_id" not in result_data(result)["matches"][0]
                result = await runtime.call("ragwell_fetch_source", source_arguments())
                assert result_data(result)["code"] == "source_reference_unavailable"
        assert len(calls) == 1

    asyncio.run(scenario())


@pytest.mark.parametrize(
    "field,value",
    [
        ("document_id", str(PROJECT_ID)),
        ("document_version_id", str(PROJECT_ID)),
        ("generation_id", str(PROJECT_ID)),
        ("source_id", str(PROJECT_ID)),
        ("start_offset", 1),
        ("end_offset", 2),
        ("next_offset", 10),
        ("character_count", 3),
        ("content", "secret-invalid-source"),
    ],
)
def test_source_identity_and_coordinates_are_checked(field: str, value: object) -> None:
    raw = source_body()
    raw[field] = value
    with pytest.raises(ValueError):
        project_source(
            DocumentSourcePreview.from_dict(raw),
            FetchSourceInput.model_validate(source_arguments()),
            project_id=PROJECT_ID,
            max_output_bytes=24000,
        )


def test_source_output_budget_returns_honest_continuation_coordinates() -> None:
    text = '😀\n"\\' * 800
    output = project_source(
        DocumentSourcePreview.from_dict(source_body(text=text)),
        FetchSourceInput.model_validate(source_arguments(limit=4000)),
        project_id=PROJECT_ID,
        max_output_bytes=2048,
    )
    data = result_data(output)
    assert result_bytes(output) <= 2048
    assert data["truncated"]
    assert text.startswith(data["content"])
    assert data["end_offset"] == data["next_offset"] == len(data["content"])
    assert data["character_count"] == len(text)


@pytest.mark.parametrize("offset,limit", [(0, 5), (4, 7), (29, 1)])
def test_valid_source_ranges_and_end_of_source(offset: int, limit: int) -> None:
    text = "Prefix and supporting quote. "
    assert len(text) == 29
    raw = source_body(text=text)
    end = min(len(text), offset + limit)
    raw.update(
        start_offset=offset,
        end_offset=end,
        content=text[offset:end],
        next_offset=end if end < len(text) else None,
    )
    output = project_source(
        DocumentSourcePreview.from_dict(raw),
        FetchSourceInput.model_validate(source_arguments(offset=offset, limit=limit)),
        project_id=PROJECT_ID,
        max_output_bytes=24000,
    )
    data = result_data(output)
    assert data["content"] == text[offset:end]
    assert data["start_offset"] == offset and data["end_offset"] == end
    assert data.get("next_offset") == raw["next_offset"]
    assert not data["truncated"]


def test_mcp_search_then_source_uses_only_published_sdk_and_fixed_project() -> None:
    async def scenario() -> None:
        calls: list[httpx.Request] = []

        def respond(request: httpx.Request) -> httpx.Response:
            calls.append(request)
            assert (
                request.headers["Authorization"] == "Bearer synthetic-test-credential"
            )
            if request.method == "POST":
                return httpx.Response(200, json=search_body())
            assert request.url.path == (
                f"/v1/projects/{PROJECT_ID}/documents/{DOCUMENT_ID}"
                f"/generations/{GENERATION_ID}/sources/{SOURCE_ID}"
            )
            assert dict(request.url.params) == {"offset": "0", "limit": "1500"}
            return httpx.Response(200, json=source_body())

        config = settings(max_searches=1)
        async with SdkOperations(
            config, transport=httpx.MockTransport(respond)
        ) as operations:
            async with Client(build_server(config, operations)) as client:
                listed = await client.list_tools()
                tool = listed.tools[1]
                assert tool.annotations is not None and tool.annotations.idempotent_hint
                assert tool.output_schema is not None
                assert "project_id" not in tool.input_schema["properties"]
                await client.call_tool("ragwell_search", {"query": "x"})
                result = await client.call_tool(
                    "ragwell_fetch_source", source_arguments()
                )
                assert not result.is_error
                jsonschema.validate(result_data(result), tool.output_schema)
                assert result_data(result)["generation_id"] == str(GENERATION_ID)
                assert result_data(result)["source_text_is_untrusted"]
        assert [request.method for request in calls] == ["POST", "GET"]

    asyncio.run(scenario())


@pytest.mark.parametrize(
    "status,expected",
    [
        (401, "authentication_failed"),
        (403, "access_denied"),
        (404, "source_unavailable"),
        (409, "source_unavailable"),
        (422, "request_rejected"),
    ],
)
def test_source_access_loss_and_deletion_fail_without_content(
    status: int, expected: str
) -> None:
    async def scenario() -> None:
        calls: list[httpx.Request] = []

        def respond(request: httpx.Request) -> httpx.Response:
            calls.append(request)
            if request.method == "POST":
                return httpx.Response(200, json=search_body())
            return httpx.Response(
                status, json={"error": {"code": "fixture", "message": "secret-raw"}}
            )

        async with SdkOperations(
            settings(), transport=httpx.MockTransport(respond)
        ) as operations:
            async with SearchRuntime(settings(), operations) as runtime:
                await runtime.call("ragwell_search", {"query": "x"})
                result = await runtime.call("ragwell_fetch_source", source_arguments())
                assert result_data(result)["code"] == expected
                assert not result_data(result)["usage_may_have_been_recorded"]
                assert "secret-raw" not in result.model_dump_json()
        assert len(calls) == 2

    asyncio.run(scenario())


def test_source_attempt_budget_is_independent_and_bounded() -> None:
    async def scenario() -> None:
        operations = FakeOperations()
        async with SearchRuntime(settings(max_searches=1), operations) as runtime:
            await runtime.call("ragwell_search", {"query": "x"})
            for _ in range(20):
                assert not (
                    await runtime.call("ragwell_fetch_source", source_arguments())
                ).is_error
            result = await runtime.call("ragwell_fetch_source", source_arguments())
            assert result_data(result)["code"] == "local_source_budget_exhausted"
            assert len(operations.source_requests) == 20
            assert len(operations.requests) == 1

    asyncio.run(scenario())


def test_source_cancellation_deadline_and_shared_admission() -> None:
    async def scenario() -> None:
        started = asyncio.Event()
        cancelled = asyncio.Event()

        class BlockingSource(FakeOperations):
            async def fetch_source(
                self, request: FetchSourceInput
            ) -> DocumentSourcePreview:
                started.set()
                try:
                    await asyncio.Event().wait()
                except asyncio.CancelledError:
                    cancelled.set()
                    raise
                raise AssertionError("unreachable")

        async with SearchRuntime(
            settings(timeout_seconds=0.05), BlockingSource()
        ) as runtime:
            await runtime.call("ragwell_search", {"query": "x"})
            task = asyncio.create_task(
                runtime.call("ragwell_fetch_source", source_arguments())
            )
            await started.wait()
            busy = await runtime.call("ragwell_search", {"query": "y"})
            assert result_data(busy)["code"] == "busy"
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            assert cancelled.is_set()
            timed_out = await runtime.call("ragwell_fetch_source", source_arguments())
            assert result_data(timed_out)["code"] == "source_timeout"
            assert not result_data(timed_out)["usage_may_have_been_recorded"]

    asyncio.run(scenario())
