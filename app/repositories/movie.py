from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.movie import Movie
from app.models.movie_rating import MovieRating


class MovieRepository:
    """Repository for movie-related queries with rating aggregations."""

    def __init__(self, db: Session):
        self.db = db

    def get_all_with_rating_aggregates(self) -> list[dict]:
        """
        Fetch all movies with rating aggregates (average score and count).
        Uses a single query with a left outer join to avoid N+1 queries.

        Returns:
            List of dicts with keys: id, title, director_id, release_year, cast,
                                     avg_rating, rating_count
        """
        query = select(
            Movie.id,
            Movie.title,
            Movie.director_id,
            Movie.release_year,
            Movie.cast,
            func.avg(MovieRating.score).cast(float).label("avg_rating"),
            func.count(MovieRating.id).label("rating_count"),
        ).outerjoin(
            MovieRating,
            Movie.id == MovieRating.movie_id,
        ).group_by(
            Movie.id,
            Movie.title,
            Movie.director_id,
            Movie.release_year,
            Movie.cast,
        )

        result = self.db.execute(query).fetchall()
        return [
            {
                "id": row.id,
                "title": row.title,
                "director_id": row.director_id,
                "release_year": row.release_year,
                "cast": row.cast,
                "avg_rating": row.avg_rating,
                "rating_count": row.rating_count if row.rating_count else 0,
            }
            for row in result
        ]

    def get_by_id_with_rating_aggregate(
        self,
        movie_id: int,
    ) -> Optional[dict]:
        """
        Fetch a single movie by ID with its rating aggregates.
        Uses a single query with a left outer join.

        Args:
            movie_id: The ID of the movie to fetch.

        Returns:
            Dict with keys: id, title, director_id, release_year, cast,
                           avg_rating, rating_count
            Returns None if movie not found.
        """
        query = select(
            Movie.id,
            Movie.title,
            Movie.director_id,
            Movie.release_year,
            Movie.cast,
            func.avg(MovieRating.score).cast(float).label("avg_rating"),
            func.count(MovieRating.id).label("rating_count"),
        ).where(
            Movie.id == movie_id,
        ).outerjoin(
            MovieRating,
            Movie.id == MovieRating.movie_id,
        ).group_by(
            Movie.id,
            Movie.title,
            Movie.director_id,
            Movie.release_year,
            Movie.cast,
        )

        result = self.db.execute(query).first()
        if result is None:
            return None

        return {
            "id": result.id,
            "title": result.title,
            "director_id": result.director_id,
            "release_year": result.release_year,
            "cast": result.cast,
            "avg_rating": result.avg_rating,
            "rating_count": result.rating_count if result.rating_count else 0,
        }

    def get_rating_aggregate(
        self,
        movie_id: int,
    ) -> dict:
        """
        Get only the aggregated rating statistics for a movie.

        Args:
            movie_id: The ID of the movie.

        Returns:
            Dict with keys: avg_rating (float or None), rating_count (int)
        """
        query = select(
            func.avg(MovieRating.score).cast(float).label("avg_rating"),
            func.count(MovieRating.id).label("rating_count"),
        ).where(
            MovieRating.movie_id == movie_id,
        )

        result = self.db.execute(query).first()
        return {
            "avg_rating": result.avg_rating if result else None,
            "rating_count": result.rating_count if result else 0,
        }

    def get_rating_aggregates_for_movies(
        self,
        movie_ids: list[int],
    ) -> dict[int, dict]:
        """
        Get rating aggregates for multiple movies.
        Returns a mapping of movie_id to its aggregates.

        Args:
            movie_ids: List of movie IDs.

        Returns:
            Dict mapping movie_id to {avg_rating, rating_count}
        """
        if not movie_ids:
            return {}

        query = select(
            MovieRating.movie_id,
            func.avg(MovieRating.score).cast(float).label("avg_rating"),
            func.count(MovieRating.id).label("rating_count"),
        ).where(
            MovieRating.movie_id.in_(movie_ids),
        ).group_by(
            MovieRating.movie_id,
        )

        results = self.db.execute(query).fetchall()

        aggregates = {movie_id: {"avg_rating": None, "rating_count": 0} for movie_id in movie_ids}
        for row in results:
            aggregates[row.movie_id] = {
                "avg_rating": row.avg_rating,
                "rating_count": row.rating_count,
            }

        return aggregates
