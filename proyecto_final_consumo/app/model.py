"""Carga de modelo SARIMA exportado y generación de pronósticos."""

# Importamos JSON, avisos, NumPy, pandas y SARIMAX.
import json
import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX


class ModeloSARIMA:
    """Reconstruye un SARIMA con parámetros exportados desde Colab."""

    def __init__(self, ruta):
        # Leemos órdenes y parámetros sin usar objetos pickle incompatibles.
        self.config = json.loads(ruta.read_text(encoding="utf-8"))
        self.order = tuple(self.config["order"])
        self.seasonal_order = tuple(self.config["seasonal_order"])
        self.params = self.config["params"]

    def pronosticar(self, serie, pasos, confianza=0.95):
        """Filtra el modelo con datos recientes y pronostica las próximas horas."""
        # Creamos la misma estructura SARIMA que se definió durante entrenamiento.
        modelo = SARIMAX(
            serie,
            order=self.order,
            seasonal_order=self.seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        # Ordenamos los parámetros en el orden interno esperado por statsmodels.
        parametros = np.array([self.params[nombre] for nombre in modelo.param_names])
        # Evitamos que advertencias de convergencia opaquen la respuesta de la API.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            resultado = modelo.filter(parametros)
            prediccion = resultado.get_forecast(steps=pasos).summary_frame(alpha=1 - confianza)
        # Normalizamos nombres de columnas para que el frontend los use fácilmente.
        return prediccion.rename(
            columns={"mean": "prediccion", "mean_ci_lower": "limite_inferior", "mean_ci_upper": "limite_superior"}
        )[["prediccion", "limite_inferior", "limite_superior"]]


def cargar_modelo(ruta):
    """Carga el modelo cuando el archivo existe o devuelve None si aún falta entrenar."""
    # Verificamos la presencia del artefacto antes de intentar abrirlo.
    return ModeloSARIMA(ruta) if ruta.exists() else None
