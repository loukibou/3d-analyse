# 1) Image Miniconda
FROM continuumio/miniconda3

# 2) libs système pour OpenCASCADE
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 3) Config conda-forge / mamba
RUN conda config --add channels conda-forge && \
    conda config --set channel_priority strict && \
    conda install -y mamba && \
    conda clean -afy

# 4) Installer Python + CadQuery + pythonOCC + Flask + Requests + Boto3
RUN mamba install -y \
     python=3.10 \
     cadquery \
     pythonocc-core \
     flask \
     requests \
     boto3 \
   && mamba clean --all --yes

# 5) Copie du code
WORKDIR /app
COPY . .

# 6) Exposition du port
ENV PORT=8000
EXPOSE 8000

# 7) Commande de lancement
CMD ["python", "app.py"]

