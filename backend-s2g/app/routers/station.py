from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.schemas.station import Station, StationCreate
from app.models.station import Station as StationModel
from app.core.database import get_db
from app.core.auth import verify_token

router = APIRouter(
    prefix="/stations",
    tags=["stations"],
    dependencies=[Depends(verify_token)]  # Protege todas las rutas del router
)

@router.post("/", response_model=Station, status_code=status.HTTP_201_CREATED)
def create_station(
    station: StationCreate,
    db: Session = Depends(get_db)
):
    db_station = StationModel(**station.dict())
    db.add(db_station)
    db.commit()
    db.refresh(db_station)
    return db_station

@router.get("/", response_model=List[Station])
def get_stations(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(StationModel)
    if status:
        q = q.filter(StationModel.status == status)
    return q.all()

@router.patch("/{station_id}", response_model=Station)
def update_station_status(
    station_id: int,
    new_status: str,
    db: Session = Depends(get_db)
):
    db_station = db.query(StationModel).filter(StationModel.id == station_id).first()
    if not db_station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )
    db_station.status = new_status
    db.commit()
    db.refresh(db_station)
    return db_station
