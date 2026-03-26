"""
Slug normalization utility for hierarchy URLs.

Ensures all author/work/chapter slugs follow a consistent format:
- Lowercase
- Alphanumeric and hyphens only
- No leading/trailing whitespace or hyphens
- Consistent transformation for deduplication
"""

import re
import unicodedata
from typing import Optional


def normalize_slug(slug: Optional[str]) -> str:
    """
    Normalize a slug to lowercase, alphanumeric + hyphens.
    
    Args:
        slug: Raw user input slug
        
    Returns:
        Normalized slug safe for URLs and unique lookups
        
    Examples:
        >>> normalize_slug("Ramayan")
        'ramayan'
        >>> normalize_slug("The Hanuman Chalisa")
        'the-hanuman-chalisa'
        >>> normalize_slug("Hello_World!")
        'hello-world'
    """
    if not slug:
        return ""
    
    # Convert to string and strip whitespace
    slug = str(slug).strip()
    
    # Normalize Unicode characters (decompose accents)
    slug = unicodedata.normalize('NFKD', slug)
    slug = slug.encode('ascii', 'ignore').decode('ascii')
    
    # Convert to lowercase
    slug = slug.lower()
    
    # Replace spaces, underscores, and other special chars with hyphens
    slug = re.sub(r'[^a-z0-9-]', '-', slug)
    
    # Collapse multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    
    # Remove leading and trailing hyphens
    slug = slug.strip('-')
    
    return slug


def validate_slug_format(slug: str) -> bool:
    """
    Validate that a slug conforms to normalized format.
    
    Useful for pre-validation before storing or comparing.
    
    Args:
        slug: Slug to validate
        
    Returns:
        True if slug is already normalized, False otherwise
    """
    if not slug:
        return False
    
    # Check if slug matches normalized pattern
    pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
    return bool(re.match(pattern, slug))


def is_same_slug(slug1: Optional[str], slug2: Optional[str]) -> bool:
    """
    Check if two slugs refer to the same entity (case-insensitive comparison).
    
    Args:
        slug1: First slug
        slug2: Second slug
        
    Returns:
        True if both normalize to the same value
    """
    return normalize_slug(slug1) == normalize_slug(slug2)


def slugify(text: Optional[str]) -> str:
    """
    Convert arbitrary text to a valid slug. Alias for normalize_slug.
    
    Args:
        text: Text to convert
        
    Returns:
        Normalized slug
    """
    return normalize_slug(text)
