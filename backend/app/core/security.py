# app/core/security.py

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Callable, Dict, Any

from app.db.session import get_db
from app.db.models import User
from app.auth.jwt import decode_token
from app.core.permissions import has_permission, role_at_least, Permission, Role, check_abac


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """
    Extract JWT from Authorization header, decode, and load user from DB.
    This is the single place where we turn a token into a User object.
    """
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing credentials")

    token = auth.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    try:
        user_id_int = int(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user id in token")

    user = db.query(User).filter(User.id == user_id_int).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active or user.is_banned:
        raise HTTPException(status_code=403, detail="User not allowed")

    return user


def require_role(min_role: str):
    """
    Usage:
        @router.get("/admin/users", dependencies=[Depends(require_role(Role.ADMIN))])
    or
        def endpoint(current_user: User = Depends(require_role(Role.ADMIN))):
            ...
    """
    def dependency(user: User = Depends(get_current_user)) -> User:
        if not role_at_least(user.role, min_role):
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return dependency


def require_permission(perm_bit: int):
    """
    Usage:
        @router.get("/admin/users", dependencies=[Depends(require_permission(Permission.MANAGE_USERS))])
    """
    def dependency(user: User = Depends(get_current_user)) -> User:
        if not has_permission(user.permissions, perm_bit):
            raise HTTPException(status_code=403, detail="Missing permission")
        return user
    return dependency


def require_abac(action: str):
    """
    Returns a dependency that gives you a checker function:

        @router.post("/moderation/...")
        def approve(...,
                    user: User = Depends(require_role(Role.MODERATOR)),
                    abac_check: Callable[[Dict[str, Any]], None] = Depends(require_abac("moderation:approve"))):
            abac_check({"author_slug": submission.author_slug, "priority": submission.priority})
            ...

    For now, no endpoints use it yet, but it's ready for Moderation module.
    """
    def dependency(user: User = Depends(get_current_user)) -> Callable[[Dict[str, Any]], None]:
        def checker(resource: Dict[str, Any]) -> None:
            if not check_abac(user.permission_scopes, action, resource):
                raise HTTPException(status_code=403, detail="ABAC check failed")
        return checker
    return dependency
