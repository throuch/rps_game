from typing import Annotated

from fastapi import APIRouter, Depends

from rps.api.deps import get_hall_of_fame_service
from rps.api.schemas import HallOfFameEntryResponse, HallOfFameResponse
from rps.domain.services import HallOfFameService

router = APIRouter(tags=["hall-of-fame"])


@router.get("/hof", response_model=HallOfFameResponse)
def get_hall_of_fame(
    service: Annotated[HallOfFameService, Depends(get_hall_of_fame_service)],
) -> HallOfFameResponse:
    entries = service.get_ranking()
    items = [
        HallOfFameEntryResponse(
            name=entry.name,
            wins=entry.wins,
            losses=entry.losses,
            total=entry.total,
            win_rate=entry.win_rate,
            created_at=entry.created_at,
        )
        for entry in entries
    ]
    return HallOfFameResponse(items=items)
