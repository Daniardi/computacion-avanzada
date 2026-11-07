"""Sesión 16: introducción al procesamiento paralelo y vectorización."""

# Importamos herramientas para medir tiempo, ejecutar tareas y usar arreglos numéricos.
import os
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

import numpy as np


def leer_sensor(id_sensor, demora=0.10):
    """Simula una tarea de entrada/salida que espera una respuesta de sensor."""
    # Esperamos para representar el tiempo de comunicación con un dispositivo externo.
    time.sleep(demora)
    # Devolvemos una lectura sencilla asociada con el identificador del sensor.
    return f"Sensor {id_sensor}: lectura recibida"


def procesar_sensor(id_sensor, cantidad=200_000):
    """Simula una tarea intensiva de CPU que puede ejecutarse en un proceso."""
    # Acumulamos cálculos para representar procesamiento continuo de lecturas.
    suma = 0
    for indice in range(cantidad):
        suma += (indice * id_sensor) % 100
    # Devolvemos el promedio calculado por este worker.
    return suma / cantidad


def amdahl(fraccion_paralelizable, workers):
    """Calcula el speedup teórico según la ley de Amdahl."""
    # Sumamos la parte serial y la parte paralelizada entre los workers disponibles.
    return 1 / ((1 - fraccion_paralelizable) + fraccion_paralelizable / workers)


if __name__ == "__main__":
    # Definimos ocho sensores que tardan principalmente esperando respuesta.
    sensores = list(range(1, 9))
    # Medimos lectura serial: se espera cada sensor uno después del otro.
    inicio = time.perf_counter()
    list(map(leer_sensor, sensores))
    tiempo_serial = time.perf_counter() - inicio
    # Medimos lectura con hilos: varias esperas ocurren simultáneamente.
    inicio = time.perf_counter()
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(leer_sensor, sensores))
    tiempo_hilos = time.perf_counter() - inicio
    # Mostramos la mejora obtenida en una tarea dominada por espera.
    print(f"Serial: {tiempo_serial:.2f} s | Hilos: {tiempo_hilos:.2f} s")

    # Ejecutamos trabajo de CPU con procesos independientes si la máquina lo permite.
    with ProcessPoolExecutor(max_workers=min(4, os.cpu_count() or 1)) as executor:
        resultados = list(executor.map(procesar_sensor, [1, 2, 3, 4]))
    print("Promedios calculados con procesos:", np.round(resultados, 2))

    # Comparamos una conversión de temperatura con ciclo Python y con NumPy.
    celsius = np.linspace(18, 30, 200_000)
    inicio = time.perf_counter()
    fahrenheit_ciclo = [valor * 9 / 5 + 32 for valor in celsius]
    tiempo_ciclo = time.perf_counter() - inicio
    inicio = time.perf_counter()
    fahrenheit_numpy = celsius * 9 / 5 + 32
    tiempo_numpy = time.perf_counter() - inicio
    print(f"Vectorización: ciclo {tiempo_ciclo:.4f} s | NumPy {tiempo_numpy:.4f} s")
    print("Mismo resultado:", np.allclose(fahrenheit_ciclo, fahrenheit_numpy))
