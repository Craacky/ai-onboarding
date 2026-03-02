from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.auth import router as auth_router
from app.api.invitations import router as invitations_router
from app.core.deps import get_db
from app.core.settings import settings

app = FastAPI(title=settings.APP_NAME)
app.include_router(auth_router)
app.include_router(invitations_router)


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
