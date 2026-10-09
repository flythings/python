# AGENTS.md

Python client library for the FlyThings IoT platform, published to PyPI as `flythings`.

## Layout

- `src/flythings/`: the package. `client.py` holds `FlyThings` (shared `requests.Session`, default `Connection`, `request()`, API factories, config file, `close`). `connection.py` holds `Connection` and `Secret` (tokens hidden from `repr`/`str`), `series.py` holds `Series`/`Observation`, `schemas.py` the `TypedDict`s for every known JSON shape, `errors.py` the exceptions, `_sockets.py` TCP/UDP socket opening, and `paths.py` the API endpoints. Each feature area is a plain class in `apis/` (insertion, query, realtime, actions, sos, util) taking `(client, connection)`.
- `tests/`: offline pytest suite. Test files must be named `*_test.py` (enforced by pre-commit). Never hit the network; mock `requests` instead.
- `examples/`: manual script against a live server. Only placeholders may be committed there.
- `docs/`: API reference in Markdown, one page per API plus `Client.md` and `Migration.md`. Keep it in sync when public methods change.

## Commands

- `uv sync`: create `.venv` with dev dependencies.
- `uv run pytest`: run tests with coverage.
- `uv run ruff check` / `uv run ruff format`: lint and format.
- `pyrefly check` / `basedpyright --pythonpath .venv/bin/python`: type check (both are uv tools, not dev dependencies).
- `uv build`: build sdist and wheel.

## Conventions

- Inside the package, import from the defining module (`from flythings.connection import Connection`), never from `flythings` itself: importing from the package while `__init__.py` is still running causes circular-import errors whenever the imports there get re-sorted.
- API classes never inherit from the client and hold no shared or class-level state: they call `client.request(..., connection=...)`. A client works against one `Connection`; multi-server or multi-user routing belongs to the caller, which creates one client per connection. Stateful APIs (real-time, actions) are added to `FlyThings._closeables` by their factory so `close()` stops them.
- Errors raise (`flythings.errors`); never `print` or return status codes. Log through `logging.getLogger(__name__)`.
- Typing: Python 3.10 floor; the dependencies are `requests` and `typing_extensions`. No `from __future__ import annotations`. Use a `TypedDict` in `schemas.py` for every JSON shape whose structure is known, with `TypedDict` and `NotRequired` imported from `typing_extensions` for optional keys; keep `JsonValue`/`dict[str, Any]` for unknown shapes only. Import `Self` from `typing_extensions` for methods that return their own instance. Quote only names that would create an import cycle (`"FlyThings"` under `TYPE_CHECKING`) or a class's own name.
- Tests use the `session`, `client`, `respond`, `sent_json` and `fake_socket` fixtures from `tests/conftest.py`; an autouse fixture makes any real socket connection raise.
- Commits follow Conventional Commits; the version is managed by commitizen from `pyproject.toml` only. Release tags have no `v` prefix.
- Do not hard-wrap prose in Markdown files.
