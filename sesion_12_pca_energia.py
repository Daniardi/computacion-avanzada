"""Actividad de la sesión 12: visualización, vectores propios y PCA."""

# Importamos las herramientas para datos, gráficos y reducción de dimensionalidad.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA


def crear_perfiles_simulados(dias=136, semilla=42):
    """Crea perfiles horarios de consumo para trabajar sin conexión a internet."""
    # Inicializamos el generador aleatorio para obtener resultados repetibles.
    generador = np.random.default_rng(semilla)
    # Construimos las fechas y horas de todos los días simulados.
    fechas = pd.date_range("2016-01-12", periods=dias * 24, freq="h")
    horas = fechas.hour.to_numpy()
    # Dibujamos picos de consumo en la mañana, al mediodía y al final de la tarde.
    patron = 260 + 220 * np.exp(-((horas - 8) / 2.5) ** 2)
    patron += 320 * np.exp(-((horas - 19) / 3.0) ** 2)
    # Añadimos variación diaria y ruido para evitar que todos los días sean iguales.
    factor_diario = np.repeat(generador.normal(1, 0.25, dias), 24)
    consumo = np.maximum(80, patron * factor_diario + generador.normal(0, 55, len(fechas)))
    # Devolvemos la tabla lista para convertirla en una matriz de perfiles diarios.
    return pd.DataFrame({"fecha": fechas, "consumo_wh": consumo})


if __name__ == "__main__":
    # Generamos los registros horarios de consumo.
    datos = crear_perfiles_simulados()
    # Convertimos cada día en una fila y cada hora en una columna.
    datos["dia"] = datos["fecha"].dt.date
    datos["hora"] = datos["fecha"].dt.hour
    tabla = datos.pivot(index="dia", columns="hora", values="consumo_wh")
    # Centramos los perfiles para que PCA analice la variación respecto al promedio.
    x = tabla.to_numpy()
    x_centrada = x - x.mean(axis=0)
    # Ajustamos PCA y calculamos la proporción de varianza explicada.
    pca = PCA().fit(x_centrada)
    print("Matriz de perfiles:", x.shape)
    print("Varianza explicada por PC1 y PC2:", pca.explained_variance_ratio_[:2].round(3))
    # Graficamos cuánto aporta cada una de las primeras componentes.
    plt.bar(range(1, 6), pca.explained_variance_ratio_[:5])
    plt.xlabel("Componente principal")
    plt.ylabel("Varianza explicada")
    plt.title("Varianza explicada por PCA")
    plt.show()
