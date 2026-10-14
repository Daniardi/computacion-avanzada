"""App Streamlit de la Sesión 10: pipeline IoT y sensación térmica."""

# Importamos librerías para datos, gráficos y modelado.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# Configuramos la página de la aplicación.
st.set_page_config(page_title="Sesión 10 | IoT y sensación térmica", page_icon="🌡️", layout="wide")


@st.cache_data
def datos_demo(n=480):
    """Crea datos reproducibles de un DHT22 para demostrar el pipeline IoT."""
    # Creamos tiempo, ciclos diarios y ruido de medición.
    generador, t = np.random.default_rng(42), np.arange(n)
    temperatura = 24 + 4 * np.sin(2 * np.pi * t / 24 - np.pi / 2) + generador.normal(0, 0.5, n)
    humedad = np.clip(65 - 12 * np.sin(2 * np.pi * t / 24 - np.pi / 2) + generador.normal(0, 2, n), 25, 95)
    sensacion = temperatura + 0.025 * (humedad - 50) + generador.normal(0, 0.35, n)
    # Entregamos las lecturas con fechas horarias.
    datos = pd.DataFrame({"fecha": pd.date_range("2026-09-01", periods=n, freq="h"), "temperatura": temperatura, "humedad": humedad, "sensacion_termica": sensacion})
    datos.loc[generador.choice(datos.index, 10, replace=False), "humedad"] = np.nan
    return datos


def preparar(datos):
    """Estandariza nombres, tipos y valores faltantes de un CSV de IoT."""
    # Copiamos para no modificar el archivo original cargado por la persona.
    resultado = datos.copy()
    # Localizamos una columna de fecha compatible con formatos comunes.
    columna_fecha = next((c for c in ["fecha", "timestamp", "_time"] if c in resultado.columns), None)
    if columna_fecha is None:
        raise ValueError("El CSV debe incluir una columna fecha, timestamp o _time.")
    # Renombramos la fecha a un nombre consistente y la convertimos a datetime.
    resultado = resultado.rename(columns={columna_fecha: "fecha"})
    resultado["fecha"] = pd.to_datetime(resultado["fecha"], errors="coerce")
    # Verificamos que las tres mediciones requeridas estén disponibles.
    requeridas = ["temperatura", "humedad", "sensacion_termica"]
    if not set(requeridas).issubset(resultado.columns):
        raise ValueError("El CSV requiere: temperatura, humedad y sensacion_termica.")
    # Tipamos las mediciones, ordenamos e interpolamos los huecos temporales.
    resultado = resultado.dropna(subset=["fecha"]).sort_values("fecha").set_index("fecha")
    resultado[requeridas] = resultado[requeridas].apply(pd.to_numeric, errors="coerce").interpolate(method="time").ffill().bfill()
    return resultado.reset_index()


def outliers_iqr(serie):
    """Identifica posibles outliers estadísticos con IQR de 1.5."""
    # Calculamos cuartiles y límites del criterio IQR.
    q1, q3 = serie.quantile(.25), serie.quantile(.75)
    inferior, superior = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
    return (serie < inferior) | (serie > superior)


# Mostramos encabezado y opción de cargar datos propios sin credenciales expuestas.
st.title("🌡️ Sesión 10 — IoT: captura y predicción de sensación térmica")
st.write("Analiza un DHT22, prepara sus datos y predice la sensación térmica con temperatura y humedad.")
archivo = st.sidebar.file_uploader("Carga CSV propio (opcional)", type="csv")

try:
    # Usamos CSV del estudiante si existe; si no, usamos datos de demostración.
    origen = pd.read_csv(archivo) if archivo else datos_demo()
    datos = preparar(origen)
except Exception as error:
    st.error(f"No se pudieron preparar los datos: {error}")
    st.stop()

# Calculamos indicadores de faltantes que existían en la fuente antes de interpolar.
st.caption("Datos demostrativos DHT22" if archivo is None else "Datos cargados desde CSV")
st.dataframe(datos.head(), use_container_width=True)

# Marcamos outliers, sin eliminarlos automáticamente.
out_temp, out_hum = outliers_iqr(datos["temperatura"]), outliers_iqr(datos["humedad"])
metrica_1, metrica_2, metrica_3 = st.columns(3)
metrica_1.metric("Lecturas preparadas", len(datos))
metrica_2.metric("Outliers temperatura", int(out_temp.sum()))
metrica_3.metric("Outliers humedad", int(out_hum.sum()))

# Graficamos las dos mediciones pedidas en el taller.
figura, ejes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
ejes[0].plot(datos["fecha"], datos["temperatura"], color="tomato", label="Temperatura")
ejes[0].scatter(datos.loc[out_temp, "fecha"], datos.loc[out_temp, "temperatura"], color="black", s=12, label="Outlier")
ejes[0].set(ylabel="°C", title="Temperatura del sensor")
ejes[0].legend()
ejes[1].plot(datos["fecha"], datos["humedad"], color="steelblue", label="Humedad")
ejes[1].scatter(datos.loc[out_hum, "fecha"], datos.loc[out_hum, "humedad"], color="black", s=12, label="Outlier")
ejes[1].set(xlabel="Tiempo", ylabel="%", title="Humedad del sensor")
ejes[1].legend()
figura.tight_layout()
st.pyplot(figura, clear_figure=True)

# Entrenamos el modelo de regresión múltiple sobre un conjunto de prueba separado.
x, y = datos[["temperatura", "humedad"]], datos["sensacion_termica"]
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.30, random_state=42)
modelo = LinearRegression().fit(x_train, y_train)
predicciones = modelo.predict(x_test)

# Mostramos las métricas en grados Celsius y la capacidad explicativa del modelo.
st.subheader("Modelo predictivo")
metrica_1, metrica_2, metrica_3 = st.columns(3)
metrica_1.metric("MAE", f"{mean_absolute_error(y_test, predicciones):.3f} °C")
metrica_2.metric("RMSE", f"{mean_squared_error(y_test, predicciones) ** .5:.3f} °C")
metrica_3.metric("R²", f"{r2_score(y_test, predicciones):.3f}")
st.write(f"Modelo: sensación = **{modelo.intercept_:.3f}** + **{modelo.coef_[0]:.3f}** × temperatura + **{modelo.coef_[1]:.3f}** × humedad")

# Permitimos predecir una nueva combinación de temperatura y humedad.
columna_1, columna_2 = st.columns(2)
temperatura_nueva = columna_1.number_input("Temperatura nueva (°C)", value=28.5)
humedad_nueva = columna_2.number_input("Humedad nueva (%)", value=56.0)
prediccion_nueva = modelo.predict(pd.DataFrame([[temperatura_nueva, humedad_nueva]], columns=["temperatura", "humedad"]))[0]
st.success(f"Sensación térmica estimada: {prediccion_nueva:.2f} °C")
