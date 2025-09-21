# Repository Guidelines

## Project Structure & Module Organization
- Place Python sources in `src/metaso_mcp/`; group reusable clients under `clients/` and FastMCP tool handlers under `tools/`.
- Keep FastAPI/FastMCP app wiring in `src/metaso_mcp/app.py`; isolate token or transport helpers in `core/` to simplify reuse.
- Store contract fixtures and example payloads in `assets/`, and integration or regression tests in `tests/` with mirrors of the package layout.
- Use `scripts/` for utility runners (refreshing schemas, lint pipelines) and keep generated OpenAPI/MCP specs out of version control unless curated.

## Build, Test, and Development Commands
- `uv pip install -r requirements.txt` installs the Python 3.13 toolchain; run after cloning or updating dependencies.
- `fastmcp run src/metaso_mcp/app.py` starts the MCP server locally; pass `--reload` while iterating on handlers.
- `pytest` executes the unit and contract test suites; append `--maxfail=1 --disable-warnings` for quick validation before pushing.
- `ruff check src tests` performs linting; add `ruff format` to auto-apply formatting fixes.

## Coding Style & Naming Conventions
- Target Python 3.13 features but guard optional syntax with feature flags when possible.
- Follow Black/PEP8 defaults (4-space indent, 88-char lines) and rely on `ruff format` for consistency.
- Name FastMCP tools as verbs (`search_web`, `fetch_snapshot`) and align module names with the Metaso endpoint they wrap.
- Keep async call sites explicit; prefer `async`/`await` over background threads to match FastMCP expectations.

## Testing Guidelines
- Author tests with `pytest` and `httpx`'s async client; isolate Metaso API calls behind a mockable interface.
- Mirror file names (`tools/search.py` -> `tests/tools/test_search.py`) and mark integration suites with `@pytest.mark.integration`.
- Maintain ≥85% statement coverage via `pytest --cov=src/metaso_mcp`; document uncovered paths in PRs.

## Commit & Pull Request Guidelines
- With no baseline history, adopt Conventional Commits (`feat:`, `fix:`) and keep subjects ≤72 characters.
- Reference Metaso issue IDs or task tickets in the body and list notable FastMCP schema changes under bullet points.
- PRs should link to design notes, include test results (command + outcome), and attach sample MCP interaction logs when behavior changes.

## Security & Configuration Tips
- Store API keys in `.env.local` using `METASO_API_KEY`; never commit secrets or bearer tokens.
- Document new environment variables in `docs/configuration.md` and provide safe defaults or stubs for CI.
