from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.station import Station as StationModel, StatusEnum
from app.core.database import get_db
from app.core.auth import verify_token

router = APIRouter(
    prefix="/stations",
    tags=["stations"],
    dependencies=[Depends(verify_token)]  # Protege todas las rutas aquí
)

@router.get("/stats")
def get_station_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(StationModel.id)).scalar()
    activos = (
        db.query(func.count(StationModel.id))
          .filter(StationModel.status == StatusEnum.activo)
          .scalar()
    )
    inactivos = (
        db.query(func.count(StationModel.id))
          .filter(StationModel.status == StatusEnum.inactivo)
          .scalar()
    )
    total_kw = db.query(func.sum(StationModel.max_kw)).scalar() or 0
    return {
        "total": total,
        "activos": activos,
        "inactivos": inactivos,
        "total_kw": total_kw
    }
