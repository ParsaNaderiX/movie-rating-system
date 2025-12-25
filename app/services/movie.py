from typing import Optional

from sqlalchemy.orm import Session

from app.exceptions import NotFoundError, ValidationError
from app.models.movie import Movie
from app.repositories.movie import MovieRepository
from app.schemas.movie import MovieUpdate


class MovieService:
    """Service for movie-related business logic."""

    def __init__(self, db: Session):
        self.repository = MovieRepository(db)

    def get_all_movies_with_ratings(self) -> list[dict]:
        """
        Retrieve all movies with their rating aggregates.
        Single query - no N+1 problem.

        Returns:
            List of movie dicts with avg_rating and rating_count.
        """
        return self.repository.get_all_with_rating_aggregates()

    def _build_movie_detail(self, movie: Movie) -> dict:
        rating_stats = self.repository.get_rating_aggregate(movie.id)
        return {
            "id": movie.id,
            "title": movie.title,
            "director_id": movie.director_id,
            "release_year": movie.release_year,
            "cast": movie.cast,
            "avg_rating": rating_stats["avg_rating"],
            "rating_count": rating_stats["rating_count"],
            "director": {
                "id": movie.director.id,
                "name": movie.director.name,
                "birth_year": movie.director.birth_year,
                "description": movie.director.description,
            },
            "genres": [
                {
                    "id": genre.id,
                    "name": genre.name,
                    "description": genre.description,
                }
                for genre in movie.genres
            ],
        }

    def get_movie_detail(self, movie_id: int) -> Optional[dict]:
        """
        Retrieve a single movie by ID with its rating aggregates.
        Uses a relation load plus an aggregate lookup.

        Args:
            movie_id: The ID of the movie to fetch.

        Returns:
            Movie dict with avg_rating and rating_count, or None if not found.
        """
        movie = self.repository.get_movie_with_relations(movie_id)
        if not movie:
            return None
        return self._build_movie_detail(movie)

    def get_rating_stats(self, movie_id: int) -> dict:
        """
        Get only rating statistics for a movie.

        Args:
            movie_id: The ID of the movie.

        Returns:
            Dict with avg_rating and rating_count.
        """
        return self.repository.get_rating_aggregate(movie_id)

    def get_rating_stats_batch(self, movie_ids: list[int]) -> dict[int, dict]:
        """
        Get rating statistics for multiple movies in a single query.

        Args:
            movie_ids: List of movie IDs.

        Returns:
            Dict mapping movie_id to {avg_rating, rating_count}.
        """
        return self.repository.get_rating_aggregates_for_movies(movie_ids)

    def update_movie(self, movie_id: int, payload: MovieUpdate) -> dict:
        movie = self.repository.get_movie_with_relations(movie_id)
        if not movie:
            raise NotFoundError("Movie not found")

        update_data = payload.model_dump(exclude_unset=True)
        genre_ids = update_data.pop("genres", None)

        for field, value in update_data.items():
            setattr(movie, field, value)

        if genre_ids is not None:
            unique_genre_ids = list(dict.fromkeys(genre_ids))
            genres = self.repository.get_genres_by_ids(unique_genre_ids)
            found_ids = {genre.id for genre in genres}
            missing_ids = sorted(set(unique_genre_ids) - found_ids)
            if missing_ids:
                self.repository.db.rollback()
                raise ValidationError(f"Genres not found: {missing_ids}")
            movie.genres = genres

        try:
            self.repository.db.commit()
        except Exception:
            self.repository.db.rollback()
            raise

        return self._build_movie_detail(movie)

    def delete_movie(self, movie_id: int) -> None:
        movie = self.repository.get_movie_by_id(movie_id)
        if not movie:
            raise NotFoundError("Movie not found")
        try:
            self.repository.delete_movie(movie_id)
            self.repository.db.commit()
        except Exception:
            self.repository.db.rollback()
            raise
