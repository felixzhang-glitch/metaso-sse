from __future__ import annotations

from typing import Any, Dict, Optional

import httpx
from fastmcp import exceptions


class MetasoClient:
    """Thin async wrapper around the Metaso search API."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout: float = 15.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = httpx.Timeout(timeout)

    async def search(
        self,
        *,
        query: str,
        scope: str = "webpage",
        size: int = 10,
        include_summary: bool = False,
        include_raw_content: bool = False,
        concise_snippet: bool = False,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a search query and return the raw Metaso payload."""

        payload: Dict[str, Any] = {
            "q": query,
            "scope": scope,
            "includeSummary": include_summary,
            "size": str(size),
            "includeRawContent": include_raw_content,
            "conciseSnippet": concise_snippet,
        }
        if extra_params:
            payload.update(extra_params)

        async with httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=self._timeout,
        ) as client:
            try:
                response = await client.post("/api/v1/search", json=payload)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                detail = self._format_error(exc)
                raise exceptions.ToolError(detail) from exc
            except httpx.HTTPError as exc:
                raise exceptions.ToolError(f"Metaso request failed: {exc}") from exc
            return response.json()

    @staticmethod
    def _format_error(exc: httpx.HTTPStatusError) -> str:
        status = exc.response.status_code
        try:
            data = exc.response.json()
        except ValueError:
            data = exc.response.text
        return f"Metaso API error {status}: {data}"


__all__ = ["MetasoClient"]
