"""Aplicación Streamlit de la sesión 16: eficiencia y paralelismo en Python."""

# Importamos módulos para tiempos, hilos, gráficos y cálculos vectorizados.
import math
import os
import time
from concurrent.futures import ThreadPoolExecutor

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


def esperar_sensor(id_sensor, demora):
    """Simula una lectura que pasa casi todo su tiempo esperando una respuesta."""
    # Pausamos el worker para representar comunicación de red o de un sensor.
    time.sleep(demora)
    # Devolvemos el identificador cuando termina la espera.
    return id_sensor


def medir_hilos(cantidad_tareas, workers, demora):
    """Mide el tiempo de atender sensores con el número elegido de hilos."""
    # Creamos una lista de tareas independientes, una por sensor.
    sensores = list(range(1, cantidad_tareas + 1))
    # Tomamos el tiempo inmediatamente antes de repartir las tareas.
    inicio = time.perf_counter()
    # Usamos como máximo tantos workers como tareas disponibles.
    with ThreadPoolExecutor(max_workers=min(workers, cantidad_tareas)) as executor:
        list(executor.map(lambda sensor: esperar_sensor(sensor, demora), sensores))
    # Calculamos el tiempo transcurrido desde el inicio hasta que todos terminan.
    return time.perf_counter() - inicio


def amdahl(fraccion_paralelizable, workers):
    """Devuelve el speedup de la ley de Amdahl para una fracción y workers dados."""
    # La expresión conserva la parte serial y divide la paralelizable entre workers.
    return 1 / ((1 - fraccion_paralelizable) + fraccion_paralelizable / workers)


# Configuramos la página antes de crear elementos visibles.
st.set_page_config(page_title="Sesión 16 | Procesamiento paralelo", page_icon="⚡", layout="wide")
# Presentamos el objetivo central de la guía.
st.title("Introducción al procesamiento en paralelo")
st.write("Compara hilos, vectorización y la ley de Amdahl para decidir cómo mejorar el rendimiento de un programa.")
st.caption(f"Núcleos detectados en el servidor: {os.cpu_count() or 1}.")

# Organizamos los experimentos de la guía en pestañas separadas.
pestana_hilos, pestana_vectorizacion, pestana_amdahl, pestana_reflexion = st.tabs(
    ["Hilos y sensores", "Vectorización", "Ley de Amdahl", "Conclusiones"]
)

with pestana_hilos:
    # Permitimos variar número de tareas y workers para una operación de entrada/salida.
    columna_tareas, columna_workers = st.columns(2)
    tareas = columna_tareas.slider("Sensores a leer", 2, 12, 8)
    workers = columna_workers.slider("Workers de tipo hilo", 1, 12, 8)
    # Elegimos una espera corta para que el experimento sea visible y no ralentice la app.
    demora = 0.08
    # Medimos primero el caso serial y después la lectura concurrente.
    tiempo_serial = medir_hilos(tareas, 1, demora)
    tiempo_hilos = medir_hilos(tareas, workers, demora)
    # Mostramos los resultados y la ganancia observada en tiempo real.
    metrica_1, metrica_2, metrica_3 = st.columns(3)
    metrica_1.metric("Lectura serial", f"{tiempo_serial:.2f} s")
    metrica_2.metric("Con hilos", f"{tiempo_hilos:.2f} s")
    metrica_3.metric("Speedup medido", f"{tiempo_serial / tiempo_hilos:.2f}x")
    # Calculamos un tiempo ideal aproximado considerando tandas de tareas por worker.
    tandas = math.ceil(tareas / min(tareas, workers))
    st.info(f"Con {workers} workers, los {tareas} sensores se atienden aproximadamente en {tandas} tanda(s). Los hilos son adecuados porque las tareas esperan respuesta.")

with pestana_vectorizacion:
    # Permitimos elegir la cantidad de lecturas para comparar ciclo y operación vectorizada.
    cantidad = st.slider("Cantidad de lecturas de temperatura", 10_000, 500_000, 100_000, 10_000)
    # Construimos el mismo conjunto de temperaturas para ambos métodos.
    celsius = np.linspace(18, 30, cantidad)
    # Medimos la conversión de grados usando un ciclo que procesa un valor a la vez.
    inicio = time.perf_counter()
    fahrenheit_ciclo = [valor * 9 / 5 + 32 for valor in celsius]
    tiempo_ciclo = time.perf_counter() - inicio
    # Medimos la misma operación sobre todo el arreglo de NumPy.
    inicio = time.perf_counter()
    fahrenheit_numpy = celsius * 9 / 5 + 32
    tiempo_numpy = time.perf_counter() - inicio
    # Mostramos el resultado y verificamos que ambos métodos son equivalentes.
    metrica_1, metrica_2, metrica_3 = st.columns(3)
    metrica_1.metric("Ciclo Python", f"{tiempo_ciclo:.4f} s")
    metrica_2.metric("NumPy vectorizado", f"{tiempo_numpy:.4f} s")
    metrica_3.metric("Aceleración", f"{tiempo_ciclo / max(tiempo_numpy, 1e-9):.1f}x")
    st.success(f"Resultados equivalentes: {np.allclose(fahrenheit_ciclo, fahrenheit_numpy)}. Antes de paralelizar, conviene vectorizar cuando la operación lo permita.")

with pestana_amdahl:
    # Dejamos que el usuario modifique la proporción de programa que sí se puede paralelizar.
    fraccion = st.slider("Fracción paralelizable (p)", 0.0, 0.99, 0.80, 0.01)
    workers = st.slider("Número de workers (N)", 1, 64, 8)
    # Calculamos el speedup actual y el límite teórico con infinitos workers.
    speedup = amdahl(fraccion, workers)
    maximo = 1 / (1 - fraccion) if fraccion < 1 else float("inf")
    metrica_1, metrica_2 = st.columns(2)
    metrica_1.metric("Speedup con N workers", f"{speedup:.2f}x")
    metrica_2.metric("Speedup máximo teórico", f"{maximo:.2f}x")
    # Graficamos cómo se aplana la curva al añadir workers.
    rango_workers = np.arange(1, 65)
    figura, eje = plt.subplots(figsize=(9, 4))
    eje.plot(rango_workers, [amdahl(fraccion, n) for n in rango_workers], color="tab:blue", linewidth=2)
    eje.scatter([workers], [speedup], color="tab:red", zorder=3, label="Configuración elegida")
    eje.set_xlabel("Número de workers")
    eje.set_ylabel("Speedup")
    eje.set_title("Ley de Amdahl: más workers no eliminan la parte serial")
    eje.legend()
    eje.grid(alpha=0.3)
    st.pyplot(figura)

with pestana_reflexion:
    # Resumimos las decisiones de rendimiento que busca reforzar la actividad.
    st.markdown(
        """
        - Los hilos son útiles cuando el programa espera red, disco o sensores.
        - Los procesos son preferibles para cálculos intensivos de CPU, porque sortean la limitación del GIL.
        - NumPy suele ser la primera optimización para operaciones numéricas repetitivas: evita ciclos Python.
        - La ley de Amdahl muestra que la parte serial establece un límite, incluso con muchos workers.
        - Orden recomendado: medir, vectorizar y después paralelizar lo que siga siendo lento.
        """
    )
