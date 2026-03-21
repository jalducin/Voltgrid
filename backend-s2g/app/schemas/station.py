from pydantic import BaseModel
from datetime import datetime

class StationBase(BaseModel):
    name: str
    location: str
    max_kw: float
    status: str

class StationCreate(StationBase):
    pass

class Station(StationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True