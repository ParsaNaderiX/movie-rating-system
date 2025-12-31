from fastapi import APIRouter, Depends, HTTPException, Response

from app.db.database import get_db
from app.schemas.common import SuccessResponse
from app.schemas.movie import MovieDetail, MovieUpdate
from app.services.movie import MovieService
from sqlalchemy.orm import Session

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/{movie_id}", response_model=SuccessResponse[MovieDetail])
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    """
    Get a single movie with rating aggregates.
    """
    service = MovieService(db)
    movie = service.get_movie_detail(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return SuccessResponse(data=MovieDetail(**movie))


@router.put("/{movie_id}", response_model=SuccessResponse[MovieDetail])
def update_movie(movie_id: int, payload: MovieUpdate, db: Session = Depends(get_db)):
    """
    Update a movie and its genres.
    """
    service = MovieService(db)
    movie = service.update_movie(movie_id, payload)
    return SuccessResponse(data=MovieDetail(**movie))


@router.delete("/{movie_id}", status_code=204)
def delete_movie(movie_id: int, db: Session = Depends(get_db)) -> Response:
    """
    Delete a movie and its related ratings/genres.
    """
    service = MovieService(db)
    service.delete_movie(movie_id)
    return Response(status_code=204)
