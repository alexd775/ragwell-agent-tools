from __future__ import annotations

import asyncio
from typing import Any

import httpx
import jsonschema
import pytest
from mcp import Client
from pydantic import ValidationError as ModelValidationError
from ragwell.types import DocumentSourcePreview, SearchResponse

from ragwell_agent_tools.operations import FetchSourceInput, SearchInput
from ragwell_agent_tools.sdk_operations import SdkOperations
from ragwell_agent_tools.tools import SearchRuntime, build_server

from .helpers import PROJECT_ID, FakeOperations, result_data, search_body, settings


@pytest.mark.parametrize(
    "arguments",
    [
        {"query": ""},
        {"query": "  "},
        {"query": "q" * 2001},
        {"query": "x", "k": 6},
        {"query": "x", "k": True},
        {"query": "x", "k": "3"},
        {"query": "x", "project_id": "foreign"},
        {"query": "x", "filters": {"tenant_id": "foreign"}},
        {"query": ["x"]},
    ],
)
def test_invalid_input_does_not_dispatch(arguments: dict[str, Any]) -> None:
    async def scenario() -> None:
        operations = FakeOperations()
        async with SearchRuntime(settings(), operations) as runtime:
            result = await runtime.call("ragwell_search", arguments)
            assert result.is_error
            assert result_data(result)["code"] == "invalid_arguments"
            assert not operations.requests

    asyncio.run(scenario())


def test_validation_does_not_echo_query() -> None:
    with pytest.raises(ModelValidationError) as error:
        SearchInput.model_validate({"query": "sensitive-value", "k": 9})
    assert "sensitive-value" not in str(error.value)


@pytest.mark.parametrize(
    "status,expected",
    [
        (401, "authentication_failed"),
        (403, "access_denied"),
        (404, "project_unavailable"),
        (429, "rate_limited"),
        (500, "api_unavailable"),
        (503, "api_unavailable"),
    ],
)
def test_http_errors_are_sanitized_and_search_is_never_replayed(
    status: int, expected: str
) -> None:
    async def scenario() -> None:
        calls: list[httpx.Request] = []
        config = settings()

        def respond(request: httpx.Request) -> httpx.Response:
            calls.append(request)
            assert request.url.path == f"/v1/projects/{PROJECT_ID}/search"
            assert request.headers["Authorization"] == f"Bearer {config.api_key}"
            return httpx.Response(
                status,
                json={
                    "error": {
                        "code": "raw-provider-code",
                        "message": "sensitive-provider-value",
                    }
                },
                headers={"Retry-After": "2", "X-Request-ID": str(PROJECT_ID)},
            )

        async with SdkOperations(
            config, transport=httpx.MockTransport(respond)
        ) as operations:
            async with SearchRuntime(config, operations) as runtime:
                result = await runtime.call(
                    "ragwell_search", {"query": "private query"}
                )
        assert len(calls) == 1
        data = result_data(result)
        assert data["code"] == expected
        assert data["request_id"] == str(PROJECT_ID)
        assert data["retry_after_seconds"] == 2
        assert "sensitive-provider-value" not in result.model_dump_json()
        assert "private query" not in result.model_dump_json()
        assert config.api_key not in result.model_dump_json()

    asyncio.run(scenario())


def test_local_budget_counts_attempts_without_replaying_failures() -> None:
    async def scenario() -> None:
        operations = FakeOperations()
        operations.error = RuntimeError("secret failure value")
        async with SearchRuntime(settings(max_searches=1), operations) as runtime:
            first = await runtime.call("ragwell_search", {"query": "x"})
            second = await runtime.call("ragwell_search", {"query": "x"})
        assert result_data(first)["code"] == "search_failed"
        assert "secret failure value" not in first.model_dump_json()
        assert result_data(second)["code"] == "local_budget_exhausted"
        assert len(operations.requests) == 1

    asyncio.run(scenario())


def test_cancellation_busy_and_deadline_release_owned_admission() -> None:
    async def scenario() -> None:
        started = asyncio.Event()
        cancelled = asyncio.Event()

        class BlockingOperations:
            async def fetch_source(
                self, request: FetchSourceInput
            ) -> DocumentSourcePreview:
                raise AssertionError("unexpected source read")

            async def search(self, request: SearchInput) -> SearchResponse:
                started.set()
                try:
                    await asyncio.Event().wait()
                except asyncio.CancelledError:
                    cancelled.set()
                    raise
                raise AssertionError("unreachable")

        async with SearchRuntime(
            settings(timeout_seconds=0.05), BlockingOperations()
        ) as runtime:
            task = asyncio.create_task(runtime.call("ragwell_search", {"query": "x"}))
            await started.wait()
            busy = await runtime.call("ragwell_search", {"query": "y"})
            assert result_data(busy)["code"] == "busy"
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            assert cancelled.is_set()
            timed_out = await runtime.call("ragwell_search", {"query": "z"})
            assert result_data(timed_out)["code"] == "search_timeout"
            assert result_data(timed_out)["usage_may_have_been_recorded"]

    asyncio.run(scenario())


def test_mcp_client_discovers_only_curated_tool_and_receives_evidence() -> None:
    async def scenario() -> None:
        operations = FakeOperations()
        async with Client(build_server(settings(), operations)) as client:
            listed = await client.list_tools()
            assert [tool.name for tool in listed.tools] == [
                "ragwell_search",
                "ragwell_fetch_source",
            ]
            tool = listed.tools[0]
            assert tool.input_schema["additionalProperties"] is False
            assert "project_id" not in tool.input_schema["properties"]
            assert tool.annotations is not None
            assert tool.annotations.read_only_hint
            assert tool.annotations.idempotent_hint is False
            result = await client.call_tool(
                "ragwell_search", {"query": "travel approval", "k": 1}
            )
            assert not result.is_error
            assert tool.output_schema is not None
            jsonschema.Draft202012Validator.check_schema(tool.output_schema)
            jsonschema.validate(result_data(result), tool.output_schema)
            assert result_data(result)["matches"][0]["parts"][2]["start_line"] == 3
            denied = await client.call_tool(
                "ragwell_search", {"query": "x", "tenant_id": "other"}
            )
            assert denied.is_error
            jsonschema.validate(result_data(denied), tool.output_schema)
            unknown = await client.call_tool("ragwell_delete", {"document_id": "other"})
            assert unknown.is_error
        assert len(operations.requests) == 1

    asyncio.run(scenario())


def test_invalid_upstream_shape_never_discloses_raw_content() -> None:
    async def scenario() -> None:
        raw = search_body()
        raw["items"][0]["citation"] = {"sensitive-value": "not a citation"}
        operations = FakeOperations(SearchResponse.from_dict(raw))
        async with SearchRuntime(settings(), operations) as runtime:
            result = await runtime.call("ragwell_search", {"query": "x"})
        assert result_data(result)["code"] == "invalid_response"
        assert "sensitive-value" not in result.model_dump_json()

    asyncio.run(scenario())
