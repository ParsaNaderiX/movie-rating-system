from typing import Optional

from sqlalchemy import Float, func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.director import Director
from app.models.genre import Genre
from app.models.movie import Movie
from app.models.movie_rating import MovieRating


class MoviesRepository:
    """Repository for list-oriented movie queries with filters and aggregates."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_movies(
        self,
        *,
        page: int,
        page_size: int,
        title: Optional[str] = None,
        release_year: Optional[int] = None,
        genre: Optional[str] = None,
    ) -> tuple[int, list[Movie], dict[int, dict]]:
        base_query = select(Movie.id)

        if title:
            base_query = base_query.where(Movie.title.ilike(f"%{title}%"))
        if release_year is not None:
            base_query = base_query.where(Movie.release_year == release_year)
        if genre:
            base_query = base_query.join(Movie.genres).where(
                func.lower(Genre.name) == func.lower(genre),
            )

        base_query = base_query.distinct()

        total_items = self.db.execute(
            select(func.count()).select_from(base_query.subquery()),
        ).scalar_one()

        offset = (page - 1) * page_size
        page_query = (
            base_query.order_by(Movie.id)
            .offset(offset)
            .limit(page_size)
        )
        movie_ids = [row.id for row in self.db.execute(page_query).all()]
        if not movie_ids:
            return total_items, [], {}

        movies_query = (
            select(Movie)
            .options(joinedload(Movie.director), selectinload(Movie.genres))
            .where(Movie.id.in_(movie_ids))
        )
        movies = self.db.execute(movies_query).scalars().all()

        aggregates_query = (
            select(
                MovieRating.movie_id,
                func.avg(MovieRating.score).cast(Float).label("average_rating"),
                func.count(MovieRating.id).label("ratings_count"),
            )
            .where(MovieRating.movie_id.in_(movie_ids))
            .group_by(MovieRating.movie_id)
        )
        aggregates = self.db.execute(aggregates_query).all()
        aggregates_map = {
            row.movie_id: {
                "average_rating": row.average_rating,
                "ratings_count": row.ratings_count,
            }
            for row in aggregates
        }

        movie_by_id = {movie.id: movie for movie in movies}
        ordered_movies = [movie_by_id[movie_id] for movie_id in movie_ids if movie_id in movie_by_id]
        return total_items, ordered_movies, aggregates_map

    def get_movie_detail(self, movie_id: int) -> tuple[Optional[Movie], dict]:
        movie_query = (
            select(Movie)
            .options(joinedload(Movie.director), selectinload(Movie.genres))
            .where(Movie.id == movie_id)
        )
        movie = self.db.execute(movie_query).scalars().first()
        if not movie:
            return None, {"average_rating": None, "ratings_count": 0}

        aggregate_query = (
            select(
                func.avg(MovieRating.score).cast(Float).label("average_rating"),
                func.count(MovieRating.id).label("ratings_count"),
            )
            .where(MovieRating.movie_id == movie_id)
        )
        aggregate_row = self.db.execute(aggregate_query).first()
        return movie, {
            "average_rating": aggregate_row.average_rating if aggregate_row else None,
            "ratings_count": aggregate_row.ratings_count if aggregate_row else 0,
        }

    def get_director_by_id(self, director_id: int) -> Optional[Director]:
        query = select(Director).where(Director.id == director_id)
        return self.db.execute(query).scalars().first()

    def get_movie_by_id(self, movie_id: int) -> Optional[Movie]:
        query = select(Movie).where(Movie.id == movie_id)
        return self.db.execute(query).scalars().first()

    def get_genres_by_ids(self, genre_ids: list[int]) -> list[Genre]:
        if not genre_ids:
            return []
        query = select(Genre).where(Genre.id.in_(genre_ids))
        return self.db.execute(query).scalars().all()

    def create_movie(
        self,
        *,
        title: str,
        director_id: int,
        release_year: int,
        cast: Optional[str],
        genres: list[Genre],
    ) -> Movie:
        movie = Movie(
            title=title,
            director_id=director_id,
            release_year=release_year,
            cast=cast,
        )
        movie.genres = genres
        self.db.add(movie)
        self.db.flush()
        return movie

    def create_rating(self, *, movie_id: int, score: int) -> MovieRating:
        rating = MovieRating(movie_id=movie_id, score=score)
        self.db.add(rating)
        self.db.flush()
        return rating
