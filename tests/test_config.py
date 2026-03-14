from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestConfigMiddleware:
    """Testes de validacao de configuracao via middleware (fail fast)."""

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_api_key_returns_500(self):
        """OPENWEATHER_API_KEY ausente deve retornar 500."""
        response = client.get("/weather?city=London")
        assert response.status_code == 500
        assert "OPENWEATHER_API_KEY" in response.json()["detail"]

    @patch.dict("os.environ", {"OPENWEATHER_API_KEY": "key123"}, clear=True)
    def test_missing_github_token_returns_500(self):
        """GITHUB_TOKEN ausente deve retornar 500."""
        response = client.get("/weather?city=London")
        assert response.status_code == 500
        assert "GITHUB_TOKEN" in response.json()["detail"]

    @patch.dict("os.environ", {"OPENWEATHER_API_KEY": "key123", "GITHUB_TOKEN": "tok"}, clear=True)
    def test_missing_gist_id_returns_500(self):
        """GIST_ID ausente deve retornar 500."""
        response = client.get("/weather?city=London")
        assert response.status_code == 500
        assert "GIST_ID" in response.json()["detail"]

    @patch.dict("os.environ", {"GIST_ID": "abc123"}, clear=True)
    def test_missing_multiple_config_returns_500(self):
        """Multiplas variaveis ausentes devem aparecer na mensagem."""
        response = client.get("/weather?city=London")
        assert response.status_code == 500
        detail = response.json()["detail"]
        assert "OPENWEATHER_API_KEY" in detail
        assert "GITHUB_TOKEN" in detail

    @patch.dict("os.environ", {}, clear=True)
    def test_health_bypasses_middleware(self):
        """GET /health nao e bloqueado pelo middleware mesmo sem config."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
