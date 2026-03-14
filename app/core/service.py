from dataclasses import asdict

from app.adapters import gist_client, weather_client
from app.core.exceptions import GistPublishError


def _coords_valid(lat, lon):
    """Verifica se as coordenadas estao no range valido."""
    if lat is None or lon is None:
        return False
    return -90 <= lat <= 90 and -180 <= lon <= 180


def get_weather(city=None, lat=None, lon=None):
    """Orquestra consulta de clima e publicacao no gist."""
    if _coords_valid(lat, lon):
        kwargs = {"lat": lat, "lon": lon}
    elif city:
        kwargs = {"city": city}
    else:
        raise ValueError("Informe city ou lat/lon validos.")

    data = weather_client.fetch(**kwargs)

    try:
        gist_status = gist_client.update(data)
    except Exception:
        gist_status = "Erro ao publicar gist"

    result = {
        "current": asdict(data.current),
        "forecast": [asdict(f) for f in data.forecast],
        "gist_status": gist_status,
    }

    if gist_status == "Erro ao publicar gist":
        raise GistPublishError(result)

    return result
