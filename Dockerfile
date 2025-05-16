# 1) Image de base Miniconda
FROM continuumio/miniconda3:latest

# 2) Libs système requises par OpenCASCADE (FreeCAD)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libgl1-mesa-glx \
      libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 3) Configurer conda-forge et installer tout
RUN conda config --add channels conda-forge && \
    conda config --set channel_priority strict && \
    conda install -y \
      freecad            \
      pythonocc-core     \
      flask              \
      requests           \
      boto3              \
    && conda clean -afy

# 4) Créer le répertoire de travail et copier l'app
WORKDIR /app
COPY . .

# 5) Exposer le port et démarrer
ENV PORT=8000
EXPOSE 8000
CMD ["python", "app.py"]
