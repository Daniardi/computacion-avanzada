"""Sesión 15: POO para IA, herencia, polimorfismo y paquete reutilizable."""

# Importamos herramientas para datos y la separación de entrenamiento/prueba.
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# Importamos las clases creadas en el paquete local energia_ml.
from energia_ml import ClasificadorEstricto, Estandarizador, FlujoModelo, RegresionLineal, RegresionLogistica


def crear_datos_energia(n_registros=400, semilla=42):
    """Simula lecturas horarias de un edificio para regresión y clasificación."""
    # Generamos datos reproducibles para que el resultado pueda verificarse.
    generador = np.random.default_rng(semilla)
    # Simulamos temperatura, ocupación y humedad como entradas del modelo.
    temperatura = generador.uniform(18, 34, n_registros)
    ocupacion = generador.integers(0, 51, n_registros)
    humedad = generador.uniform(40, 90, n_registros)
    # Construimos consumo con una relación lineal y ruido de medición.
    consumo = 5 + 1.8 * temperatura + 0.9 * ocupacion + 0.05 * humedad + generador.normal(0, 4, n_registros)
    # Organizamos todos los registros en una tabla.
    datos = pd.DataFrame({"temperatura": temperatura, "ocupacion": ocupacion, "humedad": humedad, "consumo_kwh": consumo})
    # Creamos la clase binaria que identifica consumo superior a la mediana.
    datos["consumo_alto"] = (datos["consumo_kwh"] > datos["consumo_kwh"].median()).astype(int)
    return datos


if __name__ == "__main__":
    # Seleccionamos entradas y objetivos de regresión y clasificación.
    datos = crear_datos_energia()
    x = datos[["temperatura", "ocupacion", "humedad"]].to_numpy()
    y_regresion = datos["consumo_kwh"].to_numpy()
    y_clasificacion = datos["consumo_alto"].to_numpy()
    # Reservamos datos de prueba antes de entrenar los flujos.
    x_entrenamiento, x_prueba, yreg_entrenamiento, yreg_prueba, ycla_entrenamiento, ycla_prueba = train_test_split(
        x, y_regresion, y_clasificacion, test_size=0.25, random_state=42
    )
    # Entrenamos regresión y clasificación con la misma interfaz de FlujoModelo.
    flujo_regresion = FlujoModelo(Estandarizador(), RegresionLineal(iteraciones=1000)).entrenar(x_entrenamiento, yreg_entrenamiento)
    flujo_clasificacion = FlujoModelo(Estandarizador(), RegresionLogistica(tasa=0.5, iteraciones=1000)).entrenar(x_entrenamiento, ycla_entrenamiento)
    # Mostramos las métricas de ambos objetos polimórficos.
    print("R2 de regresión:", round(flujo_regresion.evaluar(x_prueba, yreg_prueba), 3))
    print("Exactitud de clasificación:", round(flujo_clasificacion.evaluar(x_prueba, ycla_prueba), 3))
    # Comparamos la decisión estándar con la decisión estricta del reto 2.
    estricto = FlujoModelo(Estandarizador(), ClasificadorEstricto(tasa=0.5, iteraciones=1000)).entrenar(x_entrenamiento, ycla_entrenamiento)
    print("Exactitud de clasificador estricto:", round(estricto.evaluar(x_prueba, ycla_prueba), 3))
