# 1) Image de base
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

# 2) Installer les utilitaires nécessaires (gpg, dirmngr, add-apt-repository…)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      software-properties-common \
      ca-certificates \
      wget \
      gnupg \
      dirmngr \
      lsb-release \
    && rm -rf /var/lib/apt/lists/*

# 3) Activer le dépôt 'universe' et ajouter le PPA FreeCAD stable
RUN add-apt-repository universe && \
    add-apt-repository ppa:freecad-maintainers/freecad-stable && \
    apt-get update

# 4) Installer FreeCAD, son binding Python, et pip
RUN apt-get install -y --no-install-recommends \
      freecad \
      python3-freecad \
      python3-pip \
    && rm -rf /var/lib/apt/lists/*

# 5) Installer les dépendances Python de l’app
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 6) Copier le reste du code et exposer le port
COPY . .
ENV PORT=8000
EXPOSE 8000

# 7) Commande de démarrage
CMD ["python3", "app.py"]
