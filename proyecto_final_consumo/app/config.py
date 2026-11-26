"""Configuración central del proyecto final obtenida desde variables de entorno."""

# Importamos utilidades para leer variables de entorno y rutas del proyecto.
import os
from pathlib import Path

# Importamos dotenv para permitir configuración local sin publicar secretos.
from dotenv import load_dotenv

# Cargamos un archivo local .env si existe; nunca reemplaza secretos del entorno.
load_dotenv()

# Calculamos la carpeta raíz del proyecto final.
BASE_DIR = Path(__file__).resolve().parent.parent

# Leemos credenciales de InfluxDB sin incluir valores sensibles en el código.
INFLUX_URL = os.getenv("INFLUX_URL", "")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "")
INFLUX_ORG = os.getenv("INFLUX_ORG", "")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "")

# Permitimos usar la API clásica v2 o InfluxDB Cloud Serverless v3.
INFLUX_VERSION = os.getenv("INFLUX_VERSION", "2")

# Definimos la serie final: temperatura de sensores; se puede sobrescribir con secretos.
INFLUX_MEASUREMENT = os.getenv("INFLUX_MEASUREMENT", "sensores")
INFLUX_FIELD = os.getenv("INFLUX_FIELD", "temperatura")

# Ubicamos el archivo JSON generado al entrenar el modelo SARIMA.
MODEL_PATH = Path(os.getenv("MODEL_PATH", BASE_DIR / "models" / "sarima_config.json"))

# Configuramos cantidad de datos de contexto y horizonte máximo de predicción.
HORAS_CONTEXTO = int(os.getenv("HORAS_CONTEXTO", "336"))
MAX_HORAS_PREDICCION = int(os.getenv("MAX_HORAS_PREDICCION", "72"))

# Permitimos una demostración sintética mientras se configura la base real.
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("1", "true", "si", "sí")


def influx_configurado():
    """Indica si existen las credenciales necesarias para la versión configurada."""
    # Cloud Serverless v3 usa URL, token y bucket o base de datos, sin organización.
    if INFLUX_VERSION == "3":
        return all([INFLUX_URL, INFLUX_TOKEN, INFLUX_BUCKET])
    # La API v2 requiere además la organización para ejecutar consultas Flux.
    return all([INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET])
