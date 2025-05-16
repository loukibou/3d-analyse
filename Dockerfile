# ---------- Dockerfile ----------
# (1) Image de base Miniforge / conda-forge (amd64)
FROM conda-forge/miniforge3:latest    # ← orthographe correcte

# (2) Librairies CAO + dépendances API
RUN conda install -y -c conda-forge \
        python=3.10 \
        freecad \
        pythonocc-core=7.6.* \
        cadquery \
        flask \
        requests \
        boto3 \
    && conda clean -afy

# FreeCAD en mode headless
ENV QT_QPA_PLATFORM=offscreen

# (3) Copie du code
WORKDIR /app
COPY app.py .

# (4) Exposition & démarrage
ENV PORT=8000
EXPOSE 8000
CMD ["python", "app.py"]
