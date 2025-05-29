# Usa una imagen oficial de Python como imagen base
FROM python:3.9-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de requisitos primero para aprovechar el almacenamiento en caché de Docker
COPY requirements.txt requirements.txt

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación al directorio de trabajo
COPY . .

# Expone el puerto en el que se ejecuta la aplicación Flask (por defecto 5000)
EXPOSE 5000

# Define la variable de entorno para Flask (opcional, pero bueno para producción)
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Comando para ejecutar la aplicación cuando se inicie el contenedor
CMD ["flask", "run"]
