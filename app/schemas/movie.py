from typing import Optional

from pydantic import BaseModel


class RatingAggregate(BaseModel):
    """Rating aggregation statistics for a movie."""

    avg_rating: Optional[float] = None
    rating_count: int


class MovieListItem(BaseModel):
    """Movie item with aggregated ratings for list responses."""

    id: int
    title: str
    director_id: int
    release_year: int
    cast: Optional[str] = None
    avg_rating: Optional[float] = None
    rating_count: int


class MovieDetail(BaseModel):
    """Movie detail with aggregated ratings."""

    id: int
    title: str
    director_id: int
    release_year: int
    cast: Optional[str] = None
    avg_rating: Optional[float] = None
    rating_count: int
