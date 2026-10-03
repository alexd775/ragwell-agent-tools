"""Synthetic HTTP contract fixtures; no backend checkout or customer data."""

from __future__ import annotations

import os
from typing import Any
from uuid import UUID

from mcp.types import CallToolResult
from ragwell.types import (
    DocumentSourcePreview,
    MachineCapabilitiesResponse,
    SearchResponse,
)

from ragwell_agent_tools.operations import FetchSourceInput, SearchInput
from ragwell_agent_tools.settings import Settings

PROJECT_ID = UUID(int=1)
DOCUMENT_ID = UUID(int=2)
VERSION_ID = UUID(int=3)
CHUNK_ID = UUID(int=4)
SOURCE_ID = UUID(int=5)
RETRIEVAL_ID = UUID(int=6)
GENERATION_ID = UUID(int=7)


def platform_environment(**values: str) -> dict[str, str]:
    """Minimal subprocess environment; Windows Python cannot start without these."""
    inherited = {
        name: os.environ[name]
        for name in ("SYSTEMROOT", "WINDIR")
        if name in os.environ
    }
    return {**inherited, **values}


def settings(**overrides: Any) -> Settings:
    return Settings(
        **{
            "base_url": "https://example.invalid",
            "project_id": PROJECT_ID,
            "api_key": "synthetic-test-credential",
            **overrides,
        }
    )


def search_body(
    *, text: str = "Ask your manager before booking travel."
) -> dict[str, Any]:
    return {
        "retrieval_id": str(RETRIEVAL_ID),
        "retrieval_version": "hybrid-v1",
        "profile_id": None,
        "items": [
            {
                "rank": 1,
                "chunk_id": str(CHUNK_ID),
                "document_id": str(DOCUMENT_ID),
                "document_version_id": str(VERSION_ID),
                "generation_id": str(GENERATION_ID),
                "source_filename": "travel-policy.md",
                "content": text,
                "representation_version": "source-parts-v1",
                "citation": None,
                "scores": {"final": 0.7, "text": 0.3, "vector": 0.9, "hybrid": 0.7},
                "parts": [
                    {"kind": "context", "text": "Travel policy"},
                    {"kind": "separator", "text": "\n"},
                    {
                        "kind": "evidence",
                        "text": text,
                        "source_id": str(SOURCE_ID),
                        "page_number": None,
                        "start_line": 3,
                        "end_line": 3,
                        "span": {
                            "source_ordinal": 0,
                            "start_offset": 18,
                            "end_offset": 73,
                        },
                    },
                ],
            }
        ],
    }


def result_data(result: CallToolResult) -> dict[str, Any]:
    assert isinstance(result.structured_content, dict)
    return result.structured_content


class FakeOperations:
    def __init__(self, response: SearchResponse | None = None) -> None:
        self.response = response or SearchResponse.from_dict(search_body())
        self.requests: list[SearchInput] = []
        self.error: Exception | None = None
        self.source_requests: list[FetchSourceInput] = []
        self.capability_response = MachineCapabilitiesResponse.from_dict(
            capabilities_body()
        )
        self.capability_error: Exception | None = None
        self.capability_calls = 0

    async def capabilities(self) -> MachineCapabilitiesResponse:
        self.capability_calls += 1
        if self.capability_error is not None:
            raise self.capability_error
        return self.capability_response

    async def search(self, request: SearchInput) -> SearchResponse:
        self.requests.append(request)
        if self.error is not None:
            raise self.error
        return self.response

    async def fetch_source(self, request: FetchSourceInput) -> DocumentSourcePreview:
        self.source_requests.append(request)
        if self.error is not None:
            raise self.error
        return DocumentSourcePreview.from_dict(source_body())


def source_body(*, text: str = "A source passage.") -> dict[str, Any]:
    return {
        "document_id": str(DOCUMENT_ID),
        "document_version_id": str(VERSION_ID),
        "generation_id": str(GENERATION_ID),
        "source_id": str(SOURCE_ID),
        "coordinate_kind": "text",
        "source_ordinal": 0,
        "page_number": None,
        "character_count": len(text),
        "start_offset": 0,
        "end_offset": len(text),
        "content": text,
        "next_offset": None,
    }


def source_arguments(**overrides: Any) -> dict[str, Any]:
    return {
        "document_id": str(DOCUMENT_ID),
        "document_version_id": str(VERSION_ID),
        "generation_id": str(GENERATION_ID),
        "source_id": str(SOURCE_ID),
        **overrides,
    }


def capabilities_body(
    *, project_id: UUID = PROJECT_ID, scopes: list[str] | None = None
) -> dict[str, Any]:
    return {
        "projects": [
            {
                "project_id": str(project_id),
                "scopes": scopes
                if scopes is not None
                else ["document:read", "retrieval:search"],
            }
        ]
    }
