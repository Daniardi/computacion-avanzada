# Proyecto final: pronóstico de temperatura

Proyecto de Daniel Ardila Zabala para Computación Avanzada. Pronostica las próximas horas de temperatura usando una serie de sensores, SARIMA, FastAPI, InfluxDB y Docker.

## Arquitectura

InfluxDB → app/influx.py → modelo SARIMA → API FastAPI → frontend con Chart.js

La serie objetivo se configura como sensores y temperatura por defecto mediante las variables INFLUX_MEASUREMENT=sensores e INFLUX_FIELD=temperatura. Si los nombres reales son diferentes, se cambian como secretos, no en el código.

## Prueba sin datos reales

Desde esta carpeta ejecuta:

    py -m pip install -r requirements.txt
    $env:DEMO_MODE = "true"
    py scripts/crear_modelo_demo.py
    uvicorn app.main:app --host 0.0.0.0 --port 8000

Abre http://localhost:8000. El modo demo solo valida la arquitectura; para la entrega debe reemplazarse por el modelo entrenado con la serie real.

## Conexión con InfluxDB

1. Copia .env.example como .env para trabajo local, o crea secretos de Codespaces.
2. Configura INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG e INFLUX_BUCKET.
3. Entrena el SARIMA en Colab y guarda su archivo como models/sarima_config.json.
4. Ejecuta sin DEMO_MODE.

Nunca publiques .env ni el token.

## Docker

    docker build -t pronostico-temperatura .
    docker run --rm -p 8000:8000 -e INFLUX_URL -e INFLUX_TOKEN -e INFLUX_ORG -e INFLUX_BUCKET pronostico-temperatura

La opción -e pasa secretos al contenedor al ejecutarlo; no los copia dentro de la imagen.

## Evidencia final

- Frontend con histórico, pronóstico, intervalo de confianza y hora Colombia.
- API en /docs y salud en /api/salud.
- Modelo SARIMA real en models/sarima_config.json.
- Video de máximo cinco minutos mostrando ejecución sin Docker y con Docker.
