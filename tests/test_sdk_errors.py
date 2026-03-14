from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from openweather_sdk.exceptions import (
    APIKeyInvalidError,
    CityNotFoundError,
    InvalidCoordinatesError,
    InvalidInputError,
    NoWeatherDataError,
    OpenWeatherAPIError,
    RateLimitExceededError,
    RequestTimeoutError,
)

client = TestClient(app)

VALID_PARAMS = "?city=London"


class TestSDKExceptions:
    """Testes de mapeamento excecao do SDK para status HTTP."""

    @patch("app.core.service.get_weather")
    def test_city_not_found_returns_404(self, mock_service):
        """CityNotFoundError deve retornar 404."""
        mock_service.side_effect = CityNotFoundError()
        response = client.get(f"/weather{VALID_PARAMS}")
        assert response.status_code == 404

    @patch("app.core.service.get_weather")
    def test_invalid_coordinates_returns_422(self, mock_service):
        """InvalidCoordinatesError deve retornar 422."""
        mock_service.side_effect = InvalidCoordinatesError()
        response = client.get("/weather?lat=999&lon=999")
        assert response.status_code == 422

    @patch("app.core.service.get_weather")
    def test_invalid_input_returns_422(self, mock_service):
        """InvalidInputError deve retornar 422."""
        mock_service.side_effect = InvalidInputError()
        response = client.get(f"/weather{VALID_PARAMS}")
        assert response.status_code == 422

    @patch("app.core.service.get_weather")
    def test_no_weather_data_returns_404(self, mock_service):
        """NoWeatherDataError deve retornar 404."""
        mock_service.side_effect = NoWeatherDataError()
        response = client.get("/weather?lat=0&lon=0")
        assert response.status_code == 404

    @patch("app.core.service.get_weather")
    def test_api_key_invalid_returns_500(self, mock_service):
        """APIKeyInvalidError deve retornar 500 (erro de config do servidor)."""
        mock_service.side_effect = APIKeyInvalidError()
        response = client.get(f"/weather{VALID_PARAMS}")
        assert response.status_code == 500

    @patch("app.core.service.get_weather")
    def test_sdk_api_error_returns_502(self, mock_service):
        """OpenWeatherAPIError deve retornar 502."""
        mock_service.side_effect = OpenWeatherAPIError()
        response = client.get(f"/weather{VALID_PARAMS}")
        assert response.status_code == 502

    @patch("app.core.service.get_weather")
    def test_sdk_rate_limit_returns_429(self, mock_service):
        """RateLimitExceededError deve retornar 429."""
        mock_service.side_effect = RateLimitExceededError()
        response = client.get(f"/weather{VALID_PARAMS}")
        assert response.status_code == 429

    @patch("app.core.service.get_weather")
    def test_sdk_timeout_returns_504(self, mock_service):
        """RequestTimeoutError deve retornar 504."""
        mock_service.side_effect = RequestTimeoutError()
        response = client.get(f"/weather{VALID_PARAMS}")
        assert response.status_code == 504


class TestSDKUnavailable:
    """Teste de indisponibilidade generica do SDK."""

    @patch("app.core.service.get_weather")
    def test_generic_exception_returns_503(self, mock_service):
        """Excecao inesperada deve retornar 503 servico indisponivel."""
        mock_service.side_effect = Exception("conexao recusada")
        response = client.get("/weather?city=London")
        assert response.status_code == 503
        assert "indisponivel" in response.json()["detail"].lower()
