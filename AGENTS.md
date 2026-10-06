# AGENTS.md

Python client library for the FlyThings IoT platform, published to PyPI as `flythings`.

## Layout

- `src/flythings/`: the package. `BaseClient` (`base_client.py`) holds auth, server and socket handling; each feature area is a subclass in `modules/` (insertion, realtime, action, prediction, sos, util). `paths.py` holds the API endpoints, `config.py` the `ServerConfig` dataclass.
- `tests/`: offline pytest suite. Test files must be named `*_test.py` (enforced by pre-commit). Never hit the network; mock `requests` instead.
- `examples/`: manual script against a live server. Only placeholders may be committed there.
- `docs/`: per-module API reference in Markdown. Keep it in sync when public methods change.

## Commands

- `uv sync`: create `.venv` with dev dependencies.
- `uv run pytest`: run tests with coverage.
- `uv run ruff check` / `uv run ruff format`: lint and format.
- `uv build`: build sdist and wheel.

## Conventions

- Inside the package, import from the defining module (`from flythings.config import ServerConfig`), never from `flythings` itself: importing from the package while `__init__.py` is still running causes circular-import errors whenever the imports there get re-sorted.
- `BaseClient.headers` is class-level state shared by every module instance (a login on one module authenticates all of them). Tests reset it through the autouse fixture in `tests/conftest.py`.
- Commits follow Conventional Commits; the version is managed by commitizen from `pyproject.toml` only. Release tags have no `v` prefix.
- Do not hard-wrap prose in Markdown files.
