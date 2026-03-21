import csv
from app.core.database import engine, Base, SessionLocal
from app.models.station import Station as StationModel

def seed_stations(csv_path="data/estaciones.csv"):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            station = StationModel(
                name=row["name"],
                location=row["location"],
                max_kw=float(row["max_kw"]),
                status=row["status"]
            )
            db.add(station)
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_stations()
    print("Seed completed.")
