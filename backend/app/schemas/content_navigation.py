from typing import Optional

from pydantic import BaseModel


class DohaNavCard(BaseModel):
    id: int
    number_in_chapter: Optional[int]
    title: Optional[str] = None
    short_text: str


class DohaNavigationOut(BaseModel):
    previous: Optional[DohaNavCard] = None
    current: DohaNavCard
    next: Optional[DohaNavCard] = None
