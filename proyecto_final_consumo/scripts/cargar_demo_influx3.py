"""Carga una serie sintética identificada como demo en InfluxDB Cloud Serverless."""

# Importamos rutas para poder cargar módulos propios desde la carpeta scripts.
import sys
from pathlib import Path

# Añadimos la raíz del proyecto al buscador de módulos de Python.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Importamos el cliente v3, configuración y la serie didáctica ya usada por la API.
from influxdb_client_3 import InfluxDBClient3, Point

from app import config
from app.influx import serie_demo


def main():
    """Genera datos etiquetados como demo y los escribe en el bucket configurado."""
    # Exigimos InfluxDB v3 porque este script usa el cliente Cloud Serverless.
    if config.INFLUX_VERSION != "3":
        raise RuntimeError("Configure INFLUX_VERSION=3 para cargar datos demo en Cloud Serverless.")
    # Confirmamos URL, token y bucket antes de intentar una conexión remota.
    if not config.influx_configurado():
        raise RuntimeError("Faltan INFLUX_URL, INFLUX_TOKEN o INFLUX_BUCKET.")
    # Generamos 30 días de datos horarios con el mismo patrón usado en modo demo.
    serie = serie_demo(24 * 30)
    # Creamos el cliente conectado únicamente con secretos leídos del entorno.
    cliente = InfluxDBClient3(
        host=config.INFLUX_URL,
        database=config.INFLUX_BUCKET,
        token=config.INFLUX_TOKEN,
    )
    try:
        # Convertimos cada observación en un punto con una etiqueta transparente de origen.
        puntos = [
            Point(config.INFLUX_MEASUREMENT)
            .tag("origen", "demo")
            .field(config.INFLUX_FIELD, float(valor))
            .time(fecha.to_pydatetime())
            for fecha, valor in serie.items()
        ]
        # Enviamos todos los puntos al bucket o base de datos configurada.
        cliente.write(record=puntos)
    finally:
        # Cerramos la conexión aunque falle la escritura de la serie.
        cliente.close()
    # Aclaramos la naturaleza didáctica de los datos cargados para la sustentación.
    print(f"Se cargaron {len(serie)} datos DEMO en InfluxDB v3.")


# Ejecutamos la carga solo al llamar directamente este archivo desde la terminal.
if __name__ == "__main__":
    main()
