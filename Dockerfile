FROM ubuntu:22.04

# 1) Activer universe + installer pré‑requis pour PPA
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      software-properties-common \
      ca-certificates \
      wget && \
    add-apt-repository universe && \
    add-apt-repository ppa:freecad-maintainers/freecad-stable && \
    apt-get update

# 2) Installer FreeCAD & Python
RUN DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
      freecad \
      python3-freecad \
      python3-pip && \
    rm -rf /var/lib/apt/lists/*

# 3) Installer les dépendances Python  
WORKDIR /app  
COPY requirements.txt .  
RUN pip3 install --no-cache-dir -r requirements.txt

# 4) Copier le code  
COPY . .

# 5) Exposer le port et démarrer  
ENV PORT=8000  
EXPOSE 8000  
CMD ["python3", "app.py"]
