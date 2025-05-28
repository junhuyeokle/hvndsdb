from fastapi import APIRouter

from dtos.general_dto import (
    GetPresignedUrlReqeustDTO,
    GetPresignedUrlResponseDTO,
)
from services.general_service import get_presigned_url_service


general_router = APIRouter()


@general_router.post("/", response_model=GetPresignedUrlResponseDTO)
def get_presigned_url_router(dto: GetPresignedUrlReqeustDTO):
    return get_presigned_url_service(dto)
