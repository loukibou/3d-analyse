# --- Dockerfile ---
# 1) Image de base Miniconda
FROM continuumio/miniconda3:latest

# 2) Installer les libs système pour OpenCASCADE/CadQuery
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libgl1-mesa-glx \
      libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 3) Configurer conda-forge, passer en Python 3.10 et installer tout en une passe
RUN conda config --add channels conda-forge && \
    conda config --set channel_priority strict && \
    conda install -y \
      python=3.10 \
      cadquery \
      pythonocc-core \
      flask \
      requests \
      boto3 && \
    conda clean -afy

# 4) Copier et installer les éventuelles dépendances pip
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5) Copier le code de l’application
COPY . .

# 6) Exposer et lancer
ENV PORT=8000
EXPOSE 8000
CMD ["python", "app.py"]
