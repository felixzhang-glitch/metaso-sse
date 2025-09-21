from __future__ import annotations

from pathlib import Path

if __package__ in (None, ""):
    import sys

    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from metaso_mcp.clients.metaso import MetasoClient  # type: ignore
    from metaso_mcp.core.settings import get_settings  # type: ignore
    from metaso_mcp.tools.search import register_search_tool  # type: ignore
else:  # pragma: no cover - exercised via package imports
    from .clients.metaso import MetasoClient
    from .core.settings import get_settings
    from .tools.search import register_search_tool

from fastmcp.server import FastMCP
from pydantic import ValidationError

app = FastMCP("metaso-search", version="0.1.0")

try:
    settings = get_settings()
except ValidationError as exc:
    raise RuntimeError(
        "Failed to load settings. Ensure METASO_API_KEY is set in the environment or .env.local."
    ) from exc

client = MetasoClient(
    base_url=str(settings.base_url),
    api_key=settings.api_key,
    timeout=settings.request_timeout,
)

register_search_tool(app, client)


def main() -> None:
    """Entry point for running the FastMCP server via stdio."""

    app.run()


if __name__ == "__main__":  # pragma: no cover
    main()
