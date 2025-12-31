from fastapi import FastAPI

from app.exceptions import register_exception_handlers
from app.controller import movies_router

app = FastAPI(title="Movie-Rating-System")
register_exception_handlers(app)
app.include_router(movies_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    return {"status": "success", "data": {"ok": True}}

