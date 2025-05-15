# --- Dockerfile ---
# 1) On part d'une image Miniconda (Debian)
FROM continuumio/miniconda3:latest

# 2) Installer les libs système dont CadQuery a besoin
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libgl1-mesa-glx \
      libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 3) Configurer conda-forge et installer CadQuery + pythonOCC + Flask + Requests + Boto3
RUN conda config --add channels conda-forge && \
    conda config --set channel_priority strict && \
    conda install -y \
      cadquery \
      pythonocc-core \
      flask \
      requests \
      boto3 && \
    conda clean -afy

# 4) Copier le code et installer les éventuelles dépendances Pip restantes
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5) Copier le reste de l'application
COPY . .

# 6) Exposer le port et lancer
ENV PORT=8000
EXPOSE 8000
CMD ["python", "app.py"]
