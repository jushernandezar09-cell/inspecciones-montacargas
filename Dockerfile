FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Forma "shell" (no array) a propósito: así se expande $PORT, la variable
# que Render asigna automáticamente al desplegar (localmente cae en 8000).
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
