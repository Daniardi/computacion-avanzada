"""Entrena y exporta un modelo SARIMA con la serie real almacenada en InfluxDB."""

# Importamos argumentos de consola, JSON, avisos, fecha UTC y rutas de archivos.
import argparse
import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

# Importamos NumPy para calcular las métricas de evaluación del pronóstico.
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Añadimos la raíz del proyecto para importar los módulos propios desde scripts/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Importamos configuración y la función que consulta y prepara la serie de InfluxDB.
from app import config
from app.influx import leer_serie_horaria


def crear_argumentos():
    """Define opciones que permiten ajustar el entrenamiento sin cambiar código."""
    # Creamos el lector de parámetros de la línea de comandos.
    parser = argparse.ArgumentParser(description="Entrena SARIMA con datos reales de InfluxDB.")
    # Indicamos cuántas horas históricas se usarán para ajustar el modelo.
    parser.add_argument("--historial-horas", type=int, default=24 * 30)
    # Reservamos las últimas horas para evaluar antes de entrenar el modelo final.
    parser.add_argument("--horizonte-prueba", type=int, default=24)
    # Permitimos modificar el orden no estacional p, d y q si la evaluación lo requiere.
    parser.add_argument("--order", nargs=3, type=int, default=(1, 0, 1), metavar=("P", "D", "Q"))
    # Permitimos modificar el orden estacional P, D, Q y el periodo de estacionalidad.
    parser.add_argument(
        "--seasonal-order",
        nargs=4,
        type=int,
        default=(1, 1, 1, 24),
        metavar=("P", "D", "Q", "S"),
    )
    # Devolvemos los argumentos ya validados por argparse.
    return parser.parse_args()


def ajustar_modelo(serie, order, seasonal_order):
    """Ajusta SARIMA y devuelve el resultado sin imprimir advertencias de convergencia."""
    # Construimos el modelo usando los órdenes entregados por la persona que entrena.
    modelo = SARIMAX(
        serie,
        order=tuple(order),
        seasonal_order=tuple(seasonal_order),
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    # Ocultamos avisos numéricos para conservar una salida de consola legible.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # Estimamos los parámetros que mejor describen la serie observada.
        return modelo.fit(disp=False)


def calcular_metricas(resultado, serie_prueba):
    """Pronostica el periodo reservado y calcula MAE y RMSE para validación temporal."""
    # Generamos tantas predicciones como horas se reservaron para la prueba.
    prediccion = resultado.get_forecast(steps=len(serie_prueba)).predicted_mean
    # Convertimos ambos arreglos a valores numéricos para operar de forma vectorizada.
    errores = np.asarray(serie_prueba, dtype=float) - np.asarray(prediccion, dtype=float)
    # Calculamos error absoluto medio y raíz del error cuadrático medio.
    return {
        "mae": round(float(np.mean(np.abs(errores))), 4),
        "rmse": round(float(np.sqrt(np.mean(errores**2))), 4),
    }


def exportar_modelo(resultado, argumentos, n_observaciones, metricas):
    """Guarda parámetros y metadatos no sensibles en el JSON usado por FastAPI."""
    # Construimos una representación portable que evita serializar objetos pickle.
    configuracion = {
        "order": list(argumentos.order),
        "seasonal_order": list(argumentos.seasonal_order),
        "params": {nombre: float(valor) for nombre, valor in resultado.params.items()},
        "measurement": config.INFLUX_MEASUREMENT,
        "field": config.INFLUX_FIELD,
        "entrenado_en": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "n_observaciones": int(n_observaciones),
        "metricas_validacion": metricas,
    }
    # Definimos la ruta estable que carga la API al iniciar.
    destino = config.BASE_DIR / "models" / "sarima_config.json"
    # Creamos la carpeta en caso de que no exista todavía en un Codespace nuevo.
    destino.parent.mkdir(exist_ok=True)
    # Escribimos JSON UTF-8 legible sin incluir URL, token ni otros secretos.
    destino.write_text(json.dumps(configuracion, indent=2, ensure_ascii=False), encoding="utf-8")
    # Informamos la ubicación y las métricas que se deberán mencionar en la sustentación.
    print(f"Modelo exportado en: {destino}")
    print(f"MAE de validación: {metricas['mae']}")
    print(f"RMSE de validación: {metricas['rmse']}")


def main():
    """Orquesta lectura, validación temporal, ajuste final y exportación del SARIMA."""
    # Leemos los valores elegidos desde la terminal.
    argumentos = crear_argumentos()
    # Evitamos entrenar por error con la serie sintética cuando se requiere una entrega real.
    if config.DEMO_MODE:
        raise RuntimeError("DEMO_MODE debe ser false o no existir para entrenar con InfluxDB real.")
    # Confirmamos que están presentes las cuatro credenciales requeridas por InfluxDB.
    if not config.influx_configurado():
        raise RuntimeError("Faltan secretos INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG o INFLUX_BUCKET.")
    # Exigimos suficientes datos para separar prueba y conservar dos ciclos estacionales.
    minimo = argumentos.horizonte_prueba + 2 * argumentos.seasonal_order[3]
    if argumentos.historial_horas <= minimo:
        raise ValueError(f"historial-horas debe superar {minimo} para validar el modelo.")
    # Consultamos la serie real, ya regularizada a frecuencia de una hora.
    serie = leer_serie_horaria(argumentos.historial_horas)
    # Verificamos que InfluxDB devolvió suficientes observaciones utilizables.
    if len(serie) <= minimo:
        raise ValueError("InfluxDB no devolvió suficientes datos para entrenar y validar.")
    # Separamos cronológicamente la parte antigua para entrenar y la reciente para probar.
    entrenamiento = serie.iloc[: -argumentos.horizonte_prueba]
    prueba = serie.iloc[-argumentos.horizonte_prueba :]
    # Ajustamos solo con observaciones previas a la ventana de evaluación.
    resultado_prueba = ajustar_modelo(entrenamiento, argumentos.order, argumentos.seasonal_order)
    # Medimos el desempeño fuera de muestra en las últimas horas observadas.
    metricas = calcular_metricas(resultado_prueba, prueba)
    # Ajustamos una última vez con toda la historia para dejar el modelo listo para la API.
    resultado_final = ajustar_modelo(serie, argumentos.order, argumentos.seasonal_order)
    # Exportamos parámetros, metadatos y métricas, pero nunca los secretos de InfluxDB.
    exportar_modelo(resultado_final, argumentos, len(serie), metricas)


# Ejecutamos el flujo solo cuando este archivo se llama directamente desde la terminal.
if __name__ == "__main__":
    main()
