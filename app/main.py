from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.database import Base, engine
from app.modules.inspecciones_montacargas.router import router as inspecciones_router

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(inspecciones_router)


@app.on_event("startup")
def on_startup():
    # Crea las tablas si no existen. Para un solo formulario esto basta;
    # si el esquema cambia seguido más adelante, conviene pasar a Alembic.
    Base.metadata.create_all(bind=engine)


@app.get("/salud")
def salud():
    """Endpoint simple para que Render (o quien sea) confirme que la app está viva."""
    return {"status": "ok", "app": settings.app_name}
