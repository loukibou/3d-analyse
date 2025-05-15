# 1) Base Conda (Debian)
FROM continuumio/miniconda3:latest

# 2) Installer libGL pour CadQuery/OpenCASCADE
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \
        libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# 3) Configurer conda-forge et installer Mamba
RUN conda config --add channels conda-forge && \
    conda config --set channel_priority strict && \
    conda install -y mamba && \
    conda clean -afy

# 4) Installer Python 3.10, CadQuery, OCC, Flask, Requests, Boto3
RUN mamba install -y \
        python=3.10 \
        cadquery \
        pythonocc-core \
        flask \
        requests \
        boto3 && \
    mamba clean --all --yes

# 5) Copier le code de l'application
WORKDIR /app
COPY . .

# 6) Exposer le port injecté par Railway et démarrer l'app
ENV PORT=8000
EXPOSE 8000
CMD ["python", "app.py"]
