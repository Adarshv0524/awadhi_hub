from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


SUPPORTED_POETRY_TYPES = {
    "doha",
    "chaupai",
    "jhulana",
    "sorath",
    "savaiya",
    "ghanakshari",
    "chappay",
    "other_poetry",
}


class PoetryNodeIn(BaseModel):
    author_id: int = Field(..., gt=0)
    work_id: int = Field(..., gt=0)
    chapter_id: int = Field(..., gt=0)
    poetry_type: str = Field(..., min_length=1, max_length=50)
    sequence_no: int = Field(..., gt=0)
    main_text: str = Field(..., min_length=1)
    text_devanagari: Optional[str] = None
    text_romanized: Optional[str] = None
    meaning: Optional[str] = None
    prosody_metadata: Optional[dict[str, Any]] = None
    status: str = Field(default="active", min_length=1, max_length=20)
    visibility: str = Field(default="public", min_length=1, max_length=20)
    source_submission_id: Optional[int] = None
    created_by: Optional[int] = None
    verified_by: Optional[int] = None
    version: int = Field(default=1, gt=0)

    @field_validator("poetry_type")
    @classmethod
    def validate_poetry_type(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in SUPPORTED_POETRY_TYPES:
            raise ValueError("Unsupported poetry_type. Use a registered poetry type or 'other_poetry'.")
        return normalized

    @field_validator("prosody_metadata")
    @classmethod
    def validate_other_poetry_media_schema(cls, value: Optional[dict[str, Any]], info):
        if value is None:
            return value

        poetry_type = str(info.data.get("poetry_type", "")).strip().lower()
        if poetry_type != "other_poetry":
            return value

        media = value.get("media") if isinstance(value, dict) else None
        if media is None:
            return value
        if not isinstance(media, dict):
            raise ValueError("For other_poetry, prosody_metadata.media must be an object")

        media_type = media.get("type")
        if media_type not in {"image", "audio"}:
            raise ValueError("For other_poetry, prosody_metadata.media.type must be 'image' or 'audio'")

        media_url = media.get("url")
        if not isinstance(media_url, str) or not media_url.strip():
            raise ValueError("For other_poetry, prosody_metadata.media.url must be a non-empty string")

        alt_text = media.get("alt_text")
        if media_type == "image":
            if not isinstance(alt_text, str) or not alt_text.strip():
                raise ValueError("For image media, prosody_metadata.media.alt_text is required")
        elif alt_text is not None and not isinstance(alt_text, str):
            raise ValueError("For audio media, prosody_metadata.media.alt_text must be a string when provided")

        return value


class PoetryMediaSchema(BaseModel):
    type: Literal["image", "audio"]
    url: str = Field(..., min_length=1)
    alt_text: Optional[str] = None


class OtherPoetryProsodyMetadataSchema(BaseModel):
    media: Optional[PoetryMediaSchema] = None


class PoetryNodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: int
    work_id: int
    chapter_id: int
    poetry_type: str
    sequence_no: int
    main_text: str
    text_devanagari: Optional[str] = None
    text_romanized: Optional[str] = None
    meaning: Optional[str] = None
    prosody_metadata: Optional[dict[str, Any]] = None
    status: str
    visibility: str
    source_submission_id: Optional[int] = None
    created_by: Optional[int] = None
    verified_by: Optional[int] = None
    version: int
    is_deleted: bool


class PoetryNavCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    poetry_type: str
    sequence_no: int
    main_text: str


class PoetryNavOut(BaseModel):
    previous: Optional[PoetryNavCard] = None
    current: PoetryNavCard
    next: Optional[PoetryNavCard] = None


class PoetryTypeOut(BaseModel):
    id: Optional[int] = None
    poetry_type: str
    display_name: str
    family: Optional[str] = None
    is_user_defined: bool = False
    is_active: bool = True
