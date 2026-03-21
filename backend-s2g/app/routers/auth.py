from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from datetime import datetime, timedelta
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

fake_users = {
    "admin@s2g.com": {"password": "123456"}
}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode({
        "sub": form_data.username,
        "exp": datetime.utcnow() + timedelta(hours=12)
    }, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}
