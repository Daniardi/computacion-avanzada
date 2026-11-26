"""Lectura de temperatura desde InfluxDB y generación de datos de demostración."""

# Importamos NumPy, pandas y el cliente oficial de InfluxDB.
import numpy as np
import pandas as pd
from influxdb_client import InfluxDBClient
from influxdb_client_3 import InfluxDBClient3

# Importamos configuración central para acceder a variables de entorno.
from . import config


def serie_demo(horas, semilla=42):
    """Genera una temperatura horaria sintética con estacionalidad diaria."""
    # Construimos un índice horario UTC que termina en la última hora completa.
    fin = pd.Timestamp.now(tz="UTC").tz_localize(None).floor("h") - pd.Timedelta(hours=1)
    indice = pd.date_range(end=fin, periods=horas, freq="h")
    # Transformamos las horas UTC a hora local colombiana para el ciclo térmico.
    hora_colombia = (indice.hour - 5) % 24
    # Calculamos una curva diaria y ruido reproducible de un sensor.
    generador = np.random.default_rng(semilla)
    valores = 23 + 4 * np.sin(2 * np.pi * (hora_colombia - 8) / 24) + generador.normal(0, 0.5, horas)
    # Devolvemos la serie con el formato que consume el modelo.
    return pd.Series(valores, index=indice, name="temperatura")


def leer_serie_horaria(horas):
    """Consulta temperatura y la convierte en una serie con frecuencia de una hora."""
    # Usamos datos sintéticos cuando la persona está probando sin InfluxDB.
    if config.DEMO_MODE:
        return serie_demo(horas)
    # Elegimos la consulta SQL de Cloud Serverless cuando se configuró la versión 3.
    if config.INFLUX_VERSION == "3":
        return leer_serie_v3(horas)
    # Creamos el cliente únicamente con secretos leídos desde el entorno.
    with InfluxDBClient(url=config.INFLUX_URL, token=config.INFLUX_TOKEN, org=config.INFLUX_ORG) as cliente:
        # Pedimos datos recientes y agregamos a promedio horario.
        consulta = f'''
from(bucket: "{config.INFLUX_BUCKET}")
  |> range(start: -{horas + 2}h)
  |> filter(fn: (r) => r["_measurement"] == "{config.INFLUX_MEASUREMENT}")
  |> filter(fn: (r) => r["_field"] == "{config.INFLUX_FIELD}")
  |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
  |> keep(columns: ["_time", "_value"])
  |> sort(columns: ["_time"])
'''
        tablas = cliente.query_api().query(consulta, org=config.INFLUX_ORG)
    # Extraemos fechas y valores válidos de cada tabla devuelta por InfluxDB.
    tiempos, valores = [], []
    for tabla in tablas:
        for registro in tabla.records:
            if registro.get_value() is not None:
                tiempos.append(registro.get_time())
                valores.append(float(registro.get_value()))
    # Detenemos el proceso con un error claro si no hay observaciones.
    if not tiempos:
        raise ValueError("InfluxDB no devolvió datos para el measurement y field configurados.")
    # Convertimos fechas a UTC sin zona horaria y agrupamos posibles duplicados.
    indice = pd.to_datetime(tiempos, utc=True).tz_localize(None).floor("h")
    serie = pd.Series(valores, index=indice, name="temperatura").groupby(level=0).mean().sort_index()
    # Regularizamos la frecuencia y rellenamos huecos cortos para el SARIMA.
    rango = pd.date_range(serie.index.min(), serie.index.max(), freq="h")
    serie = serie.reindex(rango).interpolate(method="time").ffill().bfill()
    return serie.iloc[-horas:]


def leer_serie_v3(horas):
    """Consulta una serie horaria con el cliente oficial de InfluxDB Cloud Serverless."""
    # Validamos identificadores para evitar construir una consulta SQL insegura.
    if not config.INFLUX_MEASUREMENT.replace("_", "").isalnum():
        raise ValueError("INFLUX_MEASUREMENT solo puede contener letras, números y guion bajo.")
    # Validamos también el nombre del campo que representa la temperatura.
    if not config.INFLUX_FIELD.replace("_", "").isalnum():
        raise ValueError("INFLUX_FIELD solo puede contener letras, números y guion bajo.")
    # Construimos SQL para pedir los puntos más recientes de la medición configurada.
    consulta = f'''
SELECT time, {config.INFLUX_FIELD} AS valor
FROM {config.INFLUX_MEASUREMENT}
WHERE time >= now() - INTERVAL '{horas + 2} hours'
ORDER BY time
'''
    # Creamos un cliente v3 con URL, bucket o base de datos y token privado.
    cliente = InfluxDBClient3(
        host=config.INFLUX_URL,
        database=config.INFLUX_BUCKET,
        token=config.INFLUX_TOKEN,
    )
    try:
        # Pedimos un DataFrame para reutilizar el mismo procesamiento de pandas.
        datos = cliente.query(consulta, mode="pandas")
    finally:
        # Cerramos conexiones de red aunque la consulta tenga un error.
        cliente.close()
    # Detenemos el proceso con un mensaje claro cuando la consulta no devuelve filas.
    if datos.empty:
        raise ValueError("InfluxDB v3 no devolvió datos para el measurement y field configurados.")
    # Convertimos tiempo y valores a tipos homogéneos antes de regularizar la serie.
    indice = pd.to_datetime(datos["time"], utc=True).dt.tz_localize(None).dt.floor("h")
    valores = pd.to_numeric(datos["valor"], errors="coerce")
    # Construimos, limpiamos y ordenamos la serie temporal que consume SARIMA.
    serie = pd.Series(valores.to_numpy(), index=indice, name="temperatura").dropna()
    serie = serie.groupby(level=0).mean().sort_index()
    # Creamos frecuencia horaria y completamos huecos breves por interpolación temporal.
    rango = pd.date_range(serie.index.min(), serie.index.max(), freq="h")
    serie = serie.reindex(rango).interpolate(method="time").ffill().bfill()
    return serie.iloc[-horas:]
