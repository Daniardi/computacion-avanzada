"""App Streamlit de la Sesión 4: lógica, Big-O y vectorización."""

# Importamos NumPy para procesar los datos de sensores de forma vectorizada.
import numpy as np
# Importamos Pandas para mostrar el resultado en tablas fáciles de leer.
import pandas as pd
# Importamos Matplotlib para crear las gráficas de complejidad y rendimiento.
import matplotlib.pyplot as plt
# Importamos time para comparar duración de loop y vectorización.
import time
# Importamos Streamlit para construir la interfaz web interactiva.
import streamlit as st

# Configuramos los metadatos principales de la app.
st.set_page_config(page_title="Sesión 4 | Lógica y vectorización", page_icon="⚡", layout="wide")


def generar_datos(n, semilla=42):
    """Genera lecturas reproducibles de temperatura, humedad y día."""
    # Usamos un generador con semilla para repetir los resultados en cada interacción.
    generador = np.random.default_rng(semilla)
    # Simulamos temperaturas ambientales medidas por sensores.
    temperaturas = generador.uniform(15, 40, n)
    # Simulamos porcentajes de humedad medidos por sensores.
    humedades = generador.uniform(20, 80, n)
    # Simulamos el día de la semana de cada lectura.
    dias = generador.integers(0, 7, n)
    # Marcamos sábado y domingo como fin de semana.
    fines_de_semana = (dias == 5) | (dias == 6)
    # Entregamos los arreglos generados.
    return temperaturas, humedades, fines_de_semana


def alarma_loop(temperaturas, humedades, fines_de_semana, limite_temperatura, limite_humedad):
    """Evalúa la regla P AND Q AND NOT R con un loop de Python."""
    # Creamos la lista que contendrá las decisiones de alarma.
    resultados = []
    # Evaluamos cada lectura individualmente, por lo cual es O(n).
    for temperatura, humedad, fin_de_semana in zip(temperaturas, humedades, fines_de_semana):
        # Agregamos la decisión lógica para la lectura actual.
        resultados.append(temperatura > limite_temperatura and humedad < limite_humedad and not fin_de_semana)
    # Convertimos la lista en arreglo booleano para compararla con NumPy.
    return np.array(resultados)


def alarma_vectorizada(temperaturas, humedades, fines_de_semana, limite_temperatura, limite_humedad):
    """Evalúa la misma regla sobre arreglos NumPy completos."""
    # Comparamos todas las temperaturas al mismo tiempo.
    temperatura_alta = temperaturas > limite_temperatura
    # Comparamos todas las humedades al mismo tiempo.
    humedad_baja = humedades < limite_humedad
    # Invertimos la condición de fin de semana para obtener días laborales.
    dia_laboral = ~fines_de_semana
    # Combinamos las tres condiciones elemento a elemento.
    return temperatura_alta & humedad_baja & dia_laboral


# Escribimos el título y objetivo académico de la actividad.
st.title("⚡ Sesión 4 — Lógica, Big-O y vectorización")
st.write("La misma regla lógica puede procesarse con un loop o con NumPy: ambas son O(n), pero NumPy reduce el costo práctico.")

# Permitimos seleccionar cuántas lecturas se desean procesar sin saturar la app.
cantidad = st.sidebar.slider("Número de lecturas de sensores", 1_000, 500_000, 50_000, step=1_000)
# Permitimos explorar cómo cambian los umbrales de la regla de negocio.
umbral_temperatura = st.sidebar.slider("Temperatura mínima (°C)", 20.0, 38.0, 30.0, 0.5)
umbral_humedad = st.sidebar.slider("Humedad máxima (%)", 20.0, 70.0, 40.0, 1.0)

# Generamos datos para la demostración actual.
temperaturas, humedades, fines_de_semana = generar_datos(cantidad)
# Ajustamos los datos booleanos con los umbrales elegidos en la interfaz.
temperatura_alta = temperaturas > umbral_temperatura
humedad_baja = humedades < umbral_humedad

