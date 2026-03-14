from app.config import OPENWEATHER_API_KEY
from openweather_sdk import OpenWeatherClient


def fetch(**kwargs):
    """Consulta clima via SDK."""
    client = OpenWeatherClient(api_key=OPENWEATHER_API_KEY)
    return client.get_complete_weather(**kwargs)
