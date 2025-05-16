# 1) Image de base Miniconda
FROM continuumio/miniconda3:latest

# 2) Dépendances système pour l’affichage OpenCASCADE/FreeCAD
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libgl1-mesa-glx \
      libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 3) Configurer conda-forge et installer mamba (solveur plus rapide)
RUN conda config --add channels conda-forge && \
    conda config --set channel_priority strict && \
    conda install -y mamba && \
    conda clean -afy

# 4) Installer Python 3.10 + FreeCAD + pythonocc-core + Flask/requests/boto3
RUN mamba install -y \
      python=3.10 \
      freecad \
      pythonocc-core \
      flask \
      requests \
      boto3 && \
    mamba clean --all --yes

# 5) Copier l’application
WORKDIR /app
COPY . .

# 6) Exposer le port et démarrer
ENV PORT=8000
EXPOSE 8000
CMD ["python", "app.py"]
