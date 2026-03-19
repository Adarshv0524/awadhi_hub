# app/api/v1/users.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User

router = APIRouter(prefix="/users", tags=["users"])


class PublicUserOut(BaseModel):
    id: int
    username: Optional[str]
    role: str

    class Config:
        orm_mode = True


@router.get("/{username}", response_model=PublicUserOut)
def get_public_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
