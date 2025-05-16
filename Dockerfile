# ---------- Dockerfile ----------

# 1) Base Python 3.10 slim
FROM python:3.10-slim

# 2) Dépendance système pour OpenCASCADE (libGL)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# 3) Copier et installer les dépendances Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copier le code de l’API
COPY . .

# 5) Exposer le port (Railway injecte $PORT)
ENV PORT=8000
EXPOSE 8000

# 6) Lancer via Gunicorn (2 workers, timeout 60s)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60", "app:app"]
