from fastapi import APIRouter
from dtos.base_dto import BaseResponseDTO
from services.analyzer_service import start_analyzer_service

analyzer_router = APIRouter()


@analyzer_router.post(
    "/{building_id}/start", response_model=BaseResponseDTO[None]
)
async def start_analyzer_route(
    building_id: str,
):
    return await start_analyzer_service(building_id)
