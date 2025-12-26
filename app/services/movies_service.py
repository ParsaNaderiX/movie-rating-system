from typing import Optional

from sqlalchemy.orm import Session

from app.exceptions import NotFoundError, ValidationError
from app.schemas.movie import MovieCreateIn
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

    def create_movie(self, payload: MovieCreateIn) -> dict:
        director = self.repository.get_director_by_id(payload.director_id)
        if not director:
            raise ValidationError("Director not found")

        unique_genre_ids = list(dict.fromkeys(payload.genres))
        genres = self.repository.get_genres_by_ids(unique_genre_ids)
        found_ids = {genre.id for genre in genres}
        missing_ids = sorted(set(unique_genre_ids) - found_ids)
        if missing_ids:
            raise ValidationError(f"Genres not found: {missing_ids}")

        try:
            movie = self.repository.create_movie(
                title=payload.title,
                director_id=payload.director_id,
                release_year=payload.release_year,
                cast=payload.cast,
                genres=genres,
            )
            self.repository.db.commit()
        except Exception:
            self.repository.db.rollback()
            raise

        movie_detail, aggregate = self.repository.get_movie_detail(movie.id)
        if not movie_detail:
            raise NotFoundError("Movie not found")

        return {
            "id": movie_detail.id,
            "title": movie_detail.title,
            "release_year": movie_detail.release_year,
            "director": {
                "id": movie_detail.director.id,
                "name": movie_detail.director.name,
                "birth_year": movie_detail.director.birth_year,
                "description": movie_detail.director.description,
            },
            "genres": [genre_item.name for genre_item in movie_detail.genres],
            "cast": movie_detail.cast,
            "average_rating": aggregate["average_rating"],
            "ratings_count": aggregate["ratings_count"],
        }
