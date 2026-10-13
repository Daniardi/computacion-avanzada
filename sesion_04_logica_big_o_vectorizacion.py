"""Actividad de clase — Sesión 4: lógica, Big-O y vectorización.

Ejecute este archivo con: python sesion_04_logica_big_o_vectorizacion.py
Los comentarios describen qué hace cada bloque de código.
"""

# Importamos NumPy para crear y procesar arreglos de datos de sensores.
import numpy as np
# Importamos time para medir el tiempo de las dos implementaciones.
import time
# Importamos Matplotlib para comparar visualmente complejidades y rendimientos.
import matplotlib.pyplot as plt

# Fijamos una semilla para obtener los mismos datos aleatorios en cada ejecución.
np.random.seed(42)


def activar_alarma(temperatura, humedad):
    """Evalúa P AND Q para una única lectura ambiental."""
    # P es verdadera cuando la temperatura supera los 30 °C.
    temperatura_alta = temperatura > 30
    # Q es verdadera cuando la humedad es menor que 40 %.
    humedad_baja = humedad < 40
    # La alarma se activa únicamente si P y Q son verdaderas.
    return temperatura_alta and humedad_baja


def generar_datos(n):
    """Genera n temperaturas y humedades simuladas de sensores."""
    # Creamos temperaturas entre 15 y 40 grados Celsius.
    temperaturas = np.random.uniform(15, 40, n)
    # Creamos humedades entre 20 y 80 por ciento.
    humedades = np.random.uniform(20, 80, n)
    # Entregamos ambos vectores con n posiciones.
    return temperaturas, humedades


def generar_datos_con_dia(n):
    """Genera sensores y una bandera booleana que indica fin de semana."""
    # Reutilizamos la función anterior para las mediciones ambientales.
    temperaturas, humedades = generar_datos(n)
    # Representamos los días con números: 0=lunes y 6=domingo.
    dias = np.random.randint(0, 7, n)
    # Marcamos sábado (5) y domingo (6) como fin de semana.
    es_fin_de_semana = (dias == 5) | (dias == 6)
    # Retornamos los tres arreglos de la actividad.
    return temperaturas, humedades, es_fin_de_semana


def alarma_con_loop(temperaturas, humedades):
    """Aplica P AND Q con un loop: complejidad temporal O(n)."""
    # Preparamos una lista para almacenar las decisiones de alarma.
    resultados = []
    # Contamos evaluaciones lógicas para evidenciar el crecimiento lineal.
    operaciones = 0
    # Recorremos una vez cada pareja de lecturas de sensor.
    for temperatura, humedad in zip(temperaturas, humedades):
        # Cada vuelta evalúa una lectura, por eso hay n evaluaciones.
        operaciones += 1
        # Guardamos el resultado lógico para la lectura actual.
        resultados.append(temperatura > 30 and humedad < 40)
    # Entregamos decisiones y número de operaciones realizadas.
    return resultados, operaciones


def alarma_vectorizada(temperaturas, humedades):
    """Aplica P AND Q en arreglos NumPy: también O(n), pero más eficiente."""
    # NumPy compara todos los valores de temperatura en código compilado.
    temperatura_alta = temperaturas > 30
    # NumPy compara todos los valores de humedad al mismo tiempo.
    humedad_baja = humedades < 40
    # & ejecuta AND elemento a elemento sobre los vectores booleanos.
    return temperatura_alta & humedad_baja


def alarma_con_loop_v2(temperaturas, humedades, es_fin_de_semana):
    """Resuelve el reto: P AND Q AND NOT R con un loop O(n)."""
    # Creamos la lista de decisiones y el contador de operaciones.
    resultados, operaciones = [], 0
    # Recorremos cada lectura solo una vez, igual que en la primera versión.
    for temperatura, humedad, fin_de_semana in zip(temperaturas, humedades, es_fin_de_semana):
        # Una iteración por lectura mantiene el crecimiento lineal O(n).
        operaciones += 1
        # Aplicamos la tercera condición solicitada: no debe ser fin de semana.
        resultados.append(temperatura > 30 and humedad < 40 and not fin_de_semana)
    # Devolvemos resultados y total de evaluaciones.
    return resultados, operaciones


