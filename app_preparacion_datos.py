"""App Streamlit de la Sesión 5: preparación de datos de sensores IoT."""

# Importamos NumPy para generación de datos y escalamiento numérico.
import numpy as np
# Importamos Pandas para manipular tablas y categorías.
import pandas as pd
# Importamos Matplotlib para histogramas, boxplots y mapas de calor.
import matplotlib.pyplot as plt
# Importamos Streamlit para construir las cinco páginas interactivas.
import streamlit as st

# Configuramos la app para un diseño amplio y un título descriptivo.
st.set_page_config(page_title="Sesión 5 | Preparación de datos", page_icon="🧹", layout="wide")


@st.cache_data
def crear_dataset(n=500):
    """Genera el dataset de sensores usado en todas las páginas de la app."""
    # Creamos un generador determinista para repetir resultados al recargar.
    generador = np.random.default_rng(42)
    # Generamos 500 registros cronológicos separados por treinta minutos.
    datos = pd.DataFrame({
        "timestamp": pd.date_range("2026-01-01", periods=n, freq="30min"),
        "tipo_sensor": generador.choice(["DHT22", "BMP180", "LDR"], n, p=[0.5, 0.3, 0.2]),
        "ubicacion": generador.choice(["invernadero_1", "patio", "bodega"], n),
        "calidad_senal": generador.choice(["baja", "media", "alta"], n, p=[0.1, 0.3, 0.6]),
        "temperatura": generador.normal(24, 3, n),
        "humedad": generador.normal(60, 10, n),
        "presion": generador.normal(1013, 5, n),
        "lecturas_hora": generador.poisson(12, n),
    })
    # Insertamos faltantes y outliers para que puedan analizarse en la app.
    datos.loc[generador.choice(datos.index, 25, replace=False), "temperatura"] = np.nan
    datos.loc[generador.choice(datos.index, 20, replace=False), "humedad"] = np.nan
    datos.loc[generador.choice(datos.index, 6, replace=False), "temperatura"] = generador.choice([-40, 95, 120], 6)
    # Retornamos la tabla sintética de sensores.
    return datos


def limpiar_datos(datos):
    """Ordena por tiempo e interpola los valores faltantes numéricos."""
    # Copiamos y ordenamos para respetar la secuencia temporal.
    resultado = datos.sort_values("timestamp").reset_index(drop=True).copy()
    # Estimamos lecturas perdidas entre dos momentos conocidos.
    resultado[["temperatura", "humedad"]] = resultado[["temperatura", "humedad"]].interpolate()
    # Retornamos el dataset sin faltantes en estas variables.
    return resultado


def outliers_iqr(serie, multiplicador):
    """Calcula una máscara de outliers y sus límites IQR."""
    # Tomamos los percentiles que delimitan el rango central.
    q1, q3 = serie.quantile(0.25), serie.quantile(0.75)
    # Calculamos el rango intercuartílico.
    iqr = q3 - q1
    # Construimos el intervalo aceptado por el multiplicador seleccionado.
    inferior, superior = q1 - multiplicador * iqr, q3 + multiplicador * iqr
    # Devolvemos valores que caen fuera de ese intervalo.
    return (serie < inferior) | (serie > superior), inferior, superior


# Cargamos el dataset una sola vez para todas las páginas de la aplicación.
datos_crudos = crear_dataset()
# Mostramos encabezado y navegación de la actividad.
st.title("🧹 Sesión 5 — Preparación de datos")
st.write("Explora tipos de datos, calidad, escalamiento, particiones y estadística con sensores IoT.")
pagina = st.sidebar.radio("Página", ["1. Tipos de datos", "2. Missing values y outliers", "3. Escalamiento", "4. Train / Val / Test", "5. Estadística"])

