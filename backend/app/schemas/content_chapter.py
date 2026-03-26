from typing import Optional, List
from pydantic import BaseModel


class ChapterDohaItem(BaseModel):
    id: int
    hierarchy_path: Optional[str]
    chapter_id: Optional[int]
    number_in_chapter: Optional[int]
    main_text: str
    meaning: Optional[str]
    text_devanagari: Optional[str]
    text_romanized: Optional[str]


class ChapterDohasOut(BaseModel):
    chapter_id: int
    chapter_slug: Optional[str]
    total: int
    offset: int
    limit: int
    items: List[ChapterDohaItem]
