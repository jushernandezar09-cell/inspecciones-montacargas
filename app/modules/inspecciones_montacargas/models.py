"""
Modelo de datos de "Inspecciones Diarias Monta Cargas" (F01-I28-P-IF-02).

Una fila de esta tabla = una celda de día+turno de la hoja de papel, para
un equipo/mes/año específico. Los 31 días x 2 turnos de una hoja son 62
filas posibles; solo existen en la base de datos las que ya se llenaron
(las demás se muestran vacías en pantalla, igual que en el papel en blanco).

Las columnas del checklist (cadenas_rodillos, nivel_aceite_frenos, etc.)
están definidas en app/modules/inspecciones_montacargas/formulario.py —
ese archivo es la fuente de verdad de nombres/orden/etiquetas. Si se
agrega una columna ahí, se agrega aquí también (mismo "clave") y se corre
un ALTER TABLE en Supabase (ver scripts/supabase_schema.sql).
"""
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class InspeccionMontacargas(Base):
    """Una celda día+turno llena (o en edición) de la hoja de un equipo/mes/año."""

    __tablename__ = "inspecciones_montacargas"
    __table_args__ = (
        # Un equipo no puede tener dos filas para el mismo día+turno del
        # mismo mes/año — guardar de nuevo esa combinación actualiza la
        # fila existente (upsert), nunca crea un duplicado.
        UniqueConstraint("codigo_equipo", "anio", "mes", "dia", "turno", name="uq_hoja_dia_turno"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Identifican a qué "hoja" (equipo + mes + año) pertenece esta fila.
    codigo_equipo: Mapped[str] = mapped_column(String(80), index=True)
    anio: Mapped[int] = mapped_column(Integer, index=True)
    mes: Mapped[int] = mapped_column(Integer, index=True)  # 1-12
    dia: Mapped[int] = mapped_column(Integer)  # 1-31
    turno: Mapped[str] = mapped_column(String(1))  # "D" o "N"

    # --- Columna "Datos" ---
    responsable_revision: Mapped[str] = mapped_column(String(150), default="")

    # --- Mecanica ---
    cadenas_rodillos: Mapped[str] = mapped_column(String(5), default="")
    nivel_aceite_frenos: Mapped[str] = mapped_column(String(5), default="")
    fugas_aceite: Mapped[str] = mapped_column(String(5), default="")
    freno_mano: Mapped[str] = mapped_column(String(5), default="")
    horas_registradas: Mapped[str] = mapped_column(String(20), default="")
    juego_pedales: Mapped[str] = mapped_column(String(5), default="")

    # --- Cabina Montacargas ---
    mandos_hidraulicos: Mapped[str] = mapped_column(String(5), default="")
    temperatura_rango: Mapped[str] = mapped_column(String(5), default="")
    instrumentos_panel: Mapped[str] = mapped_column(String(5), default="")
    direccionales: Mapped[str] = mapped_column(String(5), default="")

    # --- Seguridad ---
    mecanismos_seguridad: Mapped[str] = mapped_column(String(5), default="")
    luces_freno_marcha: Mapped[str] = mapped_column(String(5), default="")
    extintor: Mapped[str] = mapped_column(String(5), default="")

    # --- Estado de correccion ---
    se_corrige: Mapped[str] = mapped_column(String(5), default="")
    responsable_correccion: Mapped[str] = mapped_column(String(150), default="")
    fecha_correccion: Mapped[str] = mapped_column(String(20), default="")  # texto "YYYY-MM-DD" o ""

    actualizado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
