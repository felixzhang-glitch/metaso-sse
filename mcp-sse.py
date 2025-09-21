"""Run Metaso MCP server over SSE transport.

Notes on stability:
- 默认会通过 sse-starlette 的心跳（ping=15s）保持连接，但代理/防火墙仍可能在空闲时断开。
- 可通过 --keepalive 调整 uvicorn 的 HTTP keep-alive 超时，减少女连接空闲被关闭的概率。
- 建议客户端始终使用准确路径（例如 /sse/），避免 307 重定向。
"""

from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent / 'src'
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))

from metaso_mcp.app import app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--host",
        default=os.getenv("METASO_SSE_HOST", "0.0.0.0"),
        help="SSE 监听地址，默认 0.0.0.0",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("METASO_SSE_PORT", "80")),
        help="SSE 监听端口，默认 80",
    )
    parser.add_argument(
        "--path",
        default=os.getenv("METASO_SSE_PATH", "/sse"),
        help="SSE 路径，默认 /sse（注意客户端可访问 /sse/，避免 307 重定向）",
    )
    parser.add_argument(
        "--keepalive",
        type=int,
        default=int(os.getenv("METASO_SSE_KEEPALIVE", "120")),
        help="uvicorn HTTP keep-alive 超时（秒），默认 120",
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("METASO_SSE_LOG_LEVEL", "INFO"),
        help="日志级别（DEBUG/INFO/WARNING/ERROR），默认 INFO",
    )
    return parser.parse_args()


async def serve_sse(host: str, port: int, path: str, keepalive: int, log_level: str) -> None:
    await app.run_http_async(
        transport="sse",
        host=host,
        port=port,
        path=path,
        log_level=log_level,
        uvicorn_config={
            "timeout_keep_alive": keepalive,
            "proxy_headers": True,
            "forwarded_allow_ips": "*",
        },
    )


def main() -> None:
    args = parse_args()
    asyncio.run(serve_sse(args.host, args.port, args.path, args.keepalive, args.log_level))


if __name__ == "__main__":  # pragma: no cover
    main()
