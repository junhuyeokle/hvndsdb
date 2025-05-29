from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from database import Base
from entities.time_mixin import TimeMixin
import uuid


class User(Base, TimeMixin):
    __tablename__ = "user"

    user_id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email = Column(String(256), nullable=False)
    name = Column(String(256), nullable=False)
    buildings = relationship(
        "Building", back_populates="user", passive_deletes=True
    )
