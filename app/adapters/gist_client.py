from github import Github, InputFileContent

from app.config import GITHUB_TOKEN, GIST_ID
from app.core.exceptions import EmptyWeatherDataError


def _format_content(complete_forecast):
    """Formata CompleteForecast no template de texto do gist."""
    current = complete_forecast.current
    lines = [
        f"Cidade: {current.city}",
        f"Clima em {current.date}: {current.temp}\u00b0, {current.description}.",
        "",
        f"Previs\u00e3o dos pr\u00f3ximos {len(complete_forecast.forecast)} dias:",
    ]
    for day in complete_forecast.forecast:
        lines.append(f"{day.date}: {day.temp}\u00b0")
    return "\n".join(lines)


def update(complete_forecast):
    """Publica dados de clima no gist."""
    if not complete_forecast.current:
        raise EmptyWeatherDataError("Dados de clima atual vazios")
    if not complete_forecast.forecast:
        raise EmptyWeatherDataError("Forecast vazio")

    content = _format_content(complete_forecast)
    g = Github(GITHUB_TOKEN)
    gist = g.get_gist(GIST_ID)
    gist.edit(files={"FinttWeatherMap": InputFileContent(content)})
    return "Gist publicado com sucesso !"
