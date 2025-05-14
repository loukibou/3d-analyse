# 1) On part de Miniconda
FROM continuumio/miniconda3

# 2) On configure conda‑forge et on installe mamba
RUN conda config --add channels conda-forge \
 && conda config --set channel_priority strict \
 && conda install -y mamba \
 && conda clean -afy

# 3) On améliore la base Python en la passant en 3.10,
#    puis on installe CadQuery, pythonOCC et vos libs
RUN mamba install -y \
     python=3.10 \
     cadquery \
     pythonocc-core \
     flask \
     requests \
     boto3 \
 && mamba clean --all --yes

# 4) On copie le code de l’application
WORKDIR /app
COPY . .

# 5) On expose le port injecté par Railway
ENV PORT=8000
EXPOSE 8000

# 6) On lance l’application
CMD ["python", "app.py"]
