"""Aplicación Streamlit: KNN para clasificación didáctica de fertilidad de suelos."""

# Importamos recursos para interfaz, manejo de datos, gráficos y KNN.
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


@st.cache_data
def crear_datos_suelo(n_muestras=900, semilla=42):
    """Crea una muestra didáctica de análisis de suelo sin depender de una API."""
    # Inicializamos números aleatorios reproducibles.
    generador = np.random.default_rng(semilla)
    # Creamos un nivel común de nutrientes que aporta realismo a las variables.
    nivel = generador.normal(0, 1, n_muestras)
    # Generamos las tres variables usadas únicamente para construir la etiqueta.
    mo = np.clip(3.8 + 1.5 * nivel + generador.normal(0, 0.8, n_muestras), 0.3, 10)
    p = np.clip(20 + 12 * nivel + generador.normal(0, 8, n_muestras), 1, 90)
    k = np.clip(0.30 + 0.15 * nivel + generador.normal(0, 0.10, n_muestras), 0.03, 1.2)
    # Generamos entradas honestas que no forman parte de la fórmula de fertilidad.
    ph = np.clip(5.8 + 0.35 * nivel + generador.normal(0, 0.55, n_muestras), 3.5, 8.5)
    acidez = np.clip(1.3 - 0.3 * nivel + generador.normal(0, 0.45, n_muestras), 0, 5)
    aluminio = np.clip(1.1 - 0.35 * nivel + generador.normal(0, 0.4, n_muestras), 0, 5)
    calcio = np.clip(4.5 + 1.1 * nivel + generador.normal(0, 1.1, n_muestras), 0.2, 15)
    magnesio = np.clip(1.6 + 0.35 * nivel + generador.normal(0, 0.5, n_muestras), 0.1, 6)
    sodio = np.clip(0.18 + generador.normal(0, 0.07, n_muestras), 0.01, 0.8)
    conductividad = np.clip(0.45 + generador.normal(0, 0.22, n_muestras), 0.02, 2.5)
    hierro = np.clip(80 - 12 * nivel + generador.normal(0, 25, n_muestras), 2, 250)
    zinc = np.clip(3 + 0.4 * nivel + generador.normal(0, 1.2, n_muestras), 0.1, 12)
    # Asignamos puntos con los umbrales didácticos de la guía.
    puntos = (mo >= 3).astype(int) + (mo > 5).astype(int)
    puntos += (p >= 15).astype(int) + (p > 30).astype(int)
    puntos += (k >= 0.2).astype(int) + (k > 0.4).astype(int)
    # Convertimos el puntaje total en una clase de fertilidad.
    fertilidad = np.select([puntos <= 2, puntos <= 4], ["baja", "media"], default="alta")
    # Entregamos la tabla completa, incluidas las variables ocultas que crean la etiqueta.
    return pd.DataFrame(
        {"ph": ph, "acidez": acidez, "aluminio": aluminio, "calcio": calcio,
         "magnesio": magnesio, "sodio": sodio, "conductividad": conductividad,
         "hierro": hierro, "zinc": zinc, "mo": mo, "p": p, "k": k, "fertilidad": fertilidad}
    )


# Configuramos la interfaz antes de crear elementos visibles.
st.set_page_config(page_title="KNN | Fertilidad de suelos", page_icon="🌱", layout="wide")
# Explicamos el objetivo académico y la limitación de los datos simulados.
st.title("KNN: clasificación de fertilidad de suelos")
st.caption("Práctica didáctica inspirada en datos de AGROSAVIA. No sustituye un diagnóstico agronómico profesional.")

# Cargamos la muestra y definimos entradas que no contienen fuga directa de la etiqueta.
datos = crear_datos_suelo()
entradas = ["ph", "acidez", "aluminio", "calcio", "magnesio", "sodio", "conductividad", "hierro", "zinc"]
x = datos[entradas]
y = datos["fertilidad"]

# Permitimos cambiar el número de vecinos para observar sobreajuste y subajuste.
k_vecinos = st.sidebar.slider("Número de vecinos (k)", 1, 51, 15, 2)
# Separamos datos de entrenamiento y prueba manteniendo las clases balanceadas.
x_entrenamiento, x_prueba, y_entrenamiento, y_prueba = train_test_split(
    x, y, test_size=0.25, random_state=42, stratify=y
)
# Creamos una tubería que estandariza y luego aplica KNN sin mezclar datos de prueba.
modelo = Pipeline(
    [("escalador", StandardScaler()), ("knn", KNeighborsClassifier(n_neighbors=k_vecinos, weights="distance"))]
)
modelo.fit(x_entrenamiento, y_entrenamiento)
# Calculamos predicciones reservadas para reportar métricas honestas.
predicciones = modelo.predict(x_prueba)

# Mostramos desempeño global del clasificador.
columna_1, columna_2, columna_3 = st.columns(3)
columna_1.metric("Exactitud en prueba", f"{accuracy_score(y_prueba, predicciones):.1%}")
columna_2.metric("F1 macro", f"{f1_score(y_prueba, predicciones, average='macro'):.1%}")
columna_3.metric("k seleccionado", k_vecinos)

# Presentamos la matriz de confusión para revisar los errores por clase.
figura, eje = plt.subplots(figsize=(5, 4))
ConfusionMatrixDisplay.from_predictions(
    y_prueba, predicciones, labels=["baja", "media", "alta"], cmap="YlGn", colorbar=False, ax=eje
)
eje.set_title("Matriz de confusión en datos de prueba")
eje.grid(False)
st.pyplot(figura)

# Solicitamos valores de una muestra nueva que se clasificará con el modelo.
st.subheader("Diagnóstico de una muestra nueva")
st.write("Completa los valores de laboratorio. Se usan entradas honestas: materia orgánica, fósforo y potasio no se usan como entradas porque definieron la etiqueta didáctica.")
columnas = st.columns(3)
valores_por_defecto = [5.8, 1.3, 1.1, 4.5, 1.6, 0.18, 0.45, 80.0, 3.0]
valores = {}
for indice, (variable, defecto) in enumerate(zip(entradas, valores_por_defecto)):
    # Distribuimos los controles en tres columnas para que la interfaz sea compacta.
    valores[variable] = columnas[indice % 3].number_input(variable.replace("_", " ").title(), min_value=0.0, value=float(defecto))

# Construimos la fila conservando exactamente el orden de las variables de entrenamiento.
muestra = pd.DataFrame([valores], columns=entradas)
# Calculamos la clase y probabilidades aportadas por los vecinos más cercanos.
clase = modelo.predict(muestra)[0]
probabilidades = pd.Series(modelo.predict_proba(muestra)[0], index=modelo.classes_).reindex(["baja", "media", "alta"])
st.success(f"Clasificación estimada: fertilidad {clase.upper()}.")
st.bar_chart(probabilidades)

# Explicamos los principios solicitados por la actividad.
with st.expander("Conceptos y respuestas de la actividad"):
    st.markdown(
        "- **Escalado:** hierro puede tener valores cercanos a cientos, mientras que la conductividad usa decimales; sin estandarizar, hierro dominaría la distancia.\n"
        "- **k pequeño:** con k=1 el modelo memoriza y es sensible al ruido; un k intermedio suele generalizar mejor.\n"
        "- **Fuga de datos:** no se usan materia orgánica, fósforo ni potasio porque esas variables construyeron la etiqueta de fertilidad.\n"
        "- **Interpretación:** KNN compara esta muestra con las más parecidas del conjunto de entrenamiento y las deja votar."
    )
