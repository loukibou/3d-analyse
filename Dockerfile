# 1) Image officielle Python (slim, Debian)
FROM python:3.10-slim

# 2) Installer les bibliothèques système nécessaires (libGL, etc.)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libgl1-mesa-glx \
      libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

# 3) Créer et se placer dans le dossier app
WORKDIR /app

# 4) Copier uniquement les dépendances et installer avec pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5) Copier le reste du code
COPY . .

# 6) Exposer le port (Railway injecte $PORT)
ENV PORT=8000
EXPOSE 8000

# 7) Lancer l’application
CMD ["python", "app.py"]
