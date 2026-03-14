import pytest


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    """Garante que as variaveis de ambiente existem para o middleware nao bloquear."""
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-key")
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setenv("GIST_ID", "test-gist-id")
