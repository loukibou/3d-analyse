# --- Dockerfile ---
FROM continuumio/miniconda3:latest

# 1) libs système pour OpenCASCADE
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libgl1-mesa-glx \
      libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2) config conda-forge + installation globale
RUN conda config --add channels conda-forge && \
    conda config --set channel_priority strict && \
    conda install -y \
      python=3.10 \
      cadquery \
      pythonocc-core \
      flask \
      requests \
      boto3 \
      gunicorn && \
    conda clean -afy

# 3) code et pip (si vous avez d’autres deps)
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) copier tout le code
COPY . .

# 5) exposer le port Railway injecte
ENV PORT=8000
EXPOSE 8000

# 6) lancer avec gunicorn (2 workers, timeout 60s)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60", "app:app"]
