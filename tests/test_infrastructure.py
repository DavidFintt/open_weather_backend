from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestInfrastructure:
    """Testes de infraestrutura: health check."""

    def test_health_check_returns_200(self):
        """GET /health deve retornar 200 com status ok."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
