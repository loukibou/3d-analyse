# ---------- Dockerfile ----------
# Image de base : mamba + Python 3.10
FROM mambaforge/mambaforge:23.3.1-4

# 1) Installer FreeCAD, pythonocc-core, CadQuery et vos libs web
RUN mamba install -y -c conda-forge \
        python=3.10 \
        freecad \
        pythonocc-core=7.6.* \
        cadquery \
        flask \
        requests \
        boto3 \
    && mamba clean -afy

# 2) Copier le code de l’API
WORKDIR /app
COPY app.py .

# 3) Lancer le service Flask
ENV PORT=8000
EXPOSE 8000
CMD ["python", "app.py"]

