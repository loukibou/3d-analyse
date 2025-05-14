# Utilise une image Miniconda officielle
FROM continuumio/miniconda3:latest

# 1) Crée un environnement conda python3.10 (CadQuery 2.1 supporté)
RUN conda create -y -n cadenv python=3.10 \
    && conda clean -afy

# 2) Active l'env, installe CadQuery et PythonOCC en même temps
SHELL ["conda", "run", "-n", "cadenv", "/bin/bash", "-c"]
RUN conda install -y -c conda-forge \
    cadquery=2.1 \
    pythonocc-core \
    flask \
    requests \
    boto3 \
    && conda clean -afy

# 3) Retour au shell normal pour COPY et CMD
SHELL ["/bin/bash", "-lc"]

# 4) Copie votre code dans /app
WORKDIR /app
COPY . .

# 5) Expose le port (Railway injecte $PORT)
ENV PORT=8000
EXPOSE 8000

# 6) Utilise l'environnement conda au runtime
CMD ["conda", "run", "--no-capture-output", "-n", "cadenv", "python", "app.py"]
