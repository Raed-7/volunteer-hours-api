from fastapi import FastAPI

from app.core.config import get_settings
from app.routers import admin, analytics, attendance, auth, events, volunteers

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")

app.include_router(auth.router)
app.include_router(volunteers.router)
app.include_router(events.router)
app.include_router(attendance.router)
app.include_router(analytics.router)
app.include_router(admin.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
