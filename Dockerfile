# ---------- Dockerfile ----------
FROM mambaforge/mambaforge:23.3.1-4

RUN mamba install -y -c conda-forge \
        python=3.10 \
        freecad \
        pythonocc-core=7.6.* \
        cadquery \
        flask \
        requests \
        boto3 \
    && mamba clean -afy

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
EXPOSE 8000
CMD ["python", "app.py"]
