"""Sesión 7 — Regresión lineal con California Housing.

Ejecute: python sesion_07_regresion_lineal.py
"""

# Importamos NumPy para los cálculos de descenso de gradiente.
import numpy as np
# Importamos Pandas para presentar coeficientes y métricas.
import pandas as pd
# Importamos herramientas de regresión y evaluación de scikit-learn.
from sklearn.datasets import fetch_california_housing
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


def descenso_gradiente(x, y, alpha=0.1, epochs=200):
    """Ajusta y = w*x + b desde cero minimizando el MSE."""
    # Iniciamos los parámetros del modelo en cero.
    peso, sesgo = 0.0, 0.0
    # Conservamos el costo de cada iteración para verificar convergencia.
    historial = []
    # Repetimos el cálculo de gradientes y la actualización de parámetros.
    for _ in range(epochs):
        # Calculamos predicción y error actuales.
        prediccion = peso * x + sesgo
        error = prediccion - y
        # Derivamos MSE respecto a peso y sesgo.
        gradiente_peso = (2 / len(x)) * np.sum(error * x)
        gradiente_sesgo = (2 / len(x)) * np.sum(error)
        # Damos un paso en dirección contraria al gradiente.
        peso -= alpha * gradiente_peso
        sesgo -= alpha * gradiente_sesgo
        # Registramos el MSE para estudiar la curva de costo.
        historial.append(np.mean(error**2))
    # Retornamos el modelo aprendido y el historial de costo.
    return peso, sesgo, historial


if __name__ == "__main__":
    # Descargamos el dataset real de valores de vivienda en California.
    vivienda = fetch_california_housing(as_frame=True)
    datos = vivienda.frame
    # Seleccionamos ingreso medio como predictor simple y valor como objetivo.
    x = datos["MedInc"].to_numpy()
    y = datos["MedHouseVal"].to_numpy()
    # Estandarizamos ambas variables para estabilizar el descenso de gradiente.
    x_normalizado = (x - x.mean()) / x.std()
    y_normalizado = (y - y.mean()) / y.std()
    # Entrenamos la regresión simple implementada a mano.
    peso, sesgo, costos = descenso_gradiente(x_normalizado, y_normalizado)
    print(f"Regresión por gradiente: w={peso:.4f}, b={sesgo:.4f}, MSE={costos[-1]:.5f}")

    # Separamos datos para evaluar una regresión múltiple sin fuga de información.
    variables = ["MedInc", "HouseAge", "AveRooms", "AveBedrms", "Population", "AveOccup"]
    x_train, x_test, y_train, y_test = train_test_split(datos[variables], y, test_size=0.2, random_state=42)
    # Ajustamos el modelo de seis variables.
    modelo = LinearRegression().fit(x_train, y_train)
    # Generamos predicciones exclusivas para el conjunto de prueba.
    predicciones = modelo.predict(x_test)
    # Calculamos las métricas solicitadas por el cuaderno.
    print("\nMétricas de prueba")
    print(f"MAE: {mean_absolute_error(y_test, predicciones):.3f}")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_test, predicciones)):.3f}")
    print(f"R²: {r2_score(y_test, predicciones):.3f}")
    # Mostramos coeficientes para interpretar el aporte de cada variable.
    print("\nCoeficientes:\n", pd.Series(modelo.coef_, index=variables).sort_values())
