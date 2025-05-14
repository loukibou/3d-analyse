# 1) Image Miniconda
FROM continuumio/miniconda3

# 2) Configurer conda-forge et installer mamba pour un solveur rapide
RUN conda config --add channels conda-forge \
 && conda config --set channel_priority strict \
 && conda install -y mamba \
 && conda clean -afy

# 3) Installer CadQuery, PythonOCC et vos dépendances Python via mamba
RUN mamba install -y \
     cadquery \
     pythonocc-core \
     flask \
     requests \
     boto3 \
 && mamba clean --all --yes

# 4) Copier votre code
WORKDIR /app
COPY . .

# 5) Exposer le port (Railway injecte $PORT)
ENV PORT=8000
EXPOSE 8000

# 6) Lancer l’app  
CMD ["python", "app.py"]
