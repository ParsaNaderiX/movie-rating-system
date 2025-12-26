from typing import Optional

from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.repositories.movies_repository import MoviesRepository


class MoviesService:
    """Service for paginated movie listing with filters."""

    def __init__(self, db: Session) -> None:
        self.repository = MoviesRepository(db)

    def list_movies(
        self,
        *,
        page: int,
        page_size: int,
        title: Optional[str] = None,
        release_year: Optional[int] = None,
        genre: Optional[str] = None,
    ) -> dict:
        total_items, movies, aggregates = self.repository.list_movies(
            page=page,
            page_size=page_size,
            title=title,
            release_year=release_year,
            genre=genre,
        )

        items = []
        for movie in movies:
            rating = aggregates.get(movie.id, {"average_rating": None, "ratings_count": 0})
            items.append(
                {
                    "id": movie.id,
                    "title": movie.title,
                    "release_year": movie.release_year,
                    "director": {
                        "id": movie.director.id,
                        "name": movie.director.name,
                    },
                    "genres": [genre_item.name for genre_item in movie.genres],
                    "average_rating": rating["average_rating"],
                    "ratings_count": rating["ratings_count"],
                }
            )

        return {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "items": items,
        }

    def get_movie_detail(self, movie_id: int) -> dict:
        movie, aggregate = self.repository.get_movie_detail(movie_id)
        if not movie:
            raise NotFoundError("Movie not found")

        return {
            "id": movie.id,
            "title": movie.title,
            "release_year": movie.release_year,
            "director": {
                "id": movie.director.id,
                "name": movie.director.name,
                "birth_year": movie.director.birth_year,
                "description": movie.director.description,
            },
            "genres": [genre_item.name for genre_item in movie.genres],
            "cast": movie.cast,
            "average_rating": aggregate["average_rating"],
            "ratings_count": aggregate["ratings_count"],
        }
