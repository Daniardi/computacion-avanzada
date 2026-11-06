"""Aplicación Streamlit de la sesión 15: POO aplicada a modelos de energía."""

# Importamos interfaz, datos, gráficos y división de entrenamiento/prueba.
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.model_selection import train_test_split

# Importamos el paquete local creado como parte de la práctica.
from energia_ml import ClasificadorEstricto, Estandarizador, FlujoModelo, RegresionLineal, RegresionLogistica


@st.cache_data
def crear_datos_energia(n_registros=400, semilla=42):
    """Genera el conjunto reproducible de lecturas energéticas usado por la sesión."""
    # Inicializamos un generador aleatorio para mantener los mismos datos en cada ejecución.
    generador = np.random.default_rng(semilla)
    # Simulamos las entradas registradas por los sensores del edificio.
    temperatura = generador.uniform(18, 34, n_registros)
    ocupacion = generador.integers(0, 51, n_registros)
    humedad = generador.uniform(40, 90, n_registros)
    # Generamos el consumo energético con ruido para representar mediciones reales.
    consumo = 5 + 1.8 * temperatura + 0.9 * ocupacion + 0.05 * humedad + generador.normal(0, 4, n_registros)
    # Construimos la tabla y la etiqueta binaria para el clasificador.
    datos = pd.DataFrame({"temperatura": temperatura, "ocupacion": ocupacion, "humedad": humedad, "consumo_kwh": consumo})
    datos["consumo_alto"] = (datos["consumo_kwh"] > datos["consumo_kwh"].median()).astype(int)
    return datos


@st.cache_resource
def entrenar_flujos(iteraciones):
    """Entrena objetos de regresión y clasificación una sola vez por configuración."""
    # Obtenemos datos y convertimos las columnas necesarias en arreglos de NumPy.
    datos = crear_datos_energia()
    x = datos[["temperatura", "ocupacion", "humedad"]].to_numpy()
    y_regresion = datos["consumo_kwh"].to_numpy()
    y_clasificacion = datos["consumo_alto"].to_numpy()
    # Conservamos el mismo conjunto de prueba para las tres comparaciones.
    division = train_test_split(x, y_regresion, y_clasificacion, test_size=0.25, random_state=42)
    x_entrenamiento, x_prueba, yreg_entrenamiento, yreg_prueba, ycla_entrenamiento, ycla_prueba = division
    # Entrenamos el flujo de regresión usando composición de estandarizador y modelo.
    regresor = FlujoModelo(Estandarizador(), RegresionLineal(iteraciones=iteraciones)).entrenar(x_entrenamiento, yreg_entrenamiento)
    # Entrenamos el clasificador normal con la misma interfaz de flujo.
    clasificador = FlujoModelo(Estandarizador(), RegresionLogistica(tasa=0.5, iteraciones=iteraciones)).entrenar(x_entrenamiento, ycla_entrenamiento)
    # Entrenamos la hija que cambia únicamente el umbral de predicción.
    estricto = FlujoModelo(Estandarizador(), ClasificadorEstricto(tasa=0.5, iteraciones=iteraciones)).entrenar(x_entrenamiento, ycla_entrenamiento)
    return regresor, clasificador, estricto, x_prueba, yreg_prueba, ycla_prueba


# Configuramos la página antes de emitir cualquier componente de Streamlit.
st.set_page_config(page_title="Sesión 15 | POO para IA", page_icon="🧱", layout="wide")
# Explicamos el objetivo de modularizar modelos de aprendizaje automático.
st.title("Sesión 15: POO para IA y modelos reutilizables")
st.write("La aplicación combina encapsulación, herencia, polimorfismo y composición usando modelos de consumo energético.")

# Permitimos experimentar con la duración del entrenamiento.
iteraciones = st.sidebar.slider("Iteraciones de entrenamiento", 100, 1500, 800, 100)
# Recuperamos los tres flujos ya entrenados para esta configuración.
regresor, clasificador, estricto, x_prueba, yreg_prueba, ycla_prueba = entrenar_flujos(iteraciones)

