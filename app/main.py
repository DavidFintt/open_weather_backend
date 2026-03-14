from fastapi import FastAPI

from app.middleware import ConfigMiddleware

app = FastAPI()
app.add_middleware(ConfigMiddleware)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/weather")
def get_weather():
    pass
