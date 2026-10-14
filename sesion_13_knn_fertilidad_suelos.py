"""Sesión 13: clasificación de fertilidad de suelos con KNN."""

# Importamos librerías para datos, escalado, clasificación y evaluación.
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def crear_datos_suelo(n_muestras=900, semilla=42):
    """Genera un conjunto didáctico inspirado en análisis de suelos."""
    # Fijamos la semilla para que los resultados sean repetibles.
    generador = np.random.default_rng(semilla)
    # Generamos un nivel latente que representa la disponibilidad general de nutrientes.
    nivel = generador.normal(0, 1, n_muestras)
    # Creamos las tres variables que definen la etiqueta de fertilidad.
    materia_organica = np.clip(3.8 + 1.5 * nivel + generador.normal(0, 0.8, n_muestras), 0.3, 10)
    fosforo = np.clip(20 + 12 * nivel + generador.normal(0, 8, n_muestras), 1, 90)
    potasio = np.clip(0.30 + 0.15 * nivel + generador.normal(0, 0.10, n_muestras), 0.03, 1.2)
    # Construimos variables honestas que se relacionan con el suelo, pero no definen la clase.
    ph = np.clip(5.8 + 0.35 * nivel + generador.normal(0, 0.55, n_muestras), 3.5, 8.5)
    acidez = np.clip(1.3 - 0.3 * nivel + generador.normal(0, 0.45, n_muestras), 0, 5)
    aluminio = np.clip(1.1 - 0.35 * nivel + generador.normal(0, 0.4, n_muestras), 0, 5)
    calcio = np.clip(4.5 + 1.1 * nivel + generador.normal(0, 1.1, n_muestras), 0.2, 15)
    magnesio = np.clip(1.6 + 0.35 * nivel + generador.normal(0, 0.5, n_muestras), 0.1, 6)
    sodio = np.clip(0.18 + generador.normal(0, 0.07, n_muestras), 0.01, 0.8)
    conductividad = np.clip(0.45 + generador.normal(0, 0.22, n_muestras), 0.02, 2.5)
    hierro = np.clip(80 - 12 * nivel + generador.normal(0, 25, n_muestras), 2, 250)
    zinc = np.clip(3 + 0.4 * nivel + generador.normal(0, 1.2, n_muestras), 0.1, 12)
    # Sumamos puntos didácticos para obtener la clase baja, media o alta.
    puntos = (materia_organica >= 3).astype(int) + (materia_organica > 5).astype(int)
    puntos += (fosforo >= 15).astype(int) + (fosforo > 30).astype(int)
    puntos += (potasio >= 0.2).astype(int) + (potasio > 0.4).astype(int)
    fertilidad = np.select([puntos <= 2, puntos <= 4], ["baja", "media"], default="alta")
    # Reunimos variables y la etiqueta en una sola tabla.
    return pd.DataFrame(
        {"ph": ph, "acidez": acidez, "aluminio": aluminio, "calcio": calcio,
         "magnesio": magnesio, "sodio": sodio, "conductividad": conductividad,
         "hierro": hierro, "zinc": zinc, "mo": materia_organica, "p": fosforo,
         "k": potasio, "fertilidad": fertilidad}
    )


if __name__ == "__main__":
    # Creamos los datos y seleccionamos solo entradas honestas para evitar fuga de información.
    datos = crear_datos_suelo()
    entradas = ["ph", "acidez", "aluminio", "calcio", "magnesio", "sodio", "conductividad", "hierro", "zinc"]
    x = datos[entradas]
    y = datos["fertilidad"]
    # Separamos entrenamiento y prueba conservando la proporción de las tres clases.
    x_entrenamiento, x_prueba, y_entrenamiento, y_prueba = train_test_split(
        x, y, test_size=0.25, random_state=42, stratify=y
    )
    # Escalamos antes de KNN para que hierro no domine por tener valores más grandes.
    modelo = Pipeline([("escalador", StandardScaler()), ("knn", KNeighborsClassifier(n_neighbors=15, weights="distance"))])
    modelo.fit(x_entrenamiento, y_entrenamiento)
    # Mostramos métricas de la evaluación reservada.
    print(classification_report(y_prueba, modelo.predict(x_prueba), zero_division=0))
