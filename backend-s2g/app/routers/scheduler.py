from fastapi import APIRouter, Depends
from app.core.auth import verify_token
from app.core.scheduler import change_status

router = APIRouter(prefix="/scheduler", tags=["scheduler"])

@router.post("/run", dependencies=[Depends(verify_token)])
def run_scheduler_now():
    change_status()
    return {"detail": "Scheduler executed"}