# Mostramos métricas para comparar los objetos que responden a la misma interfaz.
columna_1, columna_2, columna_3 = st.columns(3)
columna_1.metric("R2 de RegresionLineal", f"{regresor.evaluar(x_prueba, yreg_prueba):.3f}")
columna_2.metric("Exactitud logística", f"{clasificador.evaluar(x_prueba, ycla_prueba):.1%}")
columna_3.metric("Exactitud estricta (0.8)", f"{estricto.evaluar(x_prueba, ycla_prueba):.1%}")

# Organizamos la explicación y la exploración en pestañas independientes.
pestana_modelos, pestana_prediccion, pestana_retos = st.tabs(["Modelos y herencia", "Inferencia", "Retos y respuestas"])

with pestana_modelos:
    # Comparamos la evolución del costo heredado desde ModeloBase.
    figura, ejes = plt.subplots(1, 2, figsize=(11, 4))
    ejes[0].plot(regresor.modelo.historial, color="tab:blue")
    ejes[0].set_title("RegresionLineal: costo MSE")
    ejes[0].set_xlabel("Iteración")
    ejes[0].set_ylabel("Error cuadrático medio")
    ejes[1].plot(clasificador.modelo.historial, color="tab:green")
    ejes[1].set_title("RegresionLogistica: log-loss")
    ejes[1].set_xlabel("Iteración")
    ejes[1].set_ylabel("Entropía cruzada")
    figura.tight_layout()
    st.pyplot(figura)
    # Resaltamos qué código se comparte y cuál se especializa mediante herencia.
    st.info("ModeloBase comparte fit y el descenso de gradiente. Cada hija define únicamente activación, costo y forma de predecir.")

with pestana_prediccion:
    # Pedimos una lectura cruda, tal como llegaría desde un sensor.
    columna_temp, columna_ocupacion, columna_humedad = st.columns(3)
    temperatura = columna_temp.number_input("Temperatura (°C)", value=30.0)
    ocupacion = columna_ocupacion.number_input("Ocupación (personas)", min_value=0.0, value=40.0)
    humedad = columna_humedad.number_input("Humedad (%)", min_value=0.0, max_value=100.0, value=60.0)
    # Enviamos los datos crudos al flujo; el objeto se encarga de estandarizar internamente.
    lectura = np.array([[temperatura, ocupacion, humedad]])
    consumo = regresor.predecir(lectura)[0]
    probabilidad = clasificador.modelo.predict_proba(clasificador.preprocesador.transform(lectura))[0]
    alto_normal = clasificador.predecir(lectura)[0]
    alto_estricto = estricto.predecir(lectura)[0]
    # Comunicamos las predicciones de regresión y ambas reglas de clasificación.
    st.success(f"Consumo estimado: {consumo:.1f} kWh.")
    st.write(f"Probabilidad de consumo alto: **{probabilidad:.1%}**.")
    st.write(f"Regla estándar: **{'alto' if alto_normal else 'no alto'}** | Regla estricta: **{'alto' if alto_estricto else 'no alto'}**.")

with pestana_retos:
    # Respondemos los retos y preguntas de reflexión de la guía.
    st.markdown(
        """
        **Reto 1.** El método mae se agrega solo a RegresionLineal, porque es una métrica específica de regresión; no se modifica ModeloBase.

        **Reto 2.** ClasificadorEstricto hereda el entrenamiento y solo sobrescribe predict. Con umbral 0.8 predice menos positivos: puede reducir falsos positivos, pero aumentar falsos negativos.

        **Reto 3.** FlujoModelo funciona con un modelo de scikit-learn porque ambos respetan el contrato fit, predict y score.

        1. Tener fit una sola vez permite corregir el entrenamiento en un único lugar y todas las hijas reciben la mejora.
        2. Usar fit con una lectura nueva reemplazaría media y desviación; el modelo recibiría una escala distinta a la usada al entrenar.
        3. Para escalar entre cero y uno se agrega otro preprocesador en preprocesamiento.py; modelos.py y flujo.py pueden mantenerse sin cambios.
        """
    )
