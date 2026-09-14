from fastapi import APIRouter

from rps.api.health import router as health_router
from rps.api.v1.games import router as games_router
from rps.api.v1.players import router as players_router

v1_router = APIRouter(prefix="/rps/v1")
v1_router.include_router(players_router)
v1_router.include_router(games_router)

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(v1_router)
