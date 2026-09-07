"""
Rutas de "Inspecciones Diarias Monta Cargas".

No requiere inicio de sesión (a propósito: es una hoja de uso compartido en
planta, igual que la de papel). Cualquiera con la URL puede abrir una hoja
y llenarla.

Flujo:
  GET  /                          -> elegir/crear equipo + mes + año
  GET  /hoja?codigo=&mes=&anio=   -> la hoja completa (réplica del PDF)
  GET  /hoja/datos?...            -> JSON con las filas guardadas (para "recargar")
  POST /hoja/fila                 -> guarda (upsert) una sola fila día+turno
  GET  /api/equipos               -> códigos de equipo ya usados (autocompletar)
"""
import calendar
from datetime import datetime, date

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, distinct

from app.core.database import get_db
from app.core.config import get_settings
from app.modules.inspecciones_montacargas.models import InspeccionMontacargas
from app.modules.inspecciones_montacargas.formulario import (
    DOCUMENTO,
    TURNOS,
    MESES,
    OPCIONES_SI_NO,
    GRUPOS_CHECKLIST,
    claves_checklist,
)

router = APIRouter(tags=["inspecciones_montacargas"])
templates = Jinja2Templates(directory="app/templates")
settings = get_settings()


def _dias_del_mes(anio: int, mes: int) -> int:
    try:
        return calendar.monthrange(anio, mes)[1]
    except Exception:
        return 31


@router.get("/", response_class=HTMLResponse)
def inicio(request: Request, db: Session = Depends(get_db)):
    equipos = [
        row[0]
        for row in db.execute(
            select(distinct(InspeccionMontacargas.codigo_equipo)).order_by(InspeccionMontacargas.codigo_equipo)
        ).all()
    ]
    hoy = date.today()
    return templates.TemplateResponse(
        "inicio.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "environment": settings.environment,
            "documento": DOCUMENTO,
            "equipos": equipos,
            "meses": MESES,
            "mes_actual": hoy.month,
            "anio_actual": hoy.year,
        },
    )


@router.get("/hoja", response_class=HTMLResponse)
def ver_hoja(request: Request, codigo: str, mes: int, anio: int, db: Session = Depends(get_db)):
    codigo = (codigo or "").strip()
    if not codigo or mes < 1 or mes > 12 or anio < 2000:
        raise HTTPException(status_code=400, detail="Código de equipo, mes o año inválido.")

    total_dias = _dias_del_mes(anio, mes)

    filas_guardadas = {
        (f.dia, f.turno): f
        for f in db.execute(
            select(InspeccionMontacargas).where(
                InspeccionMontacargas.codigo_equipo == codigo,
                InspeccionMontacargas.anio == anio,
                InspeccionMontacargas.mes == mes,
            )
        ).scalars()
    }

    # Arma los 31 (o los que tenga el mes) días x 2 turnos, con lo guardado
    # o vacío si esa celda todavía no se ha llenado (igual que el papel).
    dias = []
    for dia in range(1, total_dias + 1):
        turnos = []
        for turno in TURNOS:
            fila = filas_guardadas.get((dia, turno))
            valores = {clave: getattr(fila, clave) for clave in claves_checklist()} if fila else {
                clave: "" for clave in claves_checklist()
            }
            turnos.append(
                {
                    "turno": turno,
                    "responsable_revision": fila.responsable_revision if fila else "",
                    "valores": valores,
                    "guardado": fila is not None,
                }
            )
        dias.append({"dia": dia, "turnos": turnos})

    return templates.TemplateResponse(
        "inspecciones_montacargas/hoja.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "environment": settings.environment,
            "documento": DOCUMENTO,
            "opciones_si_no": OPCIONES_SI_NO,
            "meses": MESES,
            "grupos_checklist": GRUPOS_CHECKLIST,
            "codigo_equipo": codigo,
            "mes": mes,
            "anio": anio,
            "mes_nombre": MESES[mes - 1],
            "dias": dias,
        },
    )


@router.get("/hoja/datos")
def datos_hoja(codigo: str, mes: int, anio: int, db: Session = Depends(get_db)):
    """JSON con lo guardado hasta ahora — lo usa el botón «Recargar» para
    traer cambios hechos desde otro dispositivo sin perder lo que el
    usuario está escribiendo en filas que no ha guardado."""
    filas = db.execute(
        select(InspeccionMontacargas).where(
            InspeccionMontacargas.codigo_equipo == codigo,
            InspeccionMontacargas.anio == anio,
            InspeccionMontacargas.mes == mes,
        )
    ).scalars()

    resultado = {}
    for f in filas:
        resultado[f"{f.dia}-{f.turno}"] = {
            "responsable_revision": f.responsable_revision,
            **{clave: getattr(f, clave) for clave in claves_checklist()},
            "actualizado_en": f.actualizado_en.isoformat() if f.actualizado_en else None,
        }
    return JSONResponse(resultado)


class FilaEntrada(BaseModel):
    codigo_equipo: str
    anio: int
    mes: int
    dia: int
    turno: str
    responsable_revision: str = ""
    valores: dict[str, str] = {}


@router.post("/hoja/fila")
def guardar_fila(entrada: FilaEntrada, db: Session = Depends(get_db)):
    codigo = (entrada.codigo_equipo or "").strip()
    if not codigo:
        raise HTTPException(status_code=400, detail="Falta el código de equipo.")
    if entrada.turno not in TURNOS:
        raise HTTPException(status_code=400, detail="Turno inválido.")
    if not (1 <= entrada.dia <= 31):
        raise HTTPException(status_code=400, detail="Día inválido.")

    claves_validas = set(claves_checklist())

    fila = db.execute(
        select(InspeccionMontacargas).where(
            InspeccionMontacargas.codigo_equipo == codigo,
            InspeccionMontacargas.anio == entrada.anio,
            InspeccionMontacargas.mes == entrada.mes,
            InspeccionMontacargas.dia == entrada.dia,
            InspeccionMontacargas.turno == entrada.turno,
        )
    ).scalar_one_or_none()

    if fila is None:
        fila = InspeccionMontacargas(
            codigo_equipo=codigo,
            anio=entrada.anio,
            mes=entrada.mes,
            dia=entrada.dia,
            turno=entrada.turno,
        )
        db.add(fila)

    fila.responsable_revision = (entrada.responsable_revision or "").strip()
    for clave, valor in entrada.valores.items():
        if clave in claves_validas:
            setattr(fila, clave, (valor or "").strip())

    fila.actualizado_en = datetime.utcnow()
    db.commit()
    db.refresh(fila)

    return {"ok": True, "actualizado_en": fila.actualizado_en.isoformat()}


@router.get("/api/equipos")
def api_equipos(db: Session = Depends(get_db)):
    equipos = [
        row[0]
        for row in db.execute(
            select(distinct(InspeccionMontacargas.codigo_equipo)).order_by(InspeccionMontacargas.codigo_equipo)
        ).all()
    ]
    return {"equipos": equipos}
