# app/api/v1/admin_audit.py
import csv
import io
import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import require_role
from app.core.permissions import Role
from app.db.models import AuditLog
import logging

router = APIRouter(prefix="/admin/audit_logs", tags=["admin-audit"])
logger = logging.getLogger("app.api.admin_audit")

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

def _row_to_dict(r):
    """Convert AuditLog row to dict"""
    # Tolerant accessor for metadata field
    meta = getattr(r, "audit_metadata", None) if hasattr(r, "audit_metadata") else getattr(r, "metadata", None)
    
    return {
        "id": r.id,
        "actor_user_id": r.actor_user_id,
        "action": r.action,
        "resource_type": r.resource_type,
        "resource_id": r.resource_id,
        "before": r.audit_before,  # ✅ Changed from r.before
        "after": r.after,
        "metadata": meta,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }

@router.get("", dependencies=[Depends(require_role(Role.ADMIN))])
def list_audit_logs(
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    actor_user_id: Optional[int] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    q = db.query(AuditLog)
    q = _apply_filters(q, action, resource_type, actor_user_id, start, end)
    total = q.count()
    rows = q.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
    results = [_row_to_dict(r) for r in rows]
    return {"total": total, "results": results}

@router.get("/export/csv", dependencies=[Depends(require_role(Role.ADMIN))], deprecated=True)
def export_audit_csv(
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    actor_user_id: Optional[int] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    logger.warning("Deprecated endpoint hit: GET /admin/audit_logs/export/csv")
    q = db.query(AuditLog)
    q = _apply_filters(q, action, resource_type, actor_user_id, start, end)
    rows = q.order_by(AuditLog.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id","actor_user_id","action","resource_type","resource_id","before","after","audit_metadata","created_at"])
    for r in rows:
        # read audit_metadata if present else metadata (backwards compatibility)
        meta = getattr(r, "audit_metadata", None) if hasattr(r, "audit_metadata") else getattr(r, "metadata", None)
        writer.writerow([
            r.id,
            r.actor_user_id,
            r.action,
            r.resource_type,
            r.resource_id,
            json.dumps(r.audit_before, ensure_ascii=False) if r.audit_before is not None else "",  # ✅ Changed from r.before
            json.dumps(r.after, ensure_ascii=False) if r.after is not None else "",
            json.dumps(meta, ensure_ascii=False) if meta is not None else "",
            r.created_at.isoformat() if r.created_at else "",
        ])
    resp = Response(content=output.getvalue(), media_type="text/csv")
    resp.headers["Content-Disposition"] = f"attachment; filename=audit_logs_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
    return resp

@router.get("/{id}", dependencies=[Depends(require_role(Role.ADMIN))])
def get_audit_log(id: int, db: Session = Depends(get_db)):
    r = db.query(AuditLog).filter(AuditLog.id == id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return _row_to_dict(r)
