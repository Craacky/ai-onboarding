from fastapi import FastAPI
from app.core.settings import settings
app = FastAPI(title=settings.APP_NAME)


@app.get("/health")
def health() -> dict:
    return {"status": "ok",
            "app": settings.APP_NAME,
            "env": settings.ENV
            }
