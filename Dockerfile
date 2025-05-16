# ---------- Dockerfile ----------
# Image conda officielle et publique
FROM condaforge/miniforge3:23.11.0-2

# 1) Installer toutes les dépendances en une seule transaction
RUN conda install -y -c conda-forge \
        python=3.10 \
        freecad \
        pythonocc-core=7.6.* \
        cadquery \
        flask \
        requests \
        boto3 \
    && conda clean -afy

# 2) Copier le code
WORKDIR /app
COPY app.py .

# 3) Démarrer l’API
ENV PORT=8000
EXPOSE 8000
CMD ["python", "app.py"]
