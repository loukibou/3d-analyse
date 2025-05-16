# --- Dockerfile ---

# 1) Base Ubuntu avec Python3
FROM ubuntu:22.04

# 2) Installer Python, pip, FreeCAD et dépendances OpenCASCADE
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      python3 \
      python3-pip \
      freecad \
      python3-freecad \
      libgl1-mesa-glx \
      libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 3) Copier les sources et installer les dépendances Python
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 4) Copier le code de l’API
COPY . .

# 5) Exposer le port et démarrer l’application
ENV PORT=8000
EXPOSE 8000
CMD ["python3", "app.py"]
