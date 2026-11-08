# Partimos de una imagen oficial y liviana de Python.
FROM python:3.12-slim

# Definimos la carpeta de trabajo dentro del contenedor.
WORKDIR /app

# Copiamos dependencias primero para aprovechar la caché de construcción.
COPY requirements.txt .

# Instalamos las dependencias sin conservar archivos de caché.
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos únicamente el código y recursos necesarios para servir la aplicación.
COPY app ./app
COPY frontend ./frontend
COPY models ./models

# Declaramos el puerto usado por Uvicorn.
EXPOSE 8000

# Iniciamos la API accesible desde fuera del contenedor.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
