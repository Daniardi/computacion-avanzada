"""Sesión 10 — IoT: captura, preparación y predicción de sensación térmica."""

# Importamos NumPy y Pandas para simular y preparar lecturas del sensor.
import numpy as np
import pandas as pd
# Importamos regresión y métricas para evaluar las predicciones.
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


def crear_datos_iot(n=480):
    """Simula lecturas horarias de DHT22 con temperatura, humedad y sensación."""
    # Inicializamos un generador reproducible y el eje horario.
    generador, t = np.random.default_rng(42), np.arange(n)
    fechas = pd.date_range("2026-09-01", periods=n, freq="h")
    # Simulamos ciclos diarios y variación de sensor para temperatura y humedad.
    temperatura = 24 + 4 * np.sin(2 * np.pi * t / 24 - np.pi / 2) + generador.normal(0, 0.5, n)
    humedad = np.clip(65 - 12 * np.sin(2 * np.pi * t / 24 - np.pi / 2) + generador.normal(0, 2, n), 25, 95)
    # Modelamos sensación térmica como función de temperatura y humedad.
    sensacion = temperatura + 0.025 * (humedad - 50) + generador.normal(0, 0.35, n)
    # Construimos una tabla temporal compatible con la app.
    datos = pd.DataFrame({"fecha": fechas, "temperatura": temperatura, "humedad": humedad, "sensacion_termica": sensacion})
    # Insertamos faltantes para demostrar la interpolación temporal.
    datos.loc[generador.choice(datos.index, 10, replace=False), "humedad"] = np.nan
    return datos


def preparar_datos(datos):
    """Convierte tipos, ordena en tiempo e interpola faltantes de sensores."""
    # Copiamos, tipamos fecha y ordenamos cronológicamente.
    resultado = datos.copy()
    resultado["fecha"] = pd.to_datetime(resultado["fecha"], errors="coerce")
    resultado = resultado.dropna(subset=["fecha"]).sort_values("fecha").set_index("fecha")
    # Convertimos columnas del sensor a números y completamos huecos por tiempo.
    columnas = ["temperatura", "humedad", "sensacion_termica"]
    resultado[columnas] = resultado[columnas].apply(pd.to_numeric, errors="coerce").interpolate(method="time").ffill().bfill()
    # Recuperamos la fecha como columna para visualización.
    return resultado.reset_index()


if __name__ == "__main__":
    # Generamos y limpiamos lecturas del dispositivo IoT.
    datos = preparar_datos(crear_datos_iot())
    # Usamos temperatura y humedad para predecir sensación térmica.
    x, y = datos[["temperatura", "humedad"]], datos["sensacion_termica"]
    # Separamos observaciones de prueba que el modelo no verá al entrenar.
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
    # Ajustamos la regresión lineal múltiple.
    modelo = LinearRegression().fit(x_train, y_train)
    prediccion = modelo.predict(x_test)
    # Reportamos coeficientes y métricas del modelo.
    print("Coeficiente temperatura:", round(modelo.coef_[0], 4))
    print("Coeficiente humedad:", round(modelo.coef_[1], 4))
    print("MAE:", round(mean_absolute_error(y_test, prediccion), 3))
    print("RMSE:", round(mean_squared_error(y_test, prediccion) ** 0.5, 3))
    print("R²:", round(r2_score(y_test, prediccion), 3))
