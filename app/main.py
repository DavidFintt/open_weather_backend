from fastapi import FastAPI

from app.api.routes import router
from app.middleware import ConfigMiddleware

app = FastAPI()
app.add_middleware(ConfigMiddleware)
app.include_router(router)
