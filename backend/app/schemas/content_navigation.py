from typing import Optional

from pydantic import BaseModel


class ContentNavCard(BaseModel):
    id: int
    number_in_chapter: Optional[int]
    content_type: Optional[str] = None
    title: Optional[str] = None
    short_text: str


class ContentNavigationOut(BaseModel):
    previous: Optional[ContentNavCard] = None
    current: ContentNavCard
    next: Optional[ContentNavCard] = None


# Backwards-compatible aliases for existing Doha endpoint imports.
DohaNavCard = ContentNavCard
DohaNavigationOut = ContentNavigationOut
