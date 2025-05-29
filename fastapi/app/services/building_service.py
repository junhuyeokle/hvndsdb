from sqlalchemy.orm import Session
from dtos.building_dto import (
    AddBuildingRequestDTO,
    BuildingDetailDTO,
    UpdateBuildingRequestDTO,
    BuildingDTO,
    GetBuildingDetailResponseDTO,
    GetBuildingListRequestDTO,
    GetBuildingListResponseDTO,
)
from exception import CustomException, handle_exception
from dtos.base_dto import BaseResponseDTO
from entities.building import Building
from uuid import UUID

from routers.deblur_gs_router import deblur_gs_manager
from sc3 import get_presigned_upload_url


def get_building_detail_service(
    building_id: UUID, db: Session
) -> GetBuildingDetailResponseDTO:
    try:
        building = (
            db.query(Building)
            .filter(Building.building_id == building_id)
            .first()
        )
        if not building:
            raise CustomException(404, "Building not found.")
        return GetBuildingDetailResponseDTO(
            success=True,
            code=200,
            message="Building detail retrieved.",
            data=BuildingDetailDTO.model_validate(building),
        )
    except Exception as e:
        handle_exception(e, db)


def add_building_service(
    dto: AddBuildingRequestDTO, db: Session
) -> BaseResponseDTO:
    try:
        building = Building(
            name=dto.name,
            latitude=dto.latitude,
            longitude=dto.longitude,
            user_id=dto.user_id,
        )
        db.add(building)
        db.commit()
        return BaseResponseDTO(
            success=True,
            code=201,
            message="Building added successfully.",
            data={
                "sample_upload_url": get_presigned_upload_url(
                    building.building_id + "/sample.mp4", "video/mp4"
                )
            },
        )
    except Exception as e:
        handle_exception(e, db)


def get_building_list_service(
    dto: GetBuildingListRequestDTO, db: Session
) -> GetBuildingListResponseDTO:
    try:
        query = db.query(Building)
        if dto.query:
            query = query.filter(Building.name.contains(dto.query))
        buildings = query.all()
        building_dtos = [
            BuildingDTO.model_validate(building) for building in buildings
        ]
        return GetBuildingListResponseDTO(
            success=True,
            code=200,
            message="Building list retrieved.",
            data=building_dtos,
        )
    except Exception as e:
        handle_exception(e, db)


def update_building_service(
    building_id: UUID, dto: UpdateBuildingRequestDTO, db: Session
) -> GetBuildingDetailResponseDTO:
    try:
        building = (
            db.query(Building)
            .filter(Building.building_id == building_id)
            .first()
        )
        if not building:
            raise CustomException(404, "Building not found.")
        for key, value in dto.model_dump(exclude_unset=True).items():
            setattr(building, key, value)
        db.commit()
        db.refresh(building)
        return get_building_detail_service(building.building_id, db)
    except Exception as e:
        handle_exception(e, db)


def delete_building_service(
    building_id: UUID, db: Session
) -> BaseResponseDTO[None]:
    try:
        building = (
            db.query(Building)
            .filter(Building.building_id == building_id)
            .first()
        )
        if not building:
            raise CustomException(404, "Building not found.")
        db.delete(building)
        db.commit()
        return BaseResponseDTO(
            success=True, code=200, message="Building deleted.", data=None
        )
    except Exception as e:
        handle_exception(e, db)
