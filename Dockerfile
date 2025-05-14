# 1) On part d'une image Python légère
FROM python:3.12-slim

# 2) On installe les paquets système nécessaires (libGL)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libgl1-mesa-glx \
      libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 3) On déclare le répertoire de travail
WORKDIR /app

# 4) On copie d'abord les dépendances
COPY requirements.txt .

# 5) Puis on installe les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# 6) On copie le reste de votre code
COPY . .

# 7) Exposition du port dynamique (Railway injecte $PORT)
ENV PORT=8000
EXPOSE 8000

# 8) Commande de démarrage
CMD ["python", "app.py"]
