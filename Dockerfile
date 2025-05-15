# 1) On part d'une image Ubuntu récente
FROM ubuntu:22.04

# 2) Installer FreeCAD headless + Python3 + pip + dépendances système
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
      python3-freecad \
      freecad \
      python3-pip \
      && rm -rf /var/lib/apt/lists/*

# 3) Installer Flask, requests et boto3
RUN pip3 install --no-cache-dir flask requests boto3

# 4) Copier l'app
WORKDIR /app
COPY app.py .

# 5) Exposer le port injecté par Railway
ENV PORT=8000
EXPOSE 8000

# 6) Démarrer le service
CMD ["python3", "app.py"]
