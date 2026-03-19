# app/api/v1/recommendations.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.recommendation_service import get_recommendations

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{content_type}/{content_id}")
def recommend(
    content_type: str,
    content_id: int,
    limit: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Get related content recommendations.
    - Pure read
    - Preview objects
    - Empty list if none found
    """
    return {
        "source": {"type": content_type, "id": content_id},
        "results": get_recommendations(
            db=db,
            content_type=content_type,
            content_id=content_id,
            limit=limit,
        ),
    }
