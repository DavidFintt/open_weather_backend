from dataclasses import asdict
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from openweather_sdk.exceptions import CityNotFoundError
from openweather_sdk.models import CompleteForecast, CurrentWeather, DayForecast

client = TestClient(app)

MOCK_CURRENT = CurrentWeather(
    temp=25, description="ceu limpo", city="Sao Paulo", date="14/03"
)
MOCK_FORECAST = [
    DayForecast(date="15/03", temp=22),
    DayForecast(date="16/03", temp=20),
]
MOCK_COMPLETE = CompleteForecast(current=MOCK_CURRENT, forecast=MOCK_FORECAST)
MOCK_RESPONSE = {
    "current": asdict(MOCK_CURRENT),
    "forecast": [asdict(f) for f in MOCK_FORECAST],
    "gist_status": "Gist publicado com sucesso !",
}


class TestValidation:
    """Testes de validacao de entrada no endpoint /weather."""

    def test_non_numeric_coords_returns_422(self):
        """lat/lon nao numericos devem retornar 422."""
        response = client.get("/weather?lat=abc&lon=xyz")
        assert response.status_code == 422

    @patch("app.core.service.get_weather")
    def test_extra_params_are_ignored(self, mock_service):
        """Parametros extras sao ignorados quando ha params validos."""
        mock_service.return_value = MOCK_RESPONSE
        response = client.get("/weather?city=London&bb=AAA&foo=123")
        assert response.status_code == 200

    def test_only_unknown_params_returns_422(self):
        """Somente params desconhecidos (sem city/lat/lon) deve retornar 422."""
        response = client.get("/weather?tipo=bolo&foo=bar")
        assert response.status_code == 422

    def test_no_params_returns_422(self):
        """Requisicao sem parametros deve retornar 422."""
        response = client.get("/weather")
        assert response.status_code == 422


class TestPriority:
    """Testes de priorizacao lat/lon vs cidade."""

    @patch("app.adapters.gist_client.update")
    @patch("app.adapters.weather_client.fetch")
    def test_coords_take_priority_over_city(self, mock_weather, mock_gist):
        """Quando city e lat/lon sao informados, usa lat/lon."""
        mock_weather.return_value = MOCK_COMPLETE
        mock_gist.return_value = "Gist publicado com sucesso !"
        response = client.get(
            "/weather?city=London&lat=-23.55&lon=-46.63"
        )
        assert response.status_code == 200
        mock_weather.assert_called_once()
        kwargs = mock_weather.call_args[1]
        assert kwargs.get("lat") == -23.55
        assert kwargs.get("lon") == -46.63
        assert "city" not in kwargs

    @patch("app.adapters.gist_client.update")
    @patch("app.adapters.weather_client.fetch")
    def test_invalid_coords_with_city_falls_back(self, mock_weather, mock_gist):
        """lat/lon invalidos com city valida faz fallback pra city."""
        mock_weather.return_value = MOCK_COMPLETE
        mock_gist.return_value = "Gist publicado com sucesso !"
        response = client.get(
            "/weather?city=London&lat=999&lon=999"
        )
        assert response.status_code == 200
        kwargs = mock_weather.call_args[1]
        assert kwargs.get("city") == "London"

    @patch("app.adapters.gist_client.update")
    @patch("app.adapters.weather_client.fetch")
    def test_invalid_coords_and_city_returns_error(self, mock_weather, mock_gist):
        """lat/lon invalidos e cidade inexistente retorna erro combinado."""
        mock_weather.side_effect = CityNotFoundError()
        response = client.get(
            "/weather?city=cidadeinexistente&lat=999&lon=999"
        )
        assert response.status_code in (404, 422)
        detail = str(response.json().get("detail", "")).lower()
        assert "coordenadas" in detail or "cidade" in detail


class TestHappyPath:
    """Testes de caminho feliz com retorno completo."""

    @patch("app.core.service.get_weather")
    def test_weather_by_city_returns_200(self, mock_service):
        """GET /weather?city=London retorna 200 com current, forecast e gist_status."""
        mock_service.return_value = MOCK_RESPONSE
        response = client.get("/weather?city=London")
        assert response.status_code == 200
        data = response.json()
        assert "current" in data
        assert "forecast" in data
        assert "gist_status" in data
        assert data["current"]["city"] == "Sao Paulo"
        assert len(data["forecast"]) == 2

    @patch("app.core.service.get_weather")
    def test_weather_by_coords_returns_200(self, mock_service):
        """GET /weather?lat/lon retorna 200 com current, forecast e gist_status."""
        mock_service.return_value = MOCK_RESPONSE
        response = client.get("/weather?lat=-23.55&lon=-46.63")
        assert response.status_code == 200
        data = response.json()
        assert "current" in data
        assert "forecast" in data
        assert "gist_status" in data
