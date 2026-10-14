"""App Streamlit de la Sesión 8: análisis y pronóstico de series de tiempo."""

# Importamos librerías para datos, gráficos y modelos de pronóstico.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA

# Configuramos la interfaz de Streamlit.
st.set_page_config(page_title="Sesión 8 | Series de tiempo", page_icon="⏱️", layout="wide")


@st.cache_data
def crear_sensor(dias=45):
    """Genera datos horarios reproducibles de temperatura y humedad."""
    # Definimos cantidad de lecturas, fechas y generador aleatorio.
    n, t, generador = dias * 24, np.arange(dias * 24), np.random.default_rng(42)
    fechas = pd.date_range("2025-01-01", periods=n, freq="h")
    # Integramos tendencia, estacionalidad diaria y ruido realista.
    temperatura = 22 + 0.01 * t + 4 * np.sin(2 * np.pi * t / 24 - np.pi / 2) + generador.normal(0, 0.6, n)
    humedad = np.clip(60 - 0.005 * t - 10 * np.sin(2 * np.pi * t / 24 - np.pi / 2) + generador.normal(0, 2, n), 20, 95)
    # Devolvemos el DataFrame indexado por fecha.
    return pd.DataFrame({"temperatura": temperatura, "humedad": humedad}, index=fechas)


def media_movil(train, pasos, ventana):
    """Calcula pronóstico recursivo usando el promedio de los últimos valores."""
    # Iniciamos historial y lista de predicciones futuras.
    historial, resultado = list(train), []
    # Agregamos cada pronóstico al historial para el siguiente paso.
    for _ in range(pasos):
        valor = np.mean(historial[-ventana:])
        resultado.append(valor)
        historial.append(valor)
    return np.array(resultado)


def evaluar(real, prediccion, nombre):
    """Devuelve métricas MAE y RMSE para un modelo."""
    # Calculamos ambos errores en las unidades de la variable original.
    return {"Modelo": nombre, "MAE": mean_absolute_error(real, prediccion), "RMSE": mean_squared_error(real, prediccion) ** 0.5}


# Escribimos el título y seleccionamos controles de la serie.
st.title("⏱️ Sesión 8 — Series de Tiempo")
st.write("Analiza tendencia, estacionalidad y pronósticos de un sensor ambiental horario.")
variable = st.sidebar.selectbox("Variable", ["temperatura", "humedad"])
ventana = st.sidebar.slider("Ventana de media móvil (horas)", 3, 72, 24)
horizonte = st.sidebar.slider("Horizonte de prueba (horas)", 24, 168, 120, 24)
modelo_seleccionado = st.sidebar.selectbox("Modelo destacado", ["Media móvil", "Holt-Winters", "ARIMA"])

# Cargamos serie y separamos entrenamiento del periodo final de prueba.
datos = crear_sensor()
serie = datos[variable]
train, test = serie.iloc[:-horizonte], serie.iloc[-horizonte:]

# Entrenamos los tres métodos clásicos vistos en el cuaderno.
pred_mm = media_movil(train, len(test), ventana)
pred_hw = ExponentialSmoothing(train, trend="add", seasonal="add", seasonal_periods=24).fit().forecast(len(test))
pred_arima = ARIMA(train, order=(4, 1, 2)).fit().forecast(len(test))
predicciones = {"Media móvil": pred_mm, "Holt-Winters": pred_hw, "ARIMA": pred_arima}

# Construimos tabla de evaluación con el mismo test cronológico.
resultados = pd.DataFrame([
    evaluar(test, pred_mm, "Media móvil"),
    evaluar(test, pred_hw, "Holt-Winters"),
    evaluar(test, pred_arima, "ARIMA(4,1,2)"),
]).sort_values("RMSE")
mejor = resultados.iloc[0]
columna_1, columna_2, columna_3 = st.columns(3)
columna_1.metric("Mejor modelo por RMSE", mejor["Modelo"])
columna_2.metric("MAE del mejor modelo", f"{mejor['MAE']:.3f}")
columna_3.metric("RMSE del mejor modelo", f"{mejor['RMSE']:.3f}")

# Graficamos la serie completa para observar tendencia y ciclo diario.
figura, ejes = plt.subplots(2, 1, figsize=(12, 7))
ejes[0].plot(serie.index, serie.values, color="steelblue")
ejes[0].set(title=f"Serie completa: {variable}", ylabel=variable)
# Comparamos valores reales y los tres pronósticos sobre el mismo horizonte.
ejes[1].plot(test.index, test.values, color="black", linewidth=2, label="Real")
for nombre, prediccion in predicciones.items():
    estilo = "-" if nombre == modelo_seleccionado else "--"
    ejes[1].plot(test.index, prediccion, linestyle=estilo, label=nombre)
ejes[1].set(title="Pronóstico y evaluación cronológica", xlabel="Fecha", ylabel=variable)
ejes[1].legend(ncol=2)
figura.tight_layout()
st.pyplot(figura, clear_figure=True)

# Presentamos las métricas de todos los modelos.
st.subheader("Comparación de modelos")
st.dataframe(resultados.round(3), use_container_width=True)
st.info("Holt-Winters suele capturar mejor el ciclo diario porque modela explícitamente tendencia y estacionalidad de 24 horas.")

# Construimos una demostración visible de ventanas deslizantes.
st.subheader("Ventanas deslizantes")
ventana_muestra = serie.iloc[:ventana].round(2).to_list()
st.code(f"Últimas {ventana} lecturas: {ventana_muestra}\n→ siguiente lectura: {serie.iloc[ventana]:.2f}")
st.caption("Cada ventana se puede usar como fila de entrada para regresión, RNN o LSTM.")