if pagina == "1. Tipos de datos":
    # Permitimos comparar el uso de memoria antes y después de convertir categorías.
    usar_categoria = st.toggle("Convertir texto repetitivo a category", value=True)
    # Copiamos los datos para no alterar las otras páginas.
    datos = datos_crudos.copy()
    # Aplicamos categorías solo cuando la opción está activada.
    if usar_categoria:
        datos["tipo_sensor"] = datos["tipo_sensor"].astype("category")
        datos["ubicacion"] = datos["ubicacion"].astype("category")
        datos["calidad_senal"] = pd.Categorical(datos["calidad_senal"], ["baja", "media", "alta"], ordered=True)
    # Sumamos la memoria que consume cada columna del DataFrame.
    memoria = datos.memory_usage(deep=True).sum() / 1024
    # Mostramos memoria y tipos detectados por Pandas.
    st.metric("Memoria del DataFrame", f"{memoria:.2f} KB")
    st.dataframe(pd.DataFrame({"columna": datos.dtypes.index, "tipo": datos.dtypes.astype(str).values}), use_container_width=True)
    st.info("`category` almacena códigos y una tabla pequeña de valores únicos, por eso ahorra memoria cuando el texto se repite.")

elif pagina == "2. Missing values y outliers":
    # Permitimos ajustar cuán estricto es el detector IQR.
    multiplicador = st.slider("Multiplicador IQR", 0.5, 3.0, 1.5, 0.1)
    # Limpiamos faltantes antes de detectar los valores extremos.
    datos = limpiar_datos(datos_crudos)
    # Calculamos los outliers de temperatura con el parámetro elegido.
    mascara, inferior, superior = outliers_iqr(datos["temperatura"], multiplicador)
    # Mostramos conteos de faltantes originales y outliers detectados.
    columna_1, columna_2, columna_3 = st.columns(3)
    columna_1.metric("Faltantes iniciales", int(datos_crudos[["temperatura", "humedad"]].isna().sum().sum()))
    columna_2.metric("Outliers detectados", int(mascara.sum()))
    columna_3.metric("Rango IQR", f"{inferior:.1f} a {superior:.1f} °C")
    # Dibujamos el boxplot de temperatura y marcamos los límites IQR.
    figura, eje = plt.subplots(figsize=(8, 3))
    eje.boxplot(datos["temperatura"].dropna(), vert=False)
    eje.axvline(inferior, color="crimson", linestyle="--", label="Límite IQR")
    eje.axvline(superior, color="crimson", linestyle="--")
    eje.set(title="Temperatura y outliers detectados", xlabel="°C")
    eje.legend()
    st.pyplot(figura, clear_figure=True)
    st.warning("IQR identifica valores estadísticamente inusuales; no determina por sí solo si provienen de un error o de un evento real.")

elif pagina == "3. Escalamiento":
    # Limpiamos, quitamos outliers y seleccionamos las variables numéricas.
    datos = limpiar_datos(datos_crudos)
    mascara, _, _ = outliers_iqr(datos["temperatura"], 1.5)
    columnas = ["temperatura", "humedad", "presion", "lecturas_hora"]
    matriz = datos.loc[~mascara, columnas].to_numpy()
    # Calculamos Min-Max y Z-score por columnas.
    normalizado = (matriz - matriz.min(axis=0)) / (matriz.max(axis=0) - matriz.min(axis=0))
    estandarizado = (matriz - matriz.mean(axis=0)) / matriz.std(axis=0)
    # Elegimos una variable para comparar las tres escalas.
    variable = st.selectbox("Variable", columnas, index=2)
    indice = columnas.index(variable)
    # Construimos tres histogramas para mostrar que la forma se conserva.
    figura, ejes = plt.subplots(1, 3, figsize=(13, 3.5))
    for eje, valores, titulo, color in zip(ejes, [matriz[:, indice], normalizado[:, indice], estandarizado[:, indice]], ["Original", "Min-Max [0,1]", "Z-score"], ["steelblue", "seagreen", "indianred"]):
        eje.hist(valores, bins=25, color=color)
        eje.set_title(titulo)
    st.pyplot(figura, clear_figure=True)
    st.info("Estas transformaciones solucionan diferencias de escala para algoritmos sensibles a distancias o gradientes; no eliminan asimetría ni outliers.")

