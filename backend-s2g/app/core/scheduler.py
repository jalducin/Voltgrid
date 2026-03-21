from apscheduler.schedulers.background import BackgroundScheduler
from app.core.database import SessionLocal
from app.models.station import Station, StatusEnum

def change_status():
    db = SessionLocal()
    try:
        stations = db.query(Station).all()
        for s in stations:
            s.status = StatusEnum.inactivo if s.status == StatusEnum.activo else StatusEnum.activo
        db.commit()
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(change_status, "interval", minutes=1)
    scheduler.start()
