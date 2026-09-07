"""
Definición del formulario "F01-I28-P-IF-02 · Inspecciones Diarias Monta Cargas".

Este archivo es la ÚNICA fuente de verdad sobre cómo se ve y qué columnas
tiene el documento controlado. La plantilla (hoja.html) y el backend
(router.py, models.py) leen de aquí — nunca hardcodean etiquetas ni orden
de columnas por su cuenta.

Por qué importa esto: el PDF original es un documento controlado (tiene
código, número de emisión y fecha de última revisión). Si algún día ese
documento se revisa formalmente (cambia una etiqueta, se agrega una
columna, cambia quién aprueba), el cambio se hace EN ESTE ARCHIVO —
nunca hay que tocar plantillas HTML ni la base de datos a mano.

Si se agrega o quita una columna del checklist:
    1. Súmala/quítala en COLUMNAS_CHECKLIST (respetando su "grupo").
    2. Agrega/quita la columna correspondiente en
       app/modules/inspecciones_montacargas/models.py (mismo "clave").
    3. Corre una migración (ALTER TABLE) en Supabase para esa columna.
No hay que tocar la plantilla: la tabla se dibuja sola a partir de esta lista.
"""

# --- Metadata del documento controlado (encabezado superior del PDF) ---
DOCUMENTO = {
    "titulo": "FORMULARIO DE INSPECCIONES DIARIAS MONTA CARGAS",
    "pagina": "1",
    "codigo": "F01-I28-P-IF-02",
    "emision": "2",
    "ultima_revision": "22/10/2024",
    "modificado_por": "Janiela Moreno / Asistente de Mantenimiento",
    "revisado_por": "Sergio Ortiz / Gerente de Operaciones",
    "aprobado_por": "Carolina Oviedo / Gestion de Calidad",
    "instrucciones": (
        'Indique "SI" si esta en buen estado, indique "NO" si esta en mal estado. '
        "En caso de existir un comentario, colocar un numero de referencia y "
        "anotarlo al dorso de la hoja."
    ),
}

# Turnos válidos, en el orden en que aparecen para cada día (Diurno / Nocturno)
TURNOS = ["D", "N"]

# Meses tal como se escriben en el campo "Mes" de la hoja.
MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

# Opciones para los campos tipo "si_no". Se deja en blanco por defecto
# (nunca se asume un valor que el técnico no marcó).
OPCIONES_SI_NO = ["SI", "NO"]

# --- Columnas del checklist, agrupadas exactamente como en el PDF ---
#
# Cada columna tiene:
#   clave   -> nombre de columna en la base de datos (no se cambia una vez
#              usado en producción; si hay que corregir el texto que ve el
#              usuario, se cambia "etiqueta", no "clave")
#   etiqueta-> encabezado tal como aparece en el PDF
#   tipo    -> "si_no" (desplegable SI/NO), "numero" (medición) o "texto"
#              (texto libre) o "fecha" (selector de fecha)
GRUPOS_CHECKLIST = [
    {
        "grupo": "Mecanica",
        "columnas": [
            {"clave": "cadenas_rodillos", "etiqueta": "Cadenas y rodillos de elevacion en buen estado", "tipo": "si_no"},
            {"clave": "nivel_aceite_frenos", "etiqueta": "Nivel de aceite de motor y liquido de frenos esta en nivel optimo", "tipo": "si_no"},
            {"clave": "fugas_aceite", "etiqueta": "No existen fugas de aceite de transmision, motor, liquido hidraulico o enfriamiento", "tipo": "si_no"},
            {"clave": "freno_mano", "etiqueta": "Freno de mano en buen estado", "tipo": "si_no"},
            {"clave": "horas_registradas", "etiqueta": "Horas registradas", "tipo": "numero"},
            {"clave": "juego_pedales", "etiqueta": "Juego de pedales en optimas condiciones", "tipo": "si_no"},
        ],
    },
    {
        "grupo": "Cabina Montacargas",
        "columnas": [
            {"clave": "mandos_hidraulicos", "etiqueta": "Mandos hidraulicos de subir, bajar, inclinar y movimientos funcionan correctamente", "tipo": "si_no"},
            {"clave": "temperatura_rango", "etiqueta": "Temperatura esta dentro de rango de seguridad", "tipo": "si_no"},
            {"clave": "instrumentos_panel", "etiqueta": "Instrumentos del panel funcionan correctamente", "tipo": "si_no"},
            {"clave": "direccionales", "etiqueta": "Direccionales funcionan correctamente", "tipo": "si_no"},
        ],
    },
    {
        "grupo": "Seguridad",
        "columnas": [
            {"clave": "mecanismos_seguridad", "etiqueta": "Mecanismos de seguridad funcionan correctamente", "tipo": "si_no"},
            {"clave": "luces_freno_marcha", "etiqueta": "Luces de freno, Iluminacion delantera y luces de marcha atras funcionan correctamente", "tipo": "si_no"},
            {"clave": "extintor", "etiqueta": "Extintor de montacargas en buenas condiciones", "tipo": "si_no"},
        ],
    },
    {
        "grupo": "Estado de correccion",
        "columnas": [
            {"clave": "se_corrige", "etiqueta": "Se corrije algun(o) de lo(s) daño(s) presentado(s)", "tipo": "si_no"},
            {"clave": "responsable_correccion", "etiqueta": "Responsable de correccion", "tipo": "texto"},
            {"clave": "fecha_correccion", "etiqueta": "Fecha de correccion", "tipo": "fecha"},
        ],
    },
]


def columnas_planas():
    """Todas las columnas del checklist en una sola lista (sin agrupar)."""
    return [col for grupo in GRUPOS_CHECKLIST for col in grupo["columnas"]]


def claves_checklist():
    """Solo las claves (nombres de columna) del checklist, en orden."""
    return [col["clave"] for col in columnas_planas()]
