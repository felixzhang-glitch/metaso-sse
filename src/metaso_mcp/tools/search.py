from __future__ import annotations

from typing import Any, Annotated

from fastmcp.server import Context, FastMCP
from pydantic import Field

from ..clients.metaso import MetasoClient

DEFAULT_SCOPE = "webpage"
MAX_RESULTS = 50

QueryParam = Annotated[str, Field(description="自然语言搜索关键词", min_length=1)]
ScopeParam = Annotated[
    str,
    Field(
        description="Metaso 搜索范围 (如 webpage、weibo、zhihu)",
        examples=[DEFAULT_SCOPE],
        min_length=1,
    ),
]
SizeParam = Annotated[
    int,
    Field(
        description="返回的结果数量 (1-50)",
        ge=1,
        le=MAX_RESULTS,
    ),
]
IncludeSummaryParam = Annotated[
    bool,
    Field(description="是否请求 Metaso 返回 summary 字段"),
]
IncludeRawParam = Annotated[
    bool,
    Field(description="是否包含原始内容字段"),
]
ConciseSnippetParam = Annotated[
    bool,
    Field(description="是否使用精简片段输出"),
]


def register_search_tool(app: FastMCP, client: MetasoClient) -> None:
    """Register the Metaso search tool with the given FastMCP application."""

    @app.tool(
        name="metaso_search",
        description="查询 Metaso 搜索 API，返回原始 JSON 结果。",
        tags={"search", "metaso"},
    )
    async def metaso_search(
        query: QueryParam,
        scope: ScopeParam = DEFAULT_SCOPE,
        size: SizeParam = 10,
        include_summary: IncludeSummaryParam = False,
        include_raw_content: IncludeRawParam = False,
        concise_snippet: ConciseSnippetParam = False,
        context: Context | None = None,
    ) -> dict[str, Any]:
        if context:
            context.log(
                f"Running Metaso search query={query!r} scope={scope!r} size={size}",
            )

        results = await client.search(
            query=query,
            scope=scope,
            size=size,
            include_summary=include_summary,
            include_raw_content=include_raw_content,
            concise_snippet=concise_snippet,
        )

        if context:
            hits = results.get("data") or results.get("items") or []
            count = len(hits) if isinstance(hits, list) else 0
            context.log(f"Metaso returned {count} items.")

        return results

    return None


__all__ = ["register_search_tool"]
