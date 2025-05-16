# ---------- Dockerfile ----------
FROM condaforge/miniforge3:latest      # ← tag présent pour amd64

# 1) Dépendances CAD + web API
RUN conda install -y -c conda-forge \
        python=3.10 \
        freecad \
        pythonocc-core=7.6.* \
        cadquery \
        flask \
        requests \
        boto3 \
    && conda clean -afy

# 2) Variable Qt pour le mode headless
ENV QT_QPA_PLATFORM=offscreen

# 3) Code
WORKDIR /app
COPY app.py .

# 4) Démarrage
ENV PORT=8000
EXPOSE 8000
CMD ["python", "app.py"]
