from sqlalchemy import Column, Integer, String, Float, Enum, DateTime
from app.core.database import Base
from datetime import datetime
import enum

class StatusEnum(str, enum.Enum):
    activo = "activo"
    inactivo = "inactivo"

class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    max_kw = Column(Float, nullable=False)
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.inactivo)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
