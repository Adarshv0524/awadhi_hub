# app/api/v1/admin_audit.py
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import require_role, get_current_user
from app.core.permissions import Role
from app.db.models import AuditLog, User
from app.services.privacy_service import redact_pii, mask_identifier

router = APIRouter(prefix="/admin/audit_logs", tags=["admin-audit"])


class AuditLogOut(BaseModel):
    id: int
    actor_user_id: int | None
    action: str
    resource_type: str | None
    resource_id: int | None
    before: dict | None
    after: dict | None
    metadata: dict | None
    created_at: str


class AuditLogListOut(BaseModel):
    total: int
    results: list[AuditLogOut]

def _apply_filters(q, action, resource_type, actor_user_id, start, end):
    if action:
        q = q.filter(AuditLog.action == action)
    if resource_type:
        q = q.filter(AuditLog.resource_type == resource_type)
    if actor_user_id is not None:
        q = q.filter(AuditLog.actor_user_id == actor_user_id)
    if start:
        q = q.filter(AuditLog.created_at >= start)
    if end:
        q = q.filter(AuditLog.created_at <= end)
    return q

def _row_to_dict(r, current_user: User):
    """Convert AuditLog row to dict"""
    # Tolerant accessor for metadata field
    meta = getattr(r, "audit_metadata", None) if hasattr(r, "audit_metadata") else getattr(r, "metadata", None)
    
    privileged = current_user.role == Role.ADMIN

    return {
        "id": r.id,
        "actor_user_id": r.actor_user_id if privileged else None,
        "action": r.action,
        "resource_type": r.resource_type,
        "resource_id": r.resource_id if privileged else mask_identifier(r.resource_id),
        "before": redact_pii(r.audit_before),
        "after": redact_pii(r.after),
        "metadata": redact_pii(meta),
        "created_at": r.created_at.isoformat() if r.created_at else "",
    }

@router.get("", response_model=AuditLogListOut, dependencies=[Depends(require_role(Role.MODERATOR))])
def list_audit_logs(
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    actor_user_id: Optional[int] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(AuditLog)
    q = _apply_filters(q, action, resource_type, actor_user_id, start, end)
    if current_user.role != Role.ADMIN:
        q = q.filter(AuditLog.actor_user_id == current_user.id)
    total = q.count()
    rows = q.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
    results = [_row_to_dict(r, current_user) for r in rows]
    return {"total": total, "results": results}

@router.get("/{id}", response_model=AuditLogOut, dependencies=[Depends(require_role(Role.MODERATOR))])
def get_audit_log(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    r = db.query(AuditLog).filter(AuditLog.id == id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Audit log not found")
    if current_user.role != Role.ADMIN and r.actor_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="RLS policy denied access to this audit row")
    return _row_to_dict(r, current_user)
