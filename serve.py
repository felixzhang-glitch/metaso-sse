"""Unified runner for Metaso MCP server.

Provides both SSE and Streamable-HTTP transports. In无状态(如函数计算/FC)环境，
推荐使用 `streamable-http` 以避免跨实例丢失会话导致的 404（Could not find session）。
"""

from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path

# Ensure `src` is on sys.path for script execution
ROOT = Path(__file__).resolve().parent / "src"
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))

from metaso_mcp.app import app


def default_transport() -> str:
    """Choose default transport based on environment.

    - 在阿里云函数/无服务器环境中自动使用 `streamable-http`。
    - 其他场景默认 `sse`。
    可通过 METASO_TRANSPORT/--transport 覆盖。
    """

    for key in (
        "FC_FUNCTION_NAME",  # Aliyun Function Compute
        "K_SERVICE",  # Cloud Run
        "AWS_LAMBDA_FUNCTION_NAME",  # Lambda
    ):
        if os.getenv(key):
            return "streamable-http"
    return "sse"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Metaso MCP server")
    parser.add_argument(
        "--transport",
        choices=["sse", "http", "streamable-http"],
        default=os.getenv("METASO_TRANSPORT", default_transport()),
        help="传输协议，函数计算等无状态环境推荐 streamable-http",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("METASO_HOST", "0.0.0.0"),
        help="监听地址，默认 0.0.0.0",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("METASO_PORT", "80")),
        help="监听端口，默认 80",
    )
    parser.add_argument(
        "--path",
        default=os.getenv("METASO_PATH"),
        help="服务路径；SSE 默认 /sse，streamable-http 默认 /mcp",
    )
    parser.add_argument(
        "--keepalive",
        type=int,
        default=int(os.getenv("METASO_KEEPALIVE", "300")),
        help="uvicorn HTTP keep-alive 超时（秒）",
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("METASO_LOG_LEVEL", "INFO"),
        help="日志级别（DEBUG/INFO/WARNING/ERROR）",
    )
    return parser.parse_args()


async def run_http(transport: str, host: str, port: int, path: str, keepalive: int, log_level: str) -> None:
    await app.run_http_async(
        transport=transport,
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
    path = args.path
    if not path:
        path = "/sse" if args.transport == "sse" else "/mcp"
    asyncio.run(run_http(args.transport, args.host, args.port, path, args.keepalive, args.log_level))


if __name__ == "__main__":  # pragma: no cover
    main()

