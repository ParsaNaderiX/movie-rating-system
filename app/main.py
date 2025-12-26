from fastapi import FastAPI

from app.exceptions import register_exception_handlers
from app.controller import movie_router, movies_router

app = FastAPI()
register_exception_handlers(app)
app.include_router(movie_router)
app.include_router(movies_router)


@app.get("/health")
def health_check() -> dict:
    return {"status": "success", "data": {"ok": True}}

