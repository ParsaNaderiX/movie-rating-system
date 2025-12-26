from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.common import SuccessResponse
from app.schemas.movie import MovieListPageOut
from app.services.movies_service import MoviesService

router = APIRouter(prefix="/api/v1/movies", tags=["movies"])


@router.get("", response_model=SuccessResponse[MovieListPageOut])
def list_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    title: Optional[str] = None,
    release_year: Optional[int] = None,
    genre: Optional[str] = None,
    db: Session = Depends(get_db),
):
    service = MoviesService(db)
    payload = service.list_movies(
        page=page,
        page_size=page_size,
        title=title,
        release_year=release_year,
        genre=genre,
    )
    return SuccessResponse(data=payload)
