from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.movie import MovieRepository


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

    def get_movie_detail(self, movie_id: int) -> Optional[dict]:
        """
        Retrieve a single movie by ID with its rating aggregates.
        Single query - no N+1 problem.

        Args:
            movie_id: The ID of the movie to fetch.

        Returns:
            Movie dict with avg_rating and rating_count, or None if not found.
        """
        return self.repository.get_by_id_with_rating_aggregate(movie_id)

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
