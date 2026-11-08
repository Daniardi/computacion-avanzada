"""Crea un SARIMA de demostración para probar frontend y API sin InfluxDB."""

# Importamos JSON, avisos, fecha, rutas y bibliotecas de series de tiempo.
import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Añadimos la raíz del proyecto para poder importar app al ejecutar este archivo.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# Importamos la misma serie demo usada por la API para asegurar consistencia.
from app.influx import serie_demo

# Definimos órdenes modestos con estacionalidad diaria de 24 horas.
ORDER = (1, 0, 1)
SEASONAL_ORDER = (1, 1, 1, 24)

# Generamos tres semanas de datos sintéticos y ajustamos el modelo de prueba.
serie = serie_demo(24 * 21)
modelo = SARIMAX(
    serie,
    order=ORDER,
    seasonal_order=SEASONAL_ORDER,
    enforce_stationarity=False,
    enforce_invertibility=False,
)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    resultado = modelo.fit(disp=False)

# Exportamos solamente información estable que la API puede reconstruir.
configuracion = {
    "order": list(ORDER),
    "seasonal_order": list(SEASONAL_ORDER),
    "params": {nombre: float(valor) for nombre, valor in resultado.params.items()},
    "measurement": "demo",
    "field": "temperatura_sintetica",
    "entrenado_en": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    "n_observaciones": int(len(serie)),
}

# Guardamos el artefacto en la carpeta que consume el servicio.
destino = Path(__file__).resolve().parent.parent / "models" / "sarima_config.json"
destino.parent.mkdir(exist_ok=True)
destino.write_text(json.dumps(configuracion, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Modelo demo creado en {destino}")
