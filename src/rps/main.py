from fastapi import FastAPI

from rps.api.router import api_router
from rps.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Pierre-Feuille-Ciseaux API",
        version="1.0.0",
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
    )
    app.include_router(api_router)
    return app


app = create_app()
