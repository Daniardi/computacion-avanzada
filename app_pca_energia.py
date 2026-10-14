"""Aplicación Streamlit de la sesión 12: análisis energético con PCA."""

# Importamos las librerías necesarias para la interfaz, los datos, gráficos y PCA.
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.decomposition import PCA


@st.cache_data
def crear_perfiles_simulados(dias=136, semilla=42):
    """Crea datos horarios de respaldo cuando no se logra descargar la fuente."""
    # Fijamos la semilla para que la simulación sea reproducible.
    generador = np.random.default_rng(semilla)
    # Creamos 24 observaciones horarias para cada día de la actividad.
    fechas = pd.date_range("2016-01-12", periods=dias * 24, freq="h")
    horas = fechas.hour.to_numpy()
    # Modelamos picos típicos de consumo en mañana, mediodía y tarde.
    patron = 250 + 180 * np.exp(-((horas - 8) / 2.5) ** 2)
    patron += 110 * np.exp(-((horas - 13) / 2.0) ** 2)
    patron += 330 * np.exp(-((horas - 19) / 3.0) ** 2)
    # Aplicamos variación por día y ruido para construir perfiles diferentes.
    factor_diario = np.repeat(generador.normal(1, 0.25, dias), 24)
    consumo = np.maximum(80, patron * factor_diario + generador.normal(0, 55, len(fechas)))
    # Organizamos las dos columnas que se emplean durante toda la práctica.
    return pd.DataFrame({"fecha": fechas, "consumo_wh": consumo})


@st.cache_data
def cargar_datos():
    """Descarga la fuente original y usa un respaldo si no hay conectividad."""
    # Definimos la ubicación pública del conjunto de consumo energético.
    url = "https://raw.githubusercontent.com/LuisM78/Appliances-energy-prediction-data/master/energydata_complete.csv"
    try:
        # Leemos fecha y consumo de electrodomésticos desde la fuente de la guía.
        datos = pd.read_csv(url, usecols=["date", "Appliances"], parse_dates=["date"])
        # Renombramos las variables para que sean claras en español.
        datos.columns = ["fecha", "consumo_wh"]
        # Convertimos los registros de diez minutos en consumo total por hora.
        datos = datos.set_index("fecha")["consumo_wh"].resample("h").sum().reset_index()
        origen = "Fuente original: Appliances Energy Prediction (UCI)."
    except Exception:
        # Mantenemos la aplicación funcional cuando el sitio de datos no responde.
        datos = crear_perfiles_simulados()
        origen = "Datos simulados de respaldo: no se pudo descargar la fuente externa."

    # Creamos columnas auxiliares para formar un perfil de 24 horas por día.
    datos["dia"] = datos["fecha"].dt.date
    datos["hora"] = datos["fecha"].dt.hour
    # Conservamos únicamente los días que tienen las 24 horas completas.
    datos = datos.groupby("dia").filter(lambda grupo: grupo["hora"].nunique() == 24)
    # Cada fila de la matriz representa un día y cada columna una hora.
    tabla = datos.pivot_table(index="dia", columns="hora", values="consumo_wh", aggfunc="mean")
    return datos, tabla, origen


# Configuramos la página antes de generar cualquier componente de Streamlit.
st.set_page_config(page_title="Sesión 12 | PCA de energía", page_icon="⚡", layout="wide")
# Presentamos el tema de la actividad.
st.title("Sesión 12: visualización, vectores propios y PCA")
st.write("Cada punto es un día de consumo. PCA reduce un perfil de 24 horas a componentes que resumen sus patrones principales.")

# Cargamos y preparamos los datos para el análisis.
datos, tabla, origen = cargar_datos()
st.caption(origen)

# Construimos la matriz de perfiles y la centramos respecto al día promedio.
x = tabla.to_numpy()
x_centrada = x - x.mean(axis=0)
# Ajustamos PCA sobre los perfiles centrados y proyectamos cada día en PC1 y PC2.
pca = PCA()
proyeccion = pca.fit_transform(x_centrada)
varianza = pca.explained_variance_ratio_
varianza_acumulada = np.cumsum(varianza)

# Permitimos que el usuario cambie la visualización principal.
opcion = st.sidebar.selectbox(
    "Visualización",
    ["Resumen y gráficos", "Componentes principales", "Días en PC1–PC2"],
)

