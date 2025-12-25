from typing import Optional

from pydantic import BaseModel, Field


class RatingAggregate(BaseModel):
    """Rating aggregation statistics for a movie."""

    avg_rating: Optional[float] = None
    rating_count: int


class DirectorInfo(BaseModel):
    id: int
    name: str
    birth_year: Optional[int] = None
    description: Optional[str] = None


class GenreInfo(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


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
    director: DirectorInfo
    genres: list[GenreInfo] = Field(default_factory=list)


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    release_year: Optional[int] = None
    cast: Optional[str] = None
    genres: Optional[list[int]] = None
