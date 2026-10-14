"""App Streamlit de la Sesión 7: regresión lineal y métricas."""

# Importamos NumPy, Pandas y Matplotlib para análisis y gráficos.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# Importamos Streamlit para la interfaz.
import streamlit as st
# Importamos California Housing y modelos de regresión.
from sklearn.datasets import fetch_california_housing
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# Configuramos la página de la aplicación.
st.set_page_config(page_title="Sesión 7 | Regresión lineal", page_icon="📈", layout="wide")


@st.cache_data(show_spinner="Cargando California Housing...")
def cargar_datos():
    """Descarga y conserva en caché el dataset oficial de California Housing."""
    # Cargamos el dataset como DataFrame para preservar los nombres de columnas.
    return fetch_california_housing(as_frame=True).frame


def gradiente(x, y, alpha, epochs):
    """Implementa regresión simple mediante descenso de gradiente."""
    # Normalizamos para que la tasa de aprendizaje sea estable.
    media_x, desviacion_x = x.mean(), x.std()
    media_y, desviacion_y = y.mean(), y.std()
    x_norm, y_norm = (x - media_x) / desviacion_x, (y - media_y) / desviacion_y
    # Inicializamos parámetros y costo.
    peso, sesgo, costos = 0.0, 0.0, []
    # Ejecutamos la regla de actualización del descenso de gradiente.
    for _ in range(epochs):
        prediccion = peso * x_norm + sesgo
        error = prediccion - y_norm
        peso -= alpha * (2 / len(x_norm)) * np.sum(error * x_norm)
        sesgo -= alpha * (2 / len(x_norm)) * np.sum(error)
        costos.append(np.mean(error**2))
    # Convertimos la recta normalizada a predicciones en unidades originales.
    predicciones = (peso * x_norm + sesgo) * desviacion_y + media_y
    return peso, sesgo, costos, predicciones


# Escribimos encabezado de la actividad.
st.title("📈 Sesión 7 — Regresión lineal")
st.write("Predice el valor medio de viviendas de California y observa cómo el descenso de gradiente minimiza el error.")

try:
    # Cargamos los datos públicos requeridos por el cuaderno.
    datos = cargar_datos()
except Exception as error:
    # Explicamos un fallo de descarga sin interrumpir con un error técnico crudo.
    st.error(f"No se pudo obtener California Housing: {error}")
    st.stop()

# Permitimos configurar el entrenamiento simple.
st.sidebar.header("Descenso de gradiente")
alpha = st.sidebar.slider("Tasa de aprendizaje α", 0.001, 1.0, 0.1, 0.001)
epochs = st.sidebar.slider("Iteraciones", 10, 1000, 200, 10)
pagina = st.sidebar.radio("Vista", ["Regresión simple", "Regresión múltiple", "Comparación"])

if pagina == "Regresión simple":
    # Definimos MedInc como predictor y MedHouseVal como objetivo.
    x, y = datos["MedInc"].to_numpy(), datos["MedHouseVal"].to_numpy()
    # Entrenamos el modelo con las fórmulas vistas en clase.
    peso, sesgo, costos, predicciones = gradiente(x, y, alpha, epochs)
    # Mostramos el estado final de la optimización.
    columna_1, columna_2, columna_3 = st.columns(3)
    columna_1.metric("Peso normalizado", f"{peso:.4f}")
    columna_2.metric("Sesgo normalizado", f"{sesgo:.4f}")
    columna_3.metric("MSE final", f"{costos[-1]:.5f}")
    # Mostramos datos y la recta predicha sobre una muestra para agilizar el navegador.
    figura, ejes = plt.subplots(1, 2, figsize=(13, 4))
    muestra = np.linspace(0, len(x) - 1, min(3000, len(x)), dtype=int)
    ejes[0].scatter(x[muestra], y[muestra], alpha=0.12, s=8, label="Datos")
    orden = np.argsort(x)
    ejes[0].plot(x[orden], predicciones[orden], color="crimson", linewidth=2, label="Recta por gradiente")
    ejes[0].set(xlabel="Ingreso medio (MedInc)", ylabel="Valor de vivienda", title="Regresión lineal simple")
    ejes[0].legend()
    # Graficamos la disminución de la función de costo.
    ejes[1].plot(costos, color="seagreen")
    ejes[1].set(xlabel="Iteración", ylabel="MSE", title="Convergencia del descenso de gradiente")
    ejes[1].grid(alpha=0.3)
    st.pyplot(figura, clear_figure=True)
    st.info("α muy pequeño converge lentamente; α muy grande puede oscilar o divergir.")

else:
    # Elegimos variables explicativas de la regresión múltiple del cuaderno.
    opciones = ["MedInc", "HouseAge", "AveRooms", "AveBedrms", "Population", "AveOccup", "Latitude", "Longitude"]
    seleccion = st.multiselect("Variables predictoras", opciones, default=opciones[:6])
    # Evitamos entrenar un modelo vacío si se desmarcan todas las variables.
    if not seleccion:
        st.warning("Selecciona al menos una variable predictora.")
        st.stop()
    # Separamos train y test antes de ajustar el modelo.
    x_train, x_test, y_train, y_test = train_test_split(datos[seleccion], datos["MedHouseVal"], test_size=0.2, random_state=42)
    # Entrenamos y predecimos únicamente en datos de prueba.
    modelo = LinearRegression().fit(x_train, y_train)
    predicciones = modelo.predict(x_test)
    # Mostramos R², MAE y RMSE con las unidades originales.
    metrica_1, metrica_2, metrica_3 = st.columns(3)
    metrica_1.metric("R²", f"{r2_score(y_test, predicciones):.3f}")
    metrica_2.metric("MAE", f"{mean_absolute_error(y_test, predicciones):.3f}")
    metrica_3.metric("RMSE", f"{np.sqrt(mean_squared_error(y_test, predicciones)):.3f}")
    # Dibujamos pesos y comparación de valores reales frente a predichos.
    figura, ejes = plt.subplots(1, 2, figsize=(13, 4))
    pd.Series(modelo.coef_, index=seleccion).sort_values().plot(kind="barh", ax=ejes[0], color="steelblue")
    ejes[0].set(title="Coeficientes del modelo", xlabel="Peso")
    ejes[1].scatter(y_test, predicciones, alpha=0.15, s=8)
    limites = [min(y_test.min(), predicciones.min()), max(y_test.max(), predicciones.max())]
    ejes[1].plot(limites, limites, "r--", label="Predicción perfecta")
    ejes[1].set(xlabel="Valor real", ylabel="Valor predicho", title="Evaluación en test")
    ejes[1].legend()
    st.pyplot(figura, clear_figure=True)
    if pagina == "Comparación":
        st.info("Añade Latitude y Longitude y compara R²: la ubicación puede aportar información relevante sobre el precio.")
