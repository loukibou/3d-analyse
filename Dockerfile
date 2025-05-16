FROM python:3.10-slim

# libs système pour OCCT (CadQuery/OCP)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libgl1-mesa-glx \
      libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
EXPOSE 8000

# pour prod, tu peux remplacer par gunicorn
CMD ["python", "app.py"]
