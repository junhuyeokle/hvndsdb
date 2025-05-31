from sqlalchemy import Boolean, Column, Double, ForeignKey, String
from sqlalchemy.orm import relationship
from utils.database import Base
from entities.time_mixin import TimeMixin
import uuid


class Building(Base, TimeMixin):
    __tablename__ = "building"

    building_id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name = Column(String(256), nullable=False)
    longitude = Column(Double, nullable=False)
    latitude = Column(Double, nullable=False)
    user_id = Column(
        String(36),
        ForeignKey("user.user_id", ondelete="CASCADE"),
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )
    is_ready = Column(Boolean, default=False)

    user = relationship("User", back_populates="buildings")
