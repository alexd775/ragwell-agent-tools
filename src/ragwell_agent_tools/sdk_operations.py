"""Published SDK adapter with explicit ownership and no additional retries."""

from __future__ import annotations

from types import TracebackType

import httpx
from ragwell import AsyncRagwell
from ragwell.types import (
    DocumentSourcePreview,
    MachineCapabilitiesResponse,
    SearchResponse,
)

from .operations import FetchSourceInput, SearchInput
from .settings import Settings


class SdkOperations:
    def __init__(
        self, settings: Settings, *, transport: httpx.AsyncBaseTransport | None = None
    ) -> None:
        self._client = AsyncRagwell(
            base_url=settings.base_url,
            api_key=settings.api_key,
            operation_timeout=settings.timeout_seconds,
            transport=transport,
        )
        self._project = self._client.project(settings.project_id)

    async def capabilities(self) -> MachineCapabilitiesResponse:
        return await self._client.capabilities.get()

    async def search(self, request: SearchInput) -> SearchResponse:
        return await self._project.search(query=request.query, k=request.k)

    async def fetch_source(self, request: FetchSourceInput) -> DocumentSourcePreview:
        return await self._project.documents.sources.get(
            request.document_id,
            request.generation_id,
            request.source_id,
            offset=request.offset,
            limit=request.limit,
        )

    async def __aenter__(self) -> SdkOperations:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self._client.aclose()
