import logging

from fastapi import APIRouter
from pydantic import BaseModel, Field


logger = logging.getLogger("app.api.telemetry")

router = APIRouter(prefix="/api/v1/telemetry", tags=["telemetry"])


class RendererFallbackEventIn(BaseModel):
    event_name: str = Field(..., min_length=1)
    poetry_type: str = Field(..., min_length=1)
    chapter_id: int | None = None
    sequence_no: int = Field(..., ge=0)


@router.post("/renderer-fallback", status_code=202)
async def renderer_fallback_event(payload: RendererFallbackEventIn):
    logger.info(
        "renderer_fallback_event",
        extra={
            "event_name": payload.event_name,
            "poetry_type": payload.poetry_type,
            "chapter_id": payload.chapter_id,
            "sequence_no": payload.sequence_no,
        },
    )
    return {"accepted": True}
