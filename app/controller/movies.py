import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.common import SuccessResponse
from app.schemas.movie import MovieCreateIn, MovieDetailOut, MovieListPageOut, MovieUpdate, RatingCreateIn, RatingOut
from app.services.movie import MovieService
from app.services.movies_service import MoviesService

router = APIRouter(prefix="/api/v1/movies", tags=["Movies"])
logger = logging.getLogger(__name__)


@router.get("", response_model=SuccessResponse[MovieListPageOut])
def list_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    title: Optional[str] = None,
    release_year: Optional[int] = None,
    genre: Optional[str] = None,
    db: Session = Depends(get_db),
):
    route = "/api/v1/movies"
    params = {
        "page": page,
        "page_size": page_size,
        "title": title,
        "release_year": release_year,
        "genre": genre,
    }
    logger.info("Listing movies", extra={"route": route, **params})
    try:
        service = MoviesService(db)
        payload = service.list_movies(
            page=page,
            page_size=page_size,
            title=title,
            release_year=release_year,
            genre=genre,
        )
        logger.info(
            "Movies listed successfully",
            extra={
                "route": route,
                "total_items": payload.get("total_items"),
                "returned_count": len(payload.get("items", [])),
                "page": page,
                "page_size": page_size,
            },
        )
        return SuccessResponse(data=payload)
    except Exception:
        logger.error(
            "Failed to list movies",
            exc_info=True,
            extra={"route": route, **params},
        )
        raise


@router.get("/{movie_id}", response_model=SuccessResponse[MovieDetailOut])
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    service = MoviesService(db)
    payload = service.get_movie_detail(movie_id)
    return SuccessResponse(data=payload)


@router.put("/{movie_id}", response_model=SuccessResponse[MovieDetailOut])
def update_movie(movie_id: int, payload: MovieUpdate, db: Session = Depends(get_db)):
    service = MovieService(db)
    movie = service.update_movie(movie_id, payload)
    return SuccessResponse(data=movie)


@router.delete("/{movie_id}", status_code=204)
def delete_movie(movie_id: int, db: Session = Depends(get_db)) -> Response:
    service = MovieService(db)
    service.delete_movie(movie_id)
    return Response(status_code=204)


@router.post("", response_model=SuccessResponse[MovieDetailOut], status_code=201)
def create_movie(payload: MovieCreateIn, db: Session = Depends(get_db)):
    service = MoviesService(db)
    movie = service.create_movie(payload)
    return SuccessResponse(data=movie)


@router.post("/{movie_id}/ratings", response_model=SuccessResponse[RatingOut], status_code=201)
def create_rating(movie_id: int, payload: RatingCreateIn, db: Session = Depends(get_db)):
    service = MoviesService(db)
    rating = service.create_rating(movie_id, payload)
    return SuccessResponse(data=rating)
