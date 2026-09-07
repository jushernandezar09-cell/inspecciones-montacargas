# Inspecciones Diarias Monta Cargas (F01-I28-P-IF-02)

Versión digital del formulario en papel `F01-I28-P-IF-02 · Formulario de
Inspecciones Diarias Monta Cargas`. La pantalla reproduce el documento tal
cual (mismo encabezado, mismas columnas, mismo texto) para que el registro
digital sea equivalente al de papel para efectos de auditoría.

- **Backend**: Python + FastAPI + SQLAlchemy + Jinja2 (mismo estilo que el
  proyecto "asistente").
- **Base de datos**: Supabase (Postgres) en producción; SQLite local para
  desarrollo — no hay que tocar código para cambiar entre uno y otro, solo
  la variable `DATABASE_URL`.
- **Acceso**: sin login, a propósito — es una hoja de uso compartido en
  planta, igual que la de papel.
- **Responsive**: la tabla se ve igual en celular, tablet y computadora;
  en pantallas angostas se desliza horizontalmente (las columnas Día y
  Turno quedan fijas para no perderse).
- **Guardado**: automático, fila por fila (día + turno), al salir de cada
  casilla — no hay botón de "guardar todo" que pueda pisar cambios hechos
  por otra persona en otro dispositivo.

## 1. Probarlo en tu computadora

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Abre http://localhost:8000 — usa SQLite (`data/app.db`) automáticamente,
no necesitas Supabase para probarlo.

## 2. Crear la tabla en Supabase

1. Entra a tu proyecto de Supabase → **SQL Editor** → *New query*.
2. Pega el contenido de `scripts/supabase_schema.sql` y dale **Run**.
   (Si lo saltas, la app crea la tabla sola la primera vez que arranca
   contra Supabase — pero correr el script a mano te deja ver y controlar
   exactamente qué se creó.)
3. Ve a **Project Settings → Database → Connection string → URI**. Copia
   la cadena en modo **Session pooler** (puerto `6543`) — es la más
   compatible con Render/Railway.
4. Esa cadena empieza con `postgresql://`; cámbiale el prefijo a
   `postgresql+psycopg://` (así SQLAlchemy sabe qué driver usar).

## 3. Desplegar en Render

1. Sube este proyecto a un repositorio de GitHub (puede ser privado).
2. En [render.com](https://render.com) → **New +** → **Blueprint**,
   selecciona el repositorio. Render lee `render.yaml` y arma el servicio
   solo (usa el `Dockerfile` de este proyecto).
3. En el servicio creado → **Environment**, agrega la variable
   `DATABASE_URL` con la cadena de Supabase del paso anterior (esta sí se
   escribe a mano porque es un dato secreto).
4. Guarda — Render construye y despliega. Te da una URL pública tipo
   `https://inspecciones-montacargas.onrender.com`, accesible desde
   cualquier celular, tablet o computadora, sin instalar nada.

> Nota sobre el plan gratuito de Render: el servicio "se duerme" tras
> ~15 minutos sin uso y tarda unos segundos en despertar con la primera
> visita del día. Si eso molesta en planta, se soluciona pasando al plan
> pagado más económico de Render (no requiere cambiar nada del código).

## Estructura del proyecto

```
app/
  main.py                          punto de entrada de FastAPI
  core/
    config.py                      configuración vía variables de entorno
    database.py                    conexión SQLAlchemy (SQLite/Postgres)
  modules/inspecciones_montacargas/
    formulario.py                  ← ÚNICA fuente de verdad: encabezado del
                                      documento, columnas del checklist,
                                      etiquetas. Editar aquí, no en el HTML.
    models.py                      tabla de la base de datos
    router.py                      páginas y endpoints (ver/guardar hoja)
  templates/
    base.html                      plantilla base (Tailwind, colores de marca)
    inicio.html                    elegir/crear equipo + mes + año
    inspecciones_montacargas/hoja.html   la hoja completa (réplica del PDF)
  static/img/logo_electroplast.png
scripts/supabase_schema.sql        DDL para crear la tabla en Supabase
```

## Si el documento F01-I28-P-IF-02 se revisa formalmente

Cuando cambie una etiqueta, se agregue o se quite una columna del
checklist (nueva "Última Revisión" del documento):

1. Edita `app/modules/inspecciones_montacargas/formulario.py` (agrega,
   quita o corrige la columna — un solo lugar).
2. Si agregaste/quitaste una columna (no solo el texto de una etiqueta),
   refleja el mismo cambio en `models.py` y corre un `ALTER TABLE` en
   Supabase para esa columna.
3. No hay que tocar `hoja.html` — la tabla se dibuja sola a partir de
   `formulario.py`.

## Sobre "hacerlo escalable" para los próximos formularios

Este proyecto es independiente y cubre solo este formulario, a propósito
(así se acordó). Para el siguiente PDF que se digitalice, se repite esta
misma receta como un proyecto nuevo: mismo patrón de carpetas
(`core/`, `modules/<nombre_formulario>/{formulario.py, models.py,
router.py}`, `templates/<nombre_formulario>/`), su propia tabla en
Supabase (puede vivir en el mismo proyecto de Supabase, en otra tabla) y
su propio servicio en Render.
