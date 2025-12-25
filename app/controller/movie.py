from fastapi import APIRouter, Depends, HTTPException

from app.db.database import get_db
from app.schemas.common import SuccessResponse
from app.schemas.movie import MovieDetail, MovieListItem, MovieUpdate
from app.services.movie import MovieService
from sqlalchemy.orm import Session

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("", response_model=SuccessResponse[list[MovieListItem]])
def list_movies(db: Session = Depends(get_db)):
    """
    Get all movies with rating aggregates.
    Single optimized query - no N+1 problem.
    """
    service = MovieService(db)
    movies = service.get_all_movies_with_ratings()
    return SuccessResponse(data=[MovieListItem(**movie) for movie in movies])


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
