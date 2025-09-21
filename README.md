# Metaso MCP Server

将 Metaso 搜索 API 封装为 MCP 协议服务，基于 Python 3.13 与 fastmcp 开发。支持 STDIO 与 HTTP(SSE) 两种传输。

## 环境要求
- Python 3.13
- 依赖安装：`pip install -r requirements.txt`
- 必需环境变量：`METASO_API_KEY`（你的 Metaso API 密钥）
- 可选环境变量：
  - `METASO_BASE_URL`（默认 `https://metaso.cn`）
  - `METASO_REQUEST_TIMEOUT`（默认 `15.0` 秒）

## 启动方式
- STDIO（适合本机 MCP 客户端直连）：
  - `export METASO_API_KEY="<你的Key>"`
  - `python3 src/metaso_mcp/app.py`
- SSE（HTTP 方式，默认端口 80，可自定义端口/路径）：
  - `export METASO_API_KEY="<你的Key>"`
  - `python3 mcp-sse.py --host 0.0.0.0 --port 8080 --path /sse --keepalive 300`
  - 日志会显示服务 URL，例如：`http://127.0.0.1:8080/sse/`

- 无状态/函数计算（推荐使用 Streamable HTTP 以避免 SSE 会话丢失）：
  - `export METASO_API_KEY="<你的Key>"`
  - `python3 serve.py --transport streamable-http --host 0.0.0.0 --port 8080 --path /mcp --keepalive 300`
  - 也可通过环境变量切换：`METASO_TRANSPORT=streamable-http python3 serve.py`

提示：SSE 客户端访问时请使用带尾斜杠的路径（如 `/sse/`）以避免 307 重定向。函数计算场景建议改用 `streamable-http`。

## 部署到函数计算（阿里云 FC）建议
- 打包瘦身：
  - 本仓库提供了瘦身脚本与 Makefile 任务，自动清理 `__pycache__`、`*.dist-info`、`tests/`、`docs/` 等不影响运行的文件。
  - 本地构建压缩包：
    - `make fc-zip`
    - 产物为 `dist.zip`，可直接上传到 FC 作为代码包。
- 运行入口：
  - 推荐 `python3 serve.py --transport streamable-http --host 0.0.0.0 --port 9000 --path /mcp`
  - 或使用环境变量：`METASO_TRANSPORT=streamable-http METASO_PORT=9000 METASO_PATH=/mcp`
- 实例设置：
  - 若坚持 SSE，请将实例并发设为 1、保持最小实例 ≥ 1，并开启会话粘滞，否则会出现 `Could not find session`。

## 端点说明（SSE）
- SSE 流：`GET /<path>/`（默认 `/sse/`）
- 消息提交：`POST /messages/?session_id=<服务端下发的session_id>`
- 客户端流程：先连接 SSE，收到首条 `endpoint` 事件后，按其中的 `session_id` 将 JSON-RPC 消息 POST 到 `/messages/`。
  大多数 MCP 客户端会自动完成此握手，通常无需手动构造请求。

## 工具（Tools）
- `metaso_search`
  - 参数：`query`(必填)、`scope`(默认 `webpage`)、`size`(1–50)、`include_summary`、`include_raw_content`、`concise_snippet`
  - 返回：Metaso 原始 JSON 响应

## 代理/网关稳定性建议
- 反向代理需关闭缓冲并延长读超时（Nginx 示例）：
  - `proxy_buffering off;`
  - `proxy_read_timeout 1h;`
  - `proxy_http_version 1.1;`
- 启动时适当调大 `--keepalive`（如 300–600）以降低空闲断连概率。
