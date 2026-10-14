"""Aplicación Streamlit de la sesión 11: regresión logística para lluvia."""

# Importamos las librerías para la interfaz, los gráficos y el aprendizaje automático.
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score
from sklearn.model_selection import train_test_split


@st.cache_data
def crear_datos(n_registros=300, semilla=42):
    """Genera el conjunto de datos meteorológicos sintético de la actividad."""
    # Usamos una semilla fija para mantener resultados reproducibles.
    generador = np.random.default_rng(semilla)
    # Creamos temperatura, humedad y velocidad del viento de días simulados.
    temperatura = generador.normal(24, 5, n_registros)
    humedad = generador.normal(65, 15, n_registros)
    viento = generador.normal(10, 5, n_registros)
    # Estimamos un puntaje lineal: la humedad tiene la mayor influencia positiva.
    puntaje = -6 + 0.09 * humedad - 0.05 * temperatura + 0.02 * viento
    # Transformamos el puntaje en una probabilidad mediante la función sigmoide.
    probabilidad_lluvia = 1 / (1 + np.exp(-puntaje))
    # Etiquetamos cada día como lluvia (1) o no lluvia (0) según su probabilidad.
    llovio = (generador.random(n_registros) < probabilidad_lluvia).astype(int)
    # Devolvemos los datos organizados en una tabla.
    return pd.DataFrame({"temperatura": temperatura, "humedad": humedad, "viento": viento, "llovio": llovio})


# Configuramos los datos generales de la página antes de mostrar componentes.
st.set_page_config(page_title="Sesión 11 | Regresión logística", page_icon="🌧️")
# Mostramos el título y el objetivo principal de la actividad.
st.title("Sesión 11: de regresión lineal a regresión logística")
st.write("Predicción de lluvia a partir de temperatura, humedad y velocidad del viento. Modifica el umbral y observa cómo cambian las métricas.")

# Permitimos experimentar con el umbral de decisión y con la variable viento.
umbral = st.sidebar.slider("Umbral de lluvia", 0.10, 0.90, 0.50, 0.05)
# Usamos checkbox porque es compatible con versiones antiguas y recientes de Streamlit.
usar_viento = st.sidebar.checkbox("Incluir velocidad del viento", value=True)
# Obtenemos la tabla simulada y definimos las columnas que alimentarán el modelo.
datos = crear_datos()
variables = ["temperatura", "humedad"]
if usar_viento:
    # Añadimos viento solo cuando el usuario desea incluirlo en el experimento.
    variables.append("viento")
# Separamos la tabla en entradas y salida binaria.
x = datos[variables]
y = datos["llovio"]
# Reservamos 25 % de los datos para una evaluación independiente.
x_entrenamiento, x_prueba, y_entrenamiento, y_prueba = train_test_split(
    x, y, test_size=0.25, random_state=42, stratify=y
)
# Entrenamos el clasificador usando únicamente los datos de entrenamiento.
modelo = LogisticRegression(max_iter=1000)
modelo.fit(x_entrenamiento, y_entrenamiento)
# Obtenemos probabilidades y las convertimos a clases con el umbral seleccionado.
probabilidades = modelo.predict_proba(x_prueba)[:, 1]
predicciones = (probabilidades >= umbral).astype(int)
# Calculamos la matriz de confusión para identificar aciertos y errores.
matriz = confusion_matrix(y_prueba, predicciones, labels=[0, 1])
verdaderos_negativos, falsos_positivos, falsos_negativos, verdaderos_positivos = matriz.ravel()

# Resumimos las métricas de evaluación en columnas visibles.
columna_1, columna_2, columna_3, columna_4 = st.columns(4)
columna_1.metric("Exactitud", f"{accuracy_score(y_prueba, predicciones):.2%}")
columna_2.metric("Precisión", f"{precision_score(y_prueba, predicciones, zero_division=0):.2%}")
columna_3.metric("Recall", f"{recall_score(y_prueba, predicciones, zero_division=0):.2%}")
columna_4.metric("Días predichos con lluvia", int(predicciones.sum()))

# Dibujamos la matriz de confusión y los coeficientes en una misma figura.
figura, ejes = plt.subplots(1, 2, figsize=(11, 4))
imagen = ejes[0].imshow(matriz, cmap="Blues")
ejes[0].set_title("Matriz de confusión")
ejes[0].set_xticks([0, 1], ["No lluvia", "Lluvia"])
ejes[0].set_yticks([0, 1], ["No lluvia", "Lluvia"])
ejes[0].set_xlabel("Predicción")
ejes[0].set_ylabel("Real")
for fila in range(2):
    for columna in range(2):
        # Escribimos cada cantidad dentro de su celda de la matriz.
        ejes[0].text(columna, fila, matriz[fila, columna], ha="center", va="center")
figura.colorbar(imagen, ax=ejes[0], fraction=0.046)
# Asociamos cada coeficiente aprendido con el nombre de su variable.
coeficientes = pd.Series(modelo.coef_[0], index=variables).sort_values()
coeficientes.plot.barh(ax=ejes[1], color="#1f77b4")
ejes[1].axvline(0, color="black", linewidth=0.8)
ejes[1].set_title("Coeficientes del modelo")
ejes[1].set_xlabel("Cambio en log-odds de lluvia")
figura.tight_layout()
st.pyplot(figura)

# Presentamos una lectura corta de los cuatro valores de la matriz.
st.info(f"VN: {verdaderos_negativos} | FP: {falsos_positivos} | FN: {falsos_negativos} | VP: {verdaderos_positivos}. Un falso negativo implica no llevar paraguas cuando realmente llueve.")

# Permitimos evaluar manualmente las condiciones de un nuevo día.
st.subheader("Predicción para un nuevo día")
columna_temp, columna_humedad, columna_viento = st.columns(3)
temperatura_nueva = columna_temp.number_input("Temperatura (°C)", value=24.0)
humedad_nueva = columna_humedad.number_input("Humedad (%)", value=65.0, min_value=0.0, max_value=100.0)
viento_nuevo = columna_viento.number_input("Viento (km/h)", value=10.0, min_value=0.0)
# Preparamos una fila con exactamente las mismas columnas usadas durante el entrenamiento.
nuevo_dia = pd.DataFrame([{"temperatura": temperatura_nueva, "humedad": humedad_nueva, "viento": viento_nuevo}])[variables]
# Calculamos y comunicamos la probabilidad pronosticada para el nuevo día.
probabilidad_nueva = modelo.predict_proba(nuevo_dia)[0, 1]
resultado = "Lloverá" if probabilidad_nueva >= umbral else "No lloverá"
st.success(f"{resultado} según el umbral {umbral:.2f}. Probabilidad estimada: {probabilidad_nueva:.2%}.")

# Dejamos disponibles algunos registros para que se conozca la estructura de los datos.
with st.expander("Ver datos simulados"):
    st.dataframe(datos.head(15), use_container_width=True)
