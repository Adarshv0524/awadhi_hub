# app/api/v1/admin_settings.py
import json as _json
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, ValidationError
from typing import Any, List
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.services.system_settings import (
    get_setting,
    set_setting,
    delete_setting,
    bulk_import_settings,
    SETTINGS_IMPORT_SCHEMA_VERSION,
)
from app.core.security import require_role, get_current_user
from app.core.permissions import Role

router = APIRouter(prefix="/admin/system_settings", tags=["admin-system-settings"])

class SettingIn(BaseModel):
    value: Any

class SettingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    value: Any


class BulkSettingIn(BaseModel):
    key: str
    value: Any


class BulkImportIn(BaseModel):
    schema_version: int
    settings: List[BulkSettingIn]
    dry_run: bool = True
    confirmation_text: str | None = None


CRITICAL_CONFIRMATION_TEXT = "APPLY CRITICAL SETTINGS"

@router.get("", response_model=List[SettingOut], dependencies=[Depends(require_role(Role.ADMIN))])
def list_settings(db: Session = Depends(get_db)):
    query = text("SELECT `setting_key`, `value` FROM system_settings ORDER BY `setting_key` ASC")    
    rows = db.execute(query).fetchall()
    return [{"key": r[0], "value": r[1]} for r in rows]

@router.get("/{key}", response_model=SettingOut, dependencies=[Depends(require_role(Role.ADMIN))])
def get_setting_endpoint(key: str, db: Session = Depends(get_db)):
    val = get_setting(db, key, default=None, allow_env_override=True)
    if val is None:
        raise HTTPException(status_code=404, detail="Setting not found")
    return {"key": key, "value": val}

@router.put("/{key}", response_model=SettingOut, dependencies=[Depends(require_role(Role.ADMIN))])
async def upsert_setting(key: str, request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Accept JSON body with format: {"value": <actual_value>}
    Extracts the "value" field and stores it as the setting value.
    """
    try:
        # Read JSON body
        body_data = await request.json()
        
        # Extract the "value" field - this is what gets stored
        if not isinstance(body_data, dict) or "value" not in body_data:
            raise HTTPException(status_code=422, detail="Request body must be JSON object with 'value' field")
        
        actual_value = body_data["value"]
        
        # Capture metadata from request headers for audit
        audit_meta = {
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "request_id": request.headers.get("X-Request-ID") or request.headers.get("x-request-id"),
        }
        
        # Set the value (service will validate known keys)
        set_setting(db, key, actual_value, actor_user_id=current_user.id if current_user else None, metadata=audit_meta)
        
        return {"key": key, "value": actual_value}
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set setting: {str(e)}")


@router.post("/import", dependencies=[Depends(require_role(Role.ADMIN))])
async def import_settings(
    payload: BulkImportIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if payload.schema_version != SETTINGS_IMPORT_SCHEMA_VERSION:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Unsupported settings import schema version",
                "expected": SETTINGS_IMPORT_SCHEMA_VERSION,
                "received": payload.schema_version,
            },
        )

    if not payload.settings:
        raise HTTPException(status_code=400, detail="Import payload must include at least one setting")

    audit_meta = {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "request_id": request.headers.get("X-Request-ID") or request.headers.get("x-request-id"),
        "schema_version": payload.schema_version,
    }

    settings_payload = [item.model_dump() for item in payload.settings]

    try:
        preview = bulk_import_settings(
            db=db,
            settings_payload=settings_payload,
            actor_user_id=current_user.id if current_user else None,
            metadata=audit_meta,
            dry_run=True,
        )

        has_critical_changes = any(
            item["is_critical"] and item["action"] in {"create", "update"}
            for item in preview["items"]
        )

        if payload.dry_run:
            return {
                "schema_version": SETTINGS_IMPORT_SCHEMA_VERSION,
                "confirmation_required": has_critical_changes,
                "confirmation_text_hint": CRITICAL_CONFIRMATION_TEXT if has_critical_changes else None,
                **preview,
            }

        if has_critical_changes and payload.confirmation_text != CRITICAL_CONFIRMATION_TEXT:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Critical settings detected. Confirmation text required.",
                    "required_confirmation_text": CRITICAL_CONFIRMATION_TEXT,
                },
            )

        applied = bulk_import_settings(
            db=db,
            settings_payload=settings_payload,
            actor_user_id=current_user.id if current_user else None,
            metadata={**audit_meta, "confirmed_critical": has_critical_changes},
            dry_run=False,
        )

        return {
            "schema_version": SETTINGS_IMPORT_SCHEMA_VERSION,
            "confirmation_required": has_critical_changes,
            "confirmation_text_hint": CRITICAL_CONFIRMATION_TEXT if has_critical_changes else None,
            **applied,
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import settings: {str(e)}")

@router.delete("/{key}", status_code=204, dependencies=[Depends(require_role(Role.ADMIN))])
def delete_setting_endpoint(key: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    delete_setting(db, key, actor_user_id=current_user.id if current_user else None)
    # 204 No Content - no return needed
