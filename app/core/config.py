"""
Configuración central de la aplicación.

Todo lo que cambia entre "mi computadora" y "Render + Supabase" vive aquí,
leído desde variables de entorno (archivo .env). Así el código nunca
cambia al mover la app de un lado a otro — solo cambia el .env.

Mismo patrón que app/core/config.py del proyecto "asistente".
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Identidad de la app
    app_name: str = "Electroplast · Inspecciones Monta Cargas"
    environment: str = "local"  # local | production

    # Base de datos. SQLite por defecto para desarrollo local (cero
    # configuración). En producción, DATABASE_URL apunta a Supabase
    # (Postgres), por ejemplo:
    #   postgresql+psycopg://usuario:clave@host:5432/postgres
    database_url: str = "sqlite:///./data/app.db"

    # Se agrega automáticamente a los encabezados de las páginas para
    # distinguir a simple vista el ambiente local del de producción.
    mostrar_aviso_entorno: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
