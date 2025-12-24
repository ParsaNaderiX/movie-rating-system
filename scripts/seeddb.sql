-- Dev seed data for movie-rating-system
-- Inserts consistent with models in app/models

BEGIN;

-- Directors
INSERT INTO directors (id, name, birth_year, description) VALUES
  (1, 'Christopher Nolan', 1970, 'Writer/director known for complex high-concept films'),
  (2, 'Greta Gerwig', 1983, 'Director and actor, focuses on character-driven dramas');

-- Genres
INSERT INTO genres (id, name, description) VALUES
  (1, 'Drama', 'Character driven stories'),
  (2, 'Sci-Fi', 'Science fiction and speculative narratives'),
  (3, 'Comedy', 'Humorous films');

-- Movies
INSERT INTO movies (id, title, director_id, release_year, cast) VALUES
  (1, 'Inception', 1, 2010, 'Leonardo DiCaprio, Joseph Gordon-Levitt'),
  (2, 'Little Women', 2, 2019, 'Saoirse Ronan, Emma Watson'),
  (3, 'Interstellar', 1, 2014, 'Matthew McConaughey, Anne Hathaway');

-- Movie <-> Genre relationships
INSERT INTO movie_genres (movie_id, genre_id) VALUES
  (1, 2), -- Inception -> Sci-Fi
  (1, 1), -- Inception -> Drama
  (3, 2), -- Interstellar -> Sci-Fi
  (3, 1), -- Interstellar -> Drama
  (2, 1), -- Little Women -> Drama
  (2, 3); -- Little Women -> Comedy (light touch)

-- Ratings
INSERT INTO movie_ratings (id, movie_id, score, created_at) VALUES
  (1, 1, 9, now()),
  (2, 1, 8, now()),
  (3, 3, 10, now()),
  (4, 2, 7, now());

-- Ensure sequences (if tables use serial sequences) are set past max(id)
SELECT setval(pg_get_serial_sequence('directors','id'), COALESCE((SELECT max(id) FROM directors),0));
SELECT setval(pg_get_serial_sequence('genres','id'), COALESCE((SELECT max(id) FROM genres),0));
SELECT setval(pg_get_serial_sequence('movies','id'), COALESCE((SELECT max(id) FROM movies),0));
SELECT setval(pg_get_serial_sequence('movie_ratings','id'), COALESCE((SELECT max(id) FROM movie_ratings),0));

COMMIT;
