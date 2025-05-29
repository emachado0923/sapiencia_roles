# Usa una imagen oficial de Python como imagen base
FROM python:3.10-slim

# Establece el directorio de trabajo en /app
WORKDIR /app


COPY requirements.txt requirements.txt


RUN apt-get update && \
    apt-get install -y build-essential default-libmysqlclient-dev pkg-config && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \    
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .


EXPOSE 5000


ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0


CMD ["flask", "run"]