if opcion == "Resumen y gráficos":
    # Calculamos consumo total por día y mediana de consumo por hora.
    diario = datos.groupby("dia")["consumo_wh"].sum() / 1000
    perfil = datos.groupby("hora")["consumo_wh"].median()
    # Mostramos los cuatro tipos de gráficos solicitados en la actividad.
    figura, ejes = plt.subplots(2, 2, figsize=(12, 7))
    ejes[0, 0].plot(pd.to_datetime(diario.index), diario, color="tab:blue")
    ejes[0, 0].set_title("Línea: consumo diario a lo largo del tiempo")
    ejes[0, 0].set_ylabel("kWh por día")
    ejes[0, 1].bar(perfil.index, perfil, color="tab:orange")
    ejes[0, 1].set_title("Barras: consumo típico por hora")
    ejes[0, 1].set_ylabel("Wh por hora")
    ejes[1, 0].hist(diario, bins=20, edgecolor="white", color="tab:green")
    ejes[1, 0].set_title("Histograma: distribución del consumo diario")
    ejes[1, 0].set_xlabel("kWh por día")
    ejes[1, 1].imshow(tabla, aspect="auto", cmap="Reds")
    ejes[1, 1].set_title("Mapa de calor: patrón por día y hora")
    ejes[1, 1].set_xlabel("Hora")
    ejes[1, 1].set_ylabel("Día")
    figura.tight_layout()
    st.pyplot(figura)
    st.info("El gráfico de línea permite identificar cuándo cambia el consumo; el histograma no conserva el orden temporal.")

elif opcion == "Componentes principales":
    # Elegimos cuántas componentes se desean observar, sin exceder el total disponible.
    limite = min(10, len(varianza))
    cantidad = st.slider("Componentes a mostrar", 2, limite, min(5, limite))
    # Dibujamos varianza individual y acumulada para evaluar la reducción dimensional.
    figura, eje = plt.subplots(figsize=(10, 4))
    componentes = np.arange(1, cantidad + 1)
    eje.bar(componentes, varianza[:cantidad], color="tab:orange", label="Varianza individual")
    eje.plot(componentes, varianza_acumulada[:cantidad], "o-", color="black", label="Varianza acumulada")
    eje.set_xlabel("Componente principal")
    eje.set_ylabel("Proporción de varianza")
    eje.set_title("Las primeras componentes resumen la variación entre perfiles")
    eje.legend()
    st.pyplot(figura)
    # Mostramos los pesos horarios de PC1 y PC2 para interpretarlas.
    figura, ejes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    for indice, eje in enumerate(ejes):
        pesos = pca.components_[indice]
        eje.bar(range(24), pesos, color=np.where(pesos >= 0, "tab:orange", "tab:purple"))
        eje.axhline(0, color="black", linewidth=0.8)
        eje.set_ylabel(f"PC{indice + 1}")
        eje.set_title(f"Pesos horarios de PC{indice + 1} ({varianza[indice]:.1%} de varianza)")
    ejes[1].set_xlabel("Hora del día")
    figura.tight_layout()
    st.pyplot(figura)

else:
    # Determinamos cuáles fechas corresponden a sábado o domingo.
    fechas = pd.to_datetime(tabla.index)
    fin_semana = fechas.dayofweek >= 5
    # Graficamos cada perfil diario usando sus dos primeras coordenadas PCA.
    figura, eje = plt.subplots(figsize=(9, 6))
    eje.scatter(proyeccion[~fin_semana, 0], proyeccion[~fin_semana, 1], color="lightgray", label="Entre semana")
    eje.scatter(proyeccion[fin_semana, 0], proyeccion[fin_semana, 1], color="tab:red", label="Fin de semana")
    eje.scatter(0, 0, marker="X", s=120, color="black", label="Día promedio")
    eje.axhline(0, color="black", linewidth=0.6)
    eje.axvline(0, color="black", linewidth=0.6)
    eje.set_xlabel(f"PC1 ({varianza[0]:.1%} de varianza)")
    eje.set_ylabel(f"PC2 ({varianza[1]:.1%} de varianza)")
    eje.set_title("Cada punto es un perfil diario de consumo")
    eje.legend()
    st.pyplot(figura)
    st.info("Los días alejados del centro tienen un perfil de consumo más diferente al promedio.")

# Cerramos con respuestas cortas que conectan la interfaz con las preguntas de la guía.
with st.expander("Respuestas de reflexión"):
    st.markdown(
        "1. Un día raro queda lejos del centro porque sus 24 consumos horarios difieren mucho del perfil promedio.\n\n"
        "2. Con 50 sensores, PCA permite proyectar cada observación en PC1 y PC2 para verla en un gráfico de dos dimensiones.\n\n"
        "3. Para promover ahorro se recomienda el gráfico de barras por hora, con un título como: "
        "'El consumo aumenta al final de la tarde: desconectar equipos en espera ayuda a reducirlo.'"
    )
