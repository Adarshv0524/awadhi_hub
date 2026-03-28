# app/api/v1/admin_users.py

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List, Any, Dict
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.db.models import User
from app.core.security import require_role
from app.core.permissions import Role, ROLE_RANK

router = APIRouter(prefix="/admin/users", tags=["admin-users"])

ALLOWED_ROLES = set(ROLE_RANK.keys())


def _validate_role_or_400(role: str) -> str:
    normalized = (role or "").strip().lower()
    if normalized not in ALLOWED_ROLES:
        valid = ", ".join(sorted(ALLOWED_ROLES))
        raise HTTPException(status_code=400, detail=f"Invalid role '{role}'. Allowed roles: {valid}")
    return normalized


class UserCreateAdminIn(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    password: Optional[str] = None  # optional for oauth-only accounts
    role: str = Role.REGISTERED
    permissions: int = 0
    permission_scopes: Optional[Dict[str, Any]] = None
    is_active: bool = True
    is_banned: bool = False


class UserUpdateAdminIn(BaseModel):
    role: Optional[str] = None
    permissions: Optional[int] = None
    permission_scopes: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_banned: Optional[bool] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: Optional[str]
    role: str
    permissions: int
    permission_scopes: Optional[Dict[str, Any]]
    is_active: bool
    is_banned: bool
    created_at: datetime

@router.get(
    "",
    response_model=List[UserOut],
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def list_users(
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return users


@router.get(
    "/{user_id}",
    response_model=UserOut,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def get_user_admin(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post(
    "",
    response_model=UserOut,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def create_user_admin(data: UserCreateAdminIn, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    from app.auth.hash import hash_password  # local import to avoid cycle

    password_hash = hash_password(data.password) if data.password else None
    role = _validate_role_or_400(data.role)
    user = User(
        email=data.email,
        username=data.username,
        password_hash=password_hash,
        role=role,
        permissions=data.permissions,
        permission_scopes=data.permission_scopes,
        is_active=data.is_active,
        is_banned=data.is_banned,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch(
    "/{user_id}",
    response_model=UserOut,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def update_user_admin(user_id: int, data: UserUpdateAdminIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.role is not None:
        user.role = _validate_role_or_400(data.role)
    if data.permissions is not None:
        user.permissions = data.permissions
    if data.permission_scopes is not None:
        user.permission_scopes = data.permission_scopes
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.is_banned is not None:
        user.is_banned = data.is_banned

    db.commit()
    db.refresh(user)
    return user
