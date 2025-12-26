from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


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


class DirectorOut(BaseModel):
    id: int
    name: str
    birth_year: Optional[int] = None
    description: Optional[str] = None


class DirectorSummaryOut(BaseModel):
    id: int
    name: str


class MovieListItemOut(BaseModel):
    id: int
    title: str
    release_year: int
    director: DirectorSummaryOut
    genres: list[str] = Field(default_factory=list)
    average_rating: Optional[float] = Field(default=None, validation_alias="avg_rating")
    ratings_count: int = Field(default=0, validation_alias="rating_count")

    @field_validator("genres", mode="before")
    @classmethod
    def _coerce_genres(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            if not value:
                return []
            if isinstance(value[0], str):
                return value
            if isinstance(value[0], dict) and "name" in value[0]:
                return [item["name"] for item in value if isinstance(item, dict) and "name" in item]
        return value


class MovieListPageOut(BaseModel):
    page: int
    page_size: int
    total_items: int
    items: list[MovieListItemOut] = Field(default_factory=list)


class MovieDetailOut(BaseModel):
    id: int
    title: str
    release_year: int
    director: DirectorOut
    genres: list[str] = Field(default_factory=list)
    cast: Optional[str] = None
    average_rating: Optional[float] = Field(default=None, validation_alias="avg_rating")
    ratings_count: int = Field(default=0, validation_alias="rating_count")

    @field_validator("genres", mode="before")
    @classmethod
    def _coerce_genres(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            if not value:
                return []
            if isinstance(value[0], str):
                return value
            if isinstance(value[0], dict) and "name" in value[0]:
                return [item["name"] for item in value if isinstance(item, dict) and "name" in item]
        return value


class MovieCreateIn(BaseModel):
    title: str
    director_id: int
    release_year: int
    cast: Optional[str] = None
    genres: list[int] = Field(default_factory=list)


class MovieUpdateIn(BaseModel):
    title: Optional[str] = None
    release_year: Optional[int] = None
    cast: Optional[str] = None
    genres: Optional[list[int]] = None


class RatingCreateIn(BaseModel):
    score: int = Field(..., ge=1, le=10)


class RatingOut(BaseModel):
    id: int
    movie_id: int
    score: int
    created_at: datetime
