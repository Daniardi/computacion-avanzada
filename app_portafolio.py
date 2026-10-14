"""Portafolio de aplicaciones de Computación Avanzada de Daniel Ardila Zabala."""

# Importamos Streamlit para construir la página web del portafolio.
import streamlit as st


# Configuramos los metadatos de la página antes de mostrar componentes.
st.set_page_config(
    page_title="Portafolio | Computación Avanzada",
    page_icon="💻",
    layout="wide",
)

# Aplicamos estilos propios para presentar las actividades como tarjetas visuales.
st.markdown(
    """
    <style>
    .hero {
        padding: 2rem;
        border-radius: 18px;
        color: white;
        background: linear-gradient(120deg, #0d3b66, #1d7874);
        margin-bottom: 1.5rem;
    }
    .card {
        min-height: 205px;
        padding: 1.2rem;
        border: 1px solid #d7e2ea;
        border-radius: 16px;
        background: #ffffff;
        box-shadow: 0 3px 9px rgba(0, 0, 0, 0.07);
        margin-bottom: 1rem;
    }
    .icono {
        font-size: 2.2rem;
        margin-bottom: 0.35rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Mostramos la identificación y el propósito general del portafolio.
st.markdown(
    """
    <div class="hero">
        <h1>Portafolio de Computación Avanzada</h1>
        <h3>Daniel Ardila Zabala</h3>
        <p>Aplicaciones desarrolladas en Streamlit: análisis de datos, modelos predictivos,
        visualización y aprendizaje automático.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Registramos cada actividad, su imagen simbólica, su descripción y su enlace publicado.
actividades = [
    {
        "sesion": "Sesión 2",
        "icono": "🔢",
        "titulo": "Vectores y matrices",
        "descripcion": "Operaciones vectoriales y matriciales aplicadas a problemas computacionales.",
        "url": "https://computacion-avanzada-l9ahst4kvw5u4lnei6nsfh.streamlit.app/",
    },
    {
        "sesion": "Sesión 3",
        "icono": "📉",
        "titulo": "Cálculo aplicado y gradiente",
        "descripcion": "Derivadas, gradiente y descenso de gradiente para optimización.",
        "url": "https://appgradientepy-mqkxu3x4pz7mstnhaqu4up.streamlit.app/",
    },
    {
        "sesion": "Sesión 4",
        "icono": "⚙️",
        "titulo": "Lógica, Big O y vectorización",
        "descripcion": "Comparación de eficiencia y procesamiento vectorizado con NumPy.",
        "url": "https://computacion-avanzada-97vz7zurbwwvng5pu5ddjw.streamlit.app/",
    },
    {
        "sesion": "Sesión 5",
        "icono": "🧹",
        "titulo": "Preparación de datos",
        "descripcion": "Limpieza, transformación y exploración inicial de datos.",
        "url": "https://computacion-avanzada-hxsao8q2olfabiwbnyks8s.streamlit.app/",
    },
    {
        "sesion": "Sesión 6",
        "icono": "🌦️",
        "titulo": "Estación San Rafael",
        "descripcion": "Consulta y análisis de datos meteorológicos de una estación.",
        "url": "https://computacion-avanzada-i58sjeqjsklw8fbgh3gjvm.streamlit.app/",
    },
    {
        "sesion": "Sesión 7",
        "icono": "📊",
        "titulo": "Regresión lineal",
        "descripcion": "Modelo de regresión para comprender relaciones entre variables.",
        "url": "https://computacion-avanzada-3zrgqgqzugw3vq6duf2h94.streamlit.app/",
    },
    {
        "sesion": "Sesión 8",
        "icono": "⏱️",
        "titulo": "Series de tiempo",
        "descripcion": "Análisis, descomposición y pronóstico de datos temporales.",
        "url": "https://computacion-avanzada-4bkt8w52chtrvx4xuhwq38.streamlit.app/",
    },
    {
        "sesion": "Sesión 10",
        "icono": "🌡️",
        "titulo": "IoT y sensación térmica",
        "descripcion": "Pipeline de datos de sensor y predicción de sensación térmica.",
        "url": "https://computacion-avanzada-rmytxzh44p9djh32zmwvdc.streamlit.app/",
    },
    {
        "sesion": "Sesión 11",
        "icono": "🌧️",
        "titulo": "Regresión logística",
        "descripcion": "Clasificación de lluvia, métricas y matriz de confusión.",
        "url": "https://computacion-avanzada-nwjm7j7tqv8kwmxycb2vkc.streamlit.app/",
    },
    {
        "sesion": "Sesión 12",
        "icono": "⚡",
        "titulo": "PCA y consumo energético",
        "descripcion": "Visualización de perfiles de consumo y reducción dimensional con PCA.",
        "url": "https://computacion-avanzada-9m7h6nsurghlbmxcrvpsgi.streamlit.app/",
    },
    {
        "sesion": "Proyecto KNN",
        "icono": "🌱",
        "titulo": "Fertilidad de suelos",
        "descripcion": "Clasificación didáctica de fertilidad baja, media o alta con KNN.",
        "url": "https://computacion-avanzada-npnntycn4htln6e2perksi.streamlit.app/",
    },
]

# Creamos dos columnas para distribuir las tarjetas de forma ordenada.
izquierda, derecha = st.columns(2)
for indice, actividad in enumerate(actividades):
    # Alternamos la columna para equilibrar visualmente la altura del portafolio.
    columna = izquierda if indice % 2 == 0 else derecha
    with columna:
        # Presentamos un icono, el tema y la descripción de la aplicación.
        st.markdown(
            f"""
            <div class="card">
                <div class="icono">{actividad["icono"]}</div>
                <small>{actividad["sesion"]}</small>
                <h3>{actividad["titulo"]}</h3>
                <p>{actividad["descripcion"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Añadimos un botón que abre la aplicación publicada en una nueva pestaña.
        st.link_button(f"Abrir {actividad['sesion']}", actividad["url"], use_container_width=True)

# Cerramos el portafolio con el vínculo del código fuente.
st.divider()
st.caption("Repositorio del proyecto: https://github.com/Daniardi/computacion-avanzada")
