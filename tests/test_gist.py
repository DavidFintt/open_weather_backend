from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.adapters import gist_client
from openweather_sdk.models import CompleteForecast, CurrentWeather, DayForecast

client = TestClient(app)

MOCK_CURRENT = CurrentWeather(
    temp=30, description="poucas nuvens", city="Londres", date="13/03"
)
MOCK_FORECAST = [
    DayForecast(date="14/03", temp=20),
    DayForecast(date="15/03", temp=30),
    DayForecast(date="16/03", temp=25),
    DayForecast(date="17/03", temp=28),
    DayForecast(date="18/03", temp=22),
]
MOCK_COMPLETE = CompleteForecast(current=MOCK_CURRENT, forecast=MOCK_FORECAST)


class TestGist:
    """Testes de publicacao no Gist e adapter gist_client."""

    @patch("app.adapters.gist_client.update")
    @patch("app.adapters.weather_client.fetch")
    def test_gist_receives_weather_data(self, mock_weather, mock_gist):
        """gist_client.update() deve ser chamado com os dados do clima."""
        mock_weather.return_value = MOCK_COMPLETE
        mock_gist.return_value = "Gist publicado com sucesso !"
        response = client.get("/weather?city=London")
        assert response.status_code == 200
        mock_gist.assert_called_once()
        data = response.json()
        assert data["gist_status"] == "Gist publicado com sucesso !"

    @patch("app.adapters.gist_client.update")
    @patch("app.adapters.weather_client.fetch")
    def test_gist_failure_returns_502(self, mock_weather, mock_gist):
        """Falha no gist deve retornar 502 com gist_status de erro."""
        mock_weather.return_value = MOCK_COMPLETE
        mock_gist.side_effect = Exception("GitHub API error")
        response = client.get("/weather?city=London")
        assert response.status_code == 502
        data = response.json()
        assert data["gist_status"] == "Erro ao publicar gist"

    @patch("app.adapters.gist_client.Github")
    def test_update_complete_weather(self, mock_github_cls):
        """Deve atualizar o gist com dados completos do clima."""
        mock_gist = MagicMock()
        mock_github_cls.return_value.get_gist.return_value = mock_gist
        gist_client.update(MOCK_COMPLETE)
        mock_gist.edit.assert_called_once()

    @patch("app.adapters.gist_client.Github")
    def test_update_with_empty_forecast(self, mock_github_cls):
        """Forecast vazio deve levantar erro."""
        from app.core.exceptions import EmptyWeatherDataError
        empty = CompleteForecast(current=MOCK_CURRENT, forecast=[])
        with pytest.raises(EmptyWeatherDataError):
            gist_client.update(empty)

    @patch("app.adapters.gist_client.Github")
    def test_update_with_empty_current(self, mock_github_cls):
        """Current vazio deve levantar erro."""
        from app.core.exceptions import EmptyWeatherDataError
        empty = CompleteForecast(current=None, forecast=MOCK_FORECAST)
        with pytest.raises(EmptyWeatherDataError):
            gist_client.update(empty)

    @patch("app.adapters.gist_client.Github")
    def test_format_matches_template(self, mock_github_cls):
        """Conteudo do gist deve seguir o template definido."""
        mock_gist = MagicMock()
        mock_github_cls.return_value.get_gist.return_value = mock_gist
        gist_client.update(MOCK_COMPLETE)
        call_args = mock_gist.edit.call_args
        files = call_args[1]["files"]
        content = files["FinttWeatherMap"]._identity["content"]
        assert "Cidade: Londres" in content
        assert "Clima em 13/03: 30°, poucas nuvens." in content
        assert "14/03: 20°" in content

    @patch("app.adapters.gist_client.Github")
    def test_invalid_github_token_raises_error(self, mock_github_cls):
        """Token invalido do GitHub deve levantar excecao."""
        mock_github_cls.return_value.get_gist.side_effect = Exception(
            "Bad credentials"
        )
        with pytest.raises(Exception, match="Bad credentials"):
            gist_client.update(MOCK_COMPLETE)
