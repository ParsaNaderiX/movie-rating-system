import logging
import sys


class _SafeExtraFilter(logging.Filter):
    def __init__(self, defaults: dict[str, str]) -> None:
        super().__init__()
        self._defaults = defaults

    def filter(self, record: logging.LogRecord) -> bool:
        for key, value in self._defaults.items():
            if not hasattr(record, key):
                setattr(record, key, value)
        has_movie = record.movie_id not in (None, "-", "")
        has_rating = record.rating not in (None, "-", "")
        has_route = record.route not in (None, "-", "")
        if has_movie or has_rating:
            record.context = (
                f" (movie_id={record.movie_id}, rating={record.rating}, route={record.route})"
            )
        elif has_route:
            record.context = f" (route={record.route})"
        else:
            record.context = ""
        return True


def configure_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s%(context)s"
    )

    for handler in root_logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream is sys.stdout:
            return

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(
        _SafeExtraFilter(
            defaults={
                "movie_id": "-",
                "rating": "-",
                "route": "-",
                "context": "",
            }
        )
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
