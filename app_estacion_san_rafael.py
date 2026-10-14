"""App Streamlit — Sesión 6: calidad de datos de la estación San Rafael."""

# Importamos requests para descargar los datos reales de la API MARCO-CORNARE.
import requests
# Importamos NumPy y Pandas para cálculos y estructura temporal.
import numpy as np
import pandas as pd
# Importamos Matplotlib para las gráficas de nivel y distribución.
import matplotlib.pyplot as plt
# Importamos Streamlit para construir la aplicación interactiva.
import streamlit as st
# Desactivamos advertencias de certificado de la API institucional.
import urllib3

# Ocultamos las advertencias porque la consulta se realiza a un endpoint HTTPS conocido.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Configuramos metadatos de la aplicación.
st.set_page_config(page_title="Sesión 6 | Estación San Rafael", page_icon="🌊", layout="wide")

# Definimos la personalización solicitada para la estación del estudiante.
ESTUDIANTE = "Daniel Ardila Zabala"
CODIGO_ESTACION = "9"
NOMBRE_ESTACION = "San Rafael (Aguas)"
UBICACION = "San Rafael, Antioquia"
API_BASE = "https://marco.cornare.gov.co/api/v1/estaciones"


@st.cache_data(ttl=3600, show_spinner=False)
def descargar_serie(desde, hasta):
    """Descarga y acumula todas las páginas de nivel de la estación elegida."""
    # Construimos URL y parámetros del endpoint de nivel.
    url = f"{API_BASE}/{CODIGO_ESTACION}/nivel"
    parametros = {"desde": desde, "hasta": hasta, "calidad": 1}
    # Consultamos la primera página de la API con verificación SSL desactivada.
    respuesta = requests.get(url, params=parametros, timeout=40, verify=False)
    respuesta.raise_for_status()
    # Guardamos los registros de la respuesta inicial.
    pagina = respuesta.json()
    registros = list(pagina.get("values", []))
    # Seguimos enlaces next cuando el servidor pagina una consulta extensa.
    while pagina.get("next"):
        respuesta = requests.get(pagina["next"], timeout=40, verify=False)
        respuesta.raise_for_status()
        pagina = respuesta.json()
        registros.extend(pagina.get("values", []))
    # Convertimos el resultado a DataFrame y tipamos las variables centrales.
    datos = pd.DataFrame(registros)
    if datos.empty:
        return datos
    datos["fecha"] = pd.to_datetime(datos["fecha"], errors="coerce", utc=True)
    datos["nivel"] = pd.to_numeric(datos["nivel"], errors="coerce")
    # Ordenamos la serie y descartamos fechas inválidas o repetidas.
    return datos.dropna(subset=["fecha"]).sort_values("fecha").drop_duplicates("fecha").reset_index(drop=True)


def regularizar_serie(datos):
    """Expone huecos temporales y los interpola respetando la fecha real."""
    # Calculamos la frecuencia de reporte más común de la estación.
    frecuencia = datos["fecha"].diff().dropna().mode().iloc[0]
    # Construimos un índice completo entre primera y última lectura.
    rango = pd.date_range(datos["fecha"].min(), datos["fecha"].max(), freq=frecuencia)
    # Reindexamos para convertir huecos de tiempo en valores NaN explícitos.
    regular = datos.set_index("fecha").reindex(rango)
    # Medimos la completitud antes de llenar los huecos.
    huecos = int(regular["nivel"].isna().sum())
    # Interpolamos por tiempo para aprovechar la distancia real entre fechas.
    regular["nivel"] = regular["nivel"].interpolate(method="time").ffill().bfill()
    # Recuperamos fecha como columna para las visualizaciones.
    return regular.reset_index().rename(columns={"index": "fecha"}), frecuencia, huecos


def mascara_iqr(serie, multiplicador):
    """Marca outliers estadísticos y niveles físicamente negativos."""
    # Calculamos cuartiles, IQR y límites estadísticos.
    q1, q3 = serie.quantile(0.25), serie.quantile(0.75)
    iqr = q3 - q1
    limite_inferior, limite_superior = q1 - multiplicador * iqr, q3 + multiplicador * iqr
    # Unimos anomalías IQR y la restricción física de nivel no negativo.
    mascara = (serie < limite_inferior) | (serie > limite_superior) | (serie < 0)
    return mascara, limite_inferior, limite_superior


# Mostramos la identidad personalizada de la app.
st.title("🌊 Sesión 6 — Calidad de datos hidrológicos")
st.caption(f"Estudiante: {ESTUDIANTE} | Estación {CODIGO_ESTACION}: {NOMBRE_ESTACION} | {UBICACION}")

