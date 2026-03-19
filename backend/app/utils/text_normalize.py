# app/utils/text_normalize.py
import unicodedata
import re
from typing import Optional

def normalize_roman(text: Optional[str]) -> Optional[str]:
    """
    Roman normalization:
    - Unicode NFKD
    - Remove diacritics
    - Lowercase
    - Remove punctuation
    - Collapse spaces
    """
    if not text:
        return None

    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text or None
