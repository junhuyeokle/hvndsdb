from sqlalchemy.orm import Session, joinedload
from dtos.user_dto import (
    AddUserRequestDTO,
    UpdateUserRequestDTO,
    UserDTO,
    GetUserDetailResponseDTO,
    GetUserListRequestDTO,
    GetUserListResponseDTO,
    UserDetailDTO,
)
from utils.exception import CustomException, handle_exception
from dtos.base_dto import BaseResponseDTO
from entities.user import User
from uuid import UUID


def get_user_detail_service(
    user_id: UUID, db: Session
) -> GetUserDetailResponseDTO:
    try:
        user = (
            db.query(User)
            .options(joinedload(User.buildings))
            .filter(User.user_id == user_id)
            .first()
        )
        if not user:
            raise CustomException(404, "User not found.")
        return GetUserDetailResponseDTO(
            success=True,
            code=200,
            message="User detail retrieved.",
            data=UserDetailDTO.model_validate(user),
        )
    except Exception as e:
        handle_exception(e, db)


def add_user_service(
    dto: AddUserRequestDTO, db: Session
) -> GetUserDetailResponseDTO:
    try:
        user = User(email=dto.email, name=dto.name)
        db.add(user)
        db.commit()
        db.refresh(user)
        return get_user_detail_service(user.user_id, db)
    except Exception as e:
        handle_exception(e, db)


def get_user_list_service(
    dto: GetUserListRequestDTO, db: Session
) -> GetUserListResponseDTO:
    try:
        query = db.query(User)
        if dto.query:
            query = query.filter(User.name.contains(dto.query))
        users = query.all()
        user_dtos = [UserDTO.model_validate(user) for user in users]
        return GetUserListResponseDTO(
            success=True,
            code=200,
            message="User list retrieved.",
            data=user_dtos,
        )
    except Exception as e:
        handle_exception(e, db)


def update_user_service(
    user_id: UUID, dto: UpdateUserRequestDTO, db: Session
) -> GetUserDetailResponseDTO:
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise CustomException(404, "User not found.")
        for key, value in dto.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return get_user_detail_service(user.user_id, db)
    except Exception as e:
        handle_exception(e, db)


def delete_user_service(user_id: UUID, db: Session) -> BaseResponseDTO[None]:
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise CustomException(404, "User not found.")
        db.delete(user)
        db.commit()
        return BaseResponseDTO(
            success=True, code=200, message="User deleted.", data=None
        )
    except Exception as e:
        handle_exception(e, db)
