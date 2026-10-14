"""Actividad de la sesión 11: clasificación de lluvia con regresión logística."""

# Importamos las librerías necesarias para datos y el modelo de clasificación.
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split


def crear_datos(n_registros=300, semilla=42):
    """Crea datos meteorológicos simulados y una etiqueta binaria de lluvia."""
    # Fijamos una semilla para que la práctica sea reproducible.
    generador = np.random.default_rng(semilla)
    # Simulamos las tres variables explicativas de cada día.
    temperatura = generador.normal(24, 5, n_registros)
    humedad = generador.normal(65, 15, n_registros)
    viento = generador.normal(10, 5, n_registros)
    # Calculamos el puntaje lineal que determina la probabilidad de lluvia.
    puntaje = -6 + 0.09 * humedad - 0.05 * temperatura + 0.02 * viento
    # Convertimos el puntaje en una probabilidad entre cero y uno con sigmoide.
    probabilidad_lluvia = 1 / (1 + np.exp(-puntaje))
    # Generamos la clase: 1 significa que llovió y 0 que no llovió.
    llovio = (generador.random(n_registros) < probabilidad_lluvia).astype(int)
    # Reunimos los datos en una tabla para analizarlos fácilmente.
    return pd.DataFrame({"temperatura": temperatura, "humedad": humedad, "viento": viento, "llovio": llovio})


if __name__ == "__main__":
    # Construimos el conjunto de datos de la actividad.
    datos = crear_datos()
    # Definimos las entradas del modelo y la variable que queremos predecir.
    caracteristicas = datos[["temperatura", "humedad", "viento"]]
    objetivo = datos["llovio"]
    # Separamos datos de entrenamiento y prueba conservando la proporción de clases.
    x_entrenamiento, x_prueba, y_entrenamiento, y_prueba = train_test_split(
        caracteristicas, objetivo, test_size=0.25, random_state=42, stratify=objetivo
    )
    # Ajustamos el clasificador de regresión logística con los datos de entrenamiento.
    modelo = LogisticRegression(max_iter=1000)
    modelo.fit(x_entrenamiento, y_entrenamiento)
    # Calculamos las predicciones binarias en los datos reservados para prueba.
    predicciones = modelo.predict(x_prueba)
    # Mostramos métricas básicas para evaluar el clasificador.
    print("Exactitud:", round(accuracy_score(y_prueba, predicciones), 3))
    print("Precisión:", round(precision_score(y_prueba, predicciones, zero_division=0), 3))
    print("Recall:", round(recall_score(y_prueba, predicciones, zero_division=0), 3))
