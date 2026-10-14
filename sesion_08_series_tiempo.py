"""Sesión 8 — Series de tiempo: pronóstico de temperatura y humedad."""

# Importamos NumPy y Pandas para generar y transformar series temporales.
import numpy as np
import pandas as pd
# Importamos modelos clásicos y métricas de pronóstico.
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error


def crear_sensor(n_horas=45 * 24):
    """Simula 45 días de lecturas horarias de un sensor DHT22."""
    # Usamos una semilla fija para producir siempre la misma serie.
    generador = np.random.default_rng(42)
    # Construimos el eje temporal horario y su índice numérico.
    tiempo = pd.date_range("2025-01-01", periods=n_horas, freq="h")
    t = np.arange(n_horas)
    # Combinamos tendencia, ciclo diario y ruido de medición.
    temperatura = 22 + 0.01 * t + 4 * np.sin(2 * np.pi * t / 24 - np.pi / 2) + generador.normal(0, 0.6, n_horas)
    humedad = 60 - 0.005 * t - 10 * np.sin(2 * np.pi * t / 24 - np.pi / 2) + generador.normal(0, 2, n_horas)
    # Limitamos humedad a rangos físicamente razonables.
    return pd.DataFrame({"temperatura": temperatura, "humedad": np.clip(humedad, 20, 95)}, index=tiempo)


def crear_ventanas(serie, ventana):
    """Convierte una serie en pares de valores pasados X y próximo valor y."""
    # Extraemos valores para recorrerlos en orden temporal.
    valores = np.asarray(serie)
    # Cada fila de X contiene una ventana y y es el valor siguiente.
    x = np.array([valores[i:i + ventana] for i in range(len(valores) - ventana)])
    y = np.array([valores[i + ventana] for i in range(len(valores) - ventana)])
    return x, y


def media_movil(train, pasos, ventana=24):
    """Pronostica cada paso como el promedio de la última ventana."""
    # Guardamos el historial que se amplía con cada predicción.
    historial, predicciones = list(train), []
    # Generamos recursivamente el horizonte de pronóstico.
    for _ in range(pasos):
        siguiente = np.mean(historial[-ventana:])
        predicciones.append(siguiente)
        historial.append(siguiente)
    return np.array(predicciones)


if __name__ == "__main__":
    # Generamos la serie ambiental y elegimos temperatura como objetivo inicial.
    datos = crear_sensor()
    serie = datos["temperatura"]
    # Separamos los últimos cinco días para prueba cronológica.
    train, test = serie.iloc[:-120], serie.iloc[-120:]
    # Pronosticamos con media móvil, Holt-Winters y ARIMA.
    pred_mm = media_movil(train, len(test), 24)
    pred_hw = ExponentialSmoothing(train, trend="add", seasonal="add", seasonal_periods=24).fit().forecast(len(test))
    pred_arima = ARIMA(train, order=(4, 1, 2)).fit().forecast(len(test))
    # Mostramos métricas comparables para los tres modelos.
    for nombre, prediccion in [("Media móvil", pred_mm), ("Holt-Winters", pred_hw), ("ARIMA", pred_arima)]:
        print(f"{nombre}: MAE={mean_absolute_error(test, prediccion):.3f} | RMSE={mean_squared_error(test, prediccion) ** 0.5:.3f}")
    # Construimos y evaluamos una regresión sobre ventanas deslizantes de 24 horas.
    x, y = crear_ventanas(serie, 24)
    modelo = LinearRegression().fit(x[:-120], y[:-120])
    print("Ventanas deslizantes: MAE=", round(mean_absolute_error(y[-120:], modelo.predict(x[-120:])), 3))