# Medimos la lógica con loop usando los tres criterios del reto.
inicio_loop = time.perf_counter()
resultado_loop = alarma_loop(temperaturas, humedades, fines_de_semana, umbral_temperatura, umbral_humedad)
tiempo_loop = time.perf_counter() - inicio_loop
# Medimos la lógica vectorizada equivalente.
inicio_vectorizado = time.perf_counter()
resultado_vectorizado = alarma_vectorizada(temperaturas, humedades, fines_de_semana, umbral_temperatura, umbral_humedad)
tiempo_vectorizado = time.perf_counter() - inicio_vectorizado

# Conservamos el resultado vectorizado para mostrar las alarmas con los umbrales elegidos.
resultado_personalizado = resultado_vectorizado
# Calculamos el factor de aceleración y evitamos dividir entre cero.
aceleracion = tiempo_loop / tiempo_vectorizado if tiempo_vectorizado > 0 else float("inf")

# Presentamos las métricas de la comparación de rendimiento.
columna_1, columna_2, columna_3, columna_4 = st.columns(4)
columna_1.metric("Lecturas", f"{cantidad:,}")
columna_2.metric("Alarmas activadas", f"{resultado_personalizado.sum():,}")
columna_3.metric("Tiempo loop", f"{tiempo_loop:.5f} s")
columna_4.metric("Aceleración NumPy", f"{aceleracion:.1f}×")

# Confirmamos que ambas estrategias producen las mismas decisiones con la regla base.
if np.array_equal(resultado_loop, resultado_vectorizado):
    st.success("El loop y NumPy producen las mismas decisiones. Añadir NOT fin de semana no cambia Big-O: sigue siendo O(n).")

# Mostramos un fragmento de los datos para conectar la regla con casos concretos.
st.subheader("Regla lógica aplicada")
st.code("Activar alarma = (temperatura > umbral) AND (humedad < umbral) AND NOT(es_fin_de_semana)")
# Creamos una tabla con las primeras diez lecturas procesadas.
tabla = pd.DataFrame({
    "Temperatura °C": np.round(temperaturas[:10], 2),
    "Humedad %": np.round(humedades[:10], 2),
    "Fin de semana": fines_de_semana[:10],
    "Alarma": resultado_personalizado[:10],
})
# Renderizamos la tabla dentro de la aplicación.
st.dataframe(tabla, use_container_width=True)

# Construimos una gráfica para explicar el crecimiento de Big-O.
st.subheader("Complejidad Big-O")
n = np.arange(1, 51)
figura, eje = plt.subplots(figsize=(9, 4))
# Dibujamos los cuatro patrones de crecimiento explicados en el cuaderno.
eje.plot(n, np.ones_like(n), label="O(1)")
eje.plot(n, n, label="O(n)")
eje.plot(n, n * np.log2(n), label="O(n log n)")
eje.plot(n, n**2, label="O(n²)")
# Añadimos etiquetas, cuadrícula y leyenda a la gráfica.
eje.set(xlabel="Tamaño de entrada (n)", ylabel="Operaciones teóricas", title="Cómo crece el costo computacional")
eje.grid(alpha=0.3)
eje.legend()
# Mostramos la gráfica en Streamlit.
st.pyplot(figura, clear_figure=True)

# Mostramos una comparación directa de los tiempos medidos en esta ejecución.
st.subheader("Rendimiento real: loop vs. vectorización")
figura_tiempo, eje_tiempo = plt.subplots(figsize=(6, 4))
# Dibujamos una barra para cada estrategia de procesamiento.
eje_tiempo.bar(["Loop Python", "NumPy vectorizado"], [tiempo_loop, tiempo_vectorizado], color=["crimson", "seagreen"])
# Etiquetamos la gráfica de tiempos.
eje_tiempo.set(ylabel="Segundos", title="Misma complejidad O(n), distinta constante de tiempo")
eje_tiempo.grid(axis="y", alpha=0.3)
# Enviamos la comparación a la interfaz.
st.pyplot(figura_tiempo, clear_figure=True)