# Permitimos modificar el rango sin cambiar la personalización de la estación.
columna_fecha_1, columna_fecha_2 = st.columns(2)
fecha_desde = columna_fecha_1.date_input("Fecha inicial", value=pd.Timestamp("2026-09-01")).isoformat()
fecha_hasta = columna_fecha_2.date_input("Fecha final", value=pd.Timestamp("2026-09-05")).isoformat()
mult_iqr = st.sidebar.slider("Multiplicador IQR", 0.5, 3.0, 1.5, 0.1)

try:
    # Descargamos la serie real solicitada por el estudiante.
    datos_crudos = descargar_serie(fecha_desde, fecha_hasta)
    # Informamos si la API no devolvió observaciones para ese rango.
    if datos_crudos.empty:
        st.warning("No se encontraron registros en ese periodo. Ajusta las fechas e inténtalo de nuevo.")
        st.stop()
    # Regularizamos la frecuencia y detectamos anomalías.
    datos_limpios, frecuencia, huecos = regularizar_serie(datos_crudos)
    outliers, limite_inf, limite_sup = mascara_iqr(datos_limpios["nivel"], mult_iqr)
except requests.RequestException as error:
    # Mostramos un mensaje comprensible si la API no está disponible.
    st.error(f"No fue posible consultar MARCO-CORNARE: {error}")
    st.stop()

# Calculamos indicadores de calidad usados en el ICD.
completitud = 100 * (1 - huecos / len(datos_limpios))
validez = 100 * (1 - outliers.mean())
icd = (completitud + validez) / 2

# Resumimos la consulta y calidad en tarjetas visibles.
metrica_1, metrica_2, metrica_3, metrica_4 = st.columns(4)
metrica_1.metric("Lecturas recibidas", f"{len(datos_crudos):,}")
metrica_2.metric("Huecos temporales", f"{huecos:,}")
metrica_3.metric("Outliers IQR", f"{int(outliers.sum()):,}")
metrica_4.metric("ICD", f"{icd:.1f} / 100")
st.info(f"Frecuencia típica: {frecuencia}. ICD = promedio de completitud ({completitud:.1f} %) y validez ({validez:.1f} %).")

# Dibujamos la serie real e identificamos visualmente los valores inusuales.
figura, ejes = plt.subplots(2, 1, figsize=(12, 7), height_ratios=[2, 1])
ejes[0].plot(datos_limpios["fecha"], datos_limpios["nivel"], color="steelblue", linewidth=0.8, label="Nivel")
ejes[0].scatter(datos_limpios.loc[outliers, "fecha"], datos_limpios.loc[outliers, "nivel"], color="crimson", s=14, label="Outlier")
ejes[0].axhline(limite_inf, color="darkorange", linestyle="--", linewidth=1, label="Límites IQR")
ejes[0].axhline(limite_sup, color="darkorange", linestyle="--", linewidth=1)
ejes[0].set(title="Nivel de agua — estación San Rafael", ylabel="Nivel")
ejes[0].legend(ncol=3)
# Mostramos la distribución para complementar la lectura de outliers.
ejes[1].hist(datos_limpios["nivel"], bins=35, color="seagreen", alpha=0.8)
ejes[1].set(title="Distribución del nivel", xlabel="Nivel", ylabel="Frecuencia")
figura.tight_layout()
st.pyplot(figura, clear_figure=True)

# Construimos el split cronológico solicitado por la actividad.
sin_outliers = datos_limpios.loc[~outliers].reset_index(drop=True)
corte_train, corte_val = int(len(sin_outliers) * 0.70), int(len(sin_outliers) * 0.85)
train, validacion, test = sin_outliers.iloc[:corte_train], sin_outliers.iloc[corte_train:corte_val], sin_outliers.iloc[corte_val:]
st.subheader("Split cronológico Train / Validation / Test")
st.dataframe(pd.DataFrame({
    "Conjunto": ["Train", "Validation", "Test"],
    "Registros": [len(train), len(validacion), len(test)],
    "Desde": [train.fecha.min(), validacion.fecha.min(), test.fecha.min()],
    "Hasta": [train.fecha.max(), validacion.fecha.max(), test.fecha.max()],
}), use_container_width=True)

# Presentamos estadísticas y el evento máximo solicitado por el cuaderno.
indice_maximo = datos_crudos["nivel"].idxmax()
evento_maximo = datos_crudos.loc[indice_maximo]
st.subheader("Resumen estadístico")
st.dataframe(datos_crudos["nivel"].agg(["mean", "var", "std", "min", "max"]).round(3).to_frame("nivel"), use_container_width=True)
st.success(f"Máximo observado: {evento_maximo['nivel']:.2f} el {evento_maximo['fecha']}.")
