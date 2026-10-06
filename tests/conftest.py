import pytest

from flythings import BaseClient, ServerConfig


@pytest.fixture(autouse=True)
def reset_headers(monkeypatch):
    # BaseClient.headers is class-level state shared by every module instance
    monkeypatch.setattr(BaseClient, "headers", {"x-auth-token": "", "Content-Type": "application/json"})


@pytest.fixture
def config():
    return ServerConfig(server="beta.flythings.io/api", foi="device", procedure="sensor")
