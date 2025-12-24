from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

movie_genres = Table(
    "movie_genres",
    Base.metadata,
    Column(
        "movie_id",
        Integer,
        ForeignKey("movies.id"),
        primary_key=True,
    ),
    Column(
        "genre_id",
        Integer,
        ForeignKey("genres.id"),
        primary_key=True,
    ),
)


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    director_id: Mapped[int] = mapped_column(
        ForeignKey("directors.id"),
        nullable=False,
    )
    release_year: Mapped[int] = mapped_column(Integer, nullable=False)
    cast: Mapped[str | None] = mapped_column(Text, nullable=True)

    director: Mapped["Director"] = relationship(back_populates="movies")
    genres: Mapped[list["Genre"]] = relationship(
        secondary=movie_genres,
        back_populates="movies",
    )
    ratings: Mapped[list["MovieRating"]] = relationship(back_populates="movie")