elif pagina == "4. Train / Val / Test":
    # Permitimos cambiar la estrategia de separación de la serie de tiempo.
    estrategia = st.radio("Estrategia", ["Cronológica (recomendada)", "Aleatoria"])
    # Limpiamos y quitamos outliers para preparar datos de modelado.
    datos = limpiar_datos(datos_crudos)
    mascara, _, _ = outliers_iqr(datos["temperatura"], 1.5)
    datos = datos.loc[~mascara].reset_index(drop=True)
    # Usamos 70 %, 15 % y 15 % como proporciones de train, validation y test.
    if estrategia == "Cronológica (recomendada)":
        corte_train, corte_val = int(len(datos) * 0.70), int(len(datos) * 0.85)
        train, validacion, test = datos.iloc[:corte_train], datos.iloc[corte_train:corte_val], datos.iloc[corte_val:]
    else:
        # Barajamos índices para simular un split aleatorio de idéntico tamaño.
        indices = np.random.default_rng(42).permutation(len(datos))
        corte_train, corte_val = int(len(datos) * 0.70), int(len(datos) * 0.85)
        train, validacion, test = datos.iloc[indices[:corte_train]], datos.iloc[indices[corte_train:corte_val]], datos.iloc[indices[corte_val:]]
    # Mostramos tamaños y rango temporal del train y test.
    st.write(f"Train: **{len(train)}** | Validation: **{len(validacion)}** | Test: **{len(test)}**")
    st.dataframe(pd.DataFrame({"Conjunto": ["Train", "Validation", "Test"], "Inicio": [train.timestamp.min(), validacion.timestamp.min(), test.timestamp.min()], "Fin": [train.timestamp.max(), validacion.timestamp.max(), test.timestamp.max()]}), use_container_width=True)
    st.warning("En una serie temporal, el split aleatorio puede filtrar patrones futuros hacia el entrenamiento. El test debe quedar al final del tiempo.")

else:
    # Preparamos una versión limpia para los cálculos estadísticos.
    datos = limpiar_datos(datos_crudos)
    mascara, _, _ = outliers_iqr(datos["temperatura"], 1.5)
    columnas = ["temperatura", "humedad", "presion", "lecturas_hora"]
    datos = datos.loc[~mascara, columnas]
    # Mostramos media, varianza y desviación estándar de cada variable.
    resumen = datos.agg(["mean", "var", "std"]).T.round(3)
    st.dataframe(resumen, use_container_width=True)
    # Permitimos cambiar entre covarianza y correlación.
    tipo_matriz = st.radio("Matriz", ["Correlación", "Covarianza"], horizontal=True)
    matriz = datos.corr() if tipo_matriz == "Correlación" else datos.cov()
    # Dibujamos el mapa de calor de la matriz elegida.
    figura, eje = plt.subplots(figsize=(7, 5))
    imagen = eje.imshow(matriz, cmap="coolwarm", vmin=-1 if tipo_matriz == "Correlación" else None, vmax=1 if tipo_matriz == "Correlación" else None)
    eje.set_xticks(range(len(columnas)), columnas, rotation=35, ha="right")
    eje.set_yticks(range(len(columnas)), columnas)
    for fila in range(len(columnas)):
        for columna in range(len(columnas)):
            eje.text(columna, fila, f"{matriz.iloc[fila, columna]:.2f}", ha="center", va="center")
    figura.colorbar(imagen, ax=eje)
    st.pyplot(figura, clear_figure=True)
    st.info("Una correlación cercana a 0 descarta relación lineal fuerte, pero puede existir una relación no lineal, por ejemplo cuadrática o circular.")
