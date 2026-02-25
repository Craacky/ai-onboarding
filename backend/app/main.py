from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from starlette import status

from app.core.deps import get_db
from app.core.settings import settings

app = FastAPI(title=settings.APP_NAME)


@app.get("/health")
def health() -> dict:
    return {"status": "ok",
            "app": settings.APP_NAME,
            "env": settings.ENV
            }


@app.get("/db-health")
def db_health(db: Session = Depends(get_db)) -> dict:
    db.execute(text("SELECT 1"))
    return {"status": "ok", "db": "connected"}