def alarma_vectorizada_v2(temperaturas, humedades, es_fin_de_semana):
    """Resuelve el reto con NumPy: P & Q & ~R sobre arreglos completos."""
    # Evaluamos P para todas las temperaturas.
    temperatura_alta = temperaturas > 30
    # Evaluamos Q para todas las humedades.
    humedad_baja = humedades < 40
    # ~ invierte R: True cuando no es fin de semana.
    no_es_fin_de_semana = ~es_fin_de_semana
    # Combinamos las tres proposiciones por posición del arreglo.
    return temperatura_alta & humedad_baja & no_es_fin_de_semana


def binarizar_vectorizada(imagen, umbral=128):
    """Binariza una imagen con NumPy, evitando loops anidados explícitos."""
    # Cada píxel mayor al umbral se transforma en blanco (255); los demás en negro (0).
    return np.where(imagen > umbral, 255, 0).astype(np.uint8)


if __name__ == "__main__":
    # Probamos la regla básica con los cuatro casos de la tabla de verdad.
    print("1. LÓGICA PROPOSICIONAL")
    for temperatura, humedad in [(35, 30), (35, 60), (20, 30), (20, 60)]:
        # Mostramos si cada combinación activa o no la alarma.
        print(f"Temperatura={temperatura} °C, humedad={humedad}% -> {activar_alarma(temperatura, humedad)}")

    # Creamos diez mil lecturas para comparar loop y vectorización.
    temperaturas, humedades = generar_datos(10_000)
    # Medimos la implementación basada en un loop de Python.
    inicio_loop = time.perf_counter()
    resultados_loop, operaciones = alarma_con_loop(temperaturas, humedades)
    tiempo_loop = time.perf_counter() - inicio_loop
    # Medimos la implementación basada en operaciones vectorizadas de NumPy.
    inicio_vectorizado = time.perf_counter()
    resultados_vectorizados = alarma_vectorizada(temperaturas, humedades)
    tiempo_vectorizado = time.perf_counter() - inicio_vectorizado
    # Verificamos que las dos versiones toman las mismas decisiones.
    print("\n2. LOOP VS. NUMPY")
    print(f"Operaciones del loop: {operaciones:,}")
    print(f"Resultados iguales: {np.array_equal(np.array(resultados_loop), resultados_vectorizados)}")
    print(f"Tiempo loop: {tiempo_loop:.6f}s | Tiempo NumPy: {tiempo_vectorizado:.6f}s")

    # Resolvemos el reto con un millón de datos y la condición de fin de semana.
    temperaturas, humedades, fines_de_semana = generar_datos_con_dia(1_000_000)
    # Medimos la solución con loop, que sigue teniendo una pasada sobre los datos.
    inicio_loop = time.perf_counter()
    reto_loop, operaciones_reto = alarma_con_loop_v2(temperaturas, humedades, fines_de_semana)
    tiempo_loop_reto = time.perf_counter() - inicio_loop
    # Medimos la versión vectorizada de la misma regla lógica.
    inicio_vectorizado = time.perf_counter()
    reto_vectorizado = alarma_vectorizada_v2(temperaturas, humedades, fines_de_semana)
    tiempo_vectorizado_reto = time.perf_counter() - inicio_vectorizado
    # Imprimimos la respuesta conceptual y las métricas pedidas por el reto.
    print("\n3. RETO RESUELTO")
    print("Big-O no cambia: continúa siendo O(n), porque cada lectura se evalúa una sola vez.")
    print(f"Operaciones lógicas: {operaciones_reto:,}")
    print(f"Resultados iguales: {np.array_equal(np.array(reto_loop), reto_vectorizado)}")
    print(f"Tiempo loop: {tiempo_loop_reto:.6f}s | Tiempo NumPy: {tiempo_vectorizado_reto:.6f}s")

    # Graficamos el crecimiento teórico de complejidades comunes.
    n = np.arange(1, 10)
    plt.plot(n, np.ones_like(n), label="O(1)")
    plt.plot(n, n, label="O(n)")
    plt.plot(n, n * np.log2(n), label="O(n log n)")
    plt.plot(n, n**2, label="O(n²)")
    plt.title("Crecimiento teórico de complejidades")
    plt.xlabel("Tamaño de entrada (n)")
    plt.ylabel("Operaciones teóricas")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.show()
