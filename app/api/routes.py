from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.api.mappings import EXCEPTION_STATUS_MAP
from app.core import service
from app.core.exceptions import GistPublishError
from openweather_sdk.exceptions import OpenWeatherError

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/weather")
def get_weather(
    city: Optional[str] = Query(None),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
):
    """Endpoint principal de consulta de clima."""
    try:
        result = service.get_weather(city=city, lat=lat, lon=lon)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except GistPublishError as e:
        return JSONResponse(status_code=502, content=e.result)
    except OpenWeatherError as e:
        status = EXCEPTION_STATUS_MAP.get(type(e), 502)
        raise HTTPException(status_code=status, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=503, detail="Servico temporariamente indisponivel"
        )

    return result
