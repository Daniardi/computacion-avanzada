"""Actividad de clase — Sesión 3: cálculo aplicado y descenso de gradiente.

Ejecute este archivo con: python sesion_03_calculo_gradiente.py
Cada bloque contiene comentarios que explican su ejecución.
"""

# Importamos NumPy para arreglos, derivadas y cálculos numéricos.
import numpy as np
# Importamos Matplotlib para visualizar la convergencia de los algoritmos.
import matplotlib.pyplot as plt

# Fijamos la semilla para reproducir los datos simulados en cada ejecución.
np.random.seed(42)


def funcion(x):
    """Calcula f(x) = x² - 4x + 6, una parábola con mínimo en x = 2."""
    # Evaluamos la función objetivo que queremos minimizar.
    return x**2 - 4 * x + 6


def derivada_funcion(x):
    """Calcula la derivada analítica f'(x) = 2x - 4."""
    # La derivada indica si el valor de la función sube o baja en x.
    return 2 * x - 4


def derivada_numerica(funcion_objetivo, x, h=1e-5):
    """Aproxima una derivada mediante diferencia central."""
    # Comparamos la función a ambos lados de x para estimar la pendiente.
    return (funcion_objetivo(x + h) - funcion_objetivo(x - h)) / (2 * h)


def funcion_dos_variables(x, y):
    """Calcula f(x, y) = x² + y², cuyo mínimo global está en (0, 0)."""
    # Sumamos los cuadrados de las dos coordenadas del punto.
    return x**2 + y**2


def gradiente_funcion_dos_variables(x, y):
    """Devuelve el gradiente [df/dx, df/dy] de f(x, y) = x² + y²."""
    # Las derivadas parciales son 2x respecto a x y 2y respecto a y.
    return np.array([2 * x, 2 * y])


def descenso_gradiente(gradiente, punto_inicial, tasa_aprendizaje=0.1, iteraciones=30):
    """Aplica descenso de gradiente y devuelve todos los puntos visitados."""
    # Convertimos el punto inicial a un arreglo decimal para actualizarlo.
    punto = np.array(punto_inicial, dtype=float)
    # Guardamos el primer punto para mostrar la trayectoria completa.
    historial = [punto.copy()]
    # Repetimos la actualización indicada por el algoritmo de descenso.
    for _ in range(iteraciones):
        # Calculamos la dirección que hace crecer más rápidamente la función.
        gradiente_actual = gradiente(*punto)
        # Restamos el gradiente para movernos hacia un valor menor de la función.
        punto = punto - tasa_aprendizaje * gradiente_actual
        # Conservamos una copia para analizar la convergencia posteriormente.
        historial.append(punto.copy())
    # Convertimos la lista de puntos en una matriz de NumPy.
    return np.array(historial)


def crear_datos_consumo():
    """Crea datos simulados de temperatura y consumo energético industrial."""
    # Generamos 60 temperaturas entre 10 y 38 grados Celsius.
    temperatura = np.random.uniform(10, 38, 60)
    # Añadimos ruido para representar variaciones reales del consumo.
    ruido = np.random.normal(0, 8, 60)
    # Definimos una relación lineal conocida: consumo ≈ 12.5×temperatura + 40.
    consumo = 12.5 * temperatura + 40 + ruido
    # Normalizamos la temperatura para que el entrenamiento sea estable.
    temperatura_normalizada = (temperatura - temperatura.mean()) / temperatura.std()
    # Devolvemos las variables originales y normalizadas.
    return temperatura, temperatura_normalizada, consumo


def mse(peso, sesgo, entradas, salidas):
    """Calcula el error cuadrático medio de una recta y = peso*x + sesgo."""
    # Generamos las predicciones actuales del modelo lineal.
    predicciones = peso * entradas + sesgo
    # Promediamos el cuadrado de la diferencia entre valores reales y predichos.
    return np.mean((salidas - predicciones) ** 2)


def gradiente_mse(peso, sesgo, entradas, salidas):
    """Calcula las derivadas parciales del MSE respecto al peso y al sesgo."""
    # Generamos las predicciones que se usan para calcular el error.
    predicciones = peso * entradas + sesgo
    # Derivamos el MSE respecto al peso de la recta.
    derivada_peso = -(2 / len(entradas)) * np.sum(entradas * (salidas - predicciones))
    # Derivamos el MSE respecto al sesgo de la recta.
    derivada_sesgo = -(2 / len(entradas)) * np.sum(salidas - predicciones)
    # Agrupamos ambas derivadas como el gradiente del costo.
    return np.array([derivada_peso, derivada_sesgo])


def entrenar_regresion(entradas, salidas, tasa_aprendizaje=0.3, iteraciones=200):
    """Ajusta una recta con descenso de gradiente y devuelve su historial de error."""
    # Inicializamos el peso y el sesgo sin conocimiento previo.
    peso, sesgo = 0.0, 0.0
    # Creamos una lista para observar si el error baja durante el entrenamiento.
    costos = []
    # Ejecutamos las actualizaciones de parámetros solicitadas.
    for _ in range(iteraciones):
        # Calculamos cómo debe cambiar cada parámetro para reducir el MSE.
        gradiente_peso, gradiente_sesgo = gradiente_mse(peso, sesgo, entradas, salidas)
        # Actualizamos el peso en dirección contraria a su derivada.
        peso -= tasa_aprendizaje * gradiente_peso
        # Actualizamos el sesgo en dirección contraria a su derivada.
        sesgo -= tasa_aprendizaje * gradiente_sesgo
        # Registramos el error luego de actualizar los parámetros.
        costos.append(mse(peso, sesgo, entradas, salidas))
    # Entregamos el modelo aprendido y la evolución de su error.
    return peso, sesgo, costos


if __name__ == "__main__":
    # Comparamos la derivada exacta y la aproximación numérica en x = 0.5.
    punto_unidimensional = 0.5
    print("1. DERIVADA")
    print("Analítica:", derivada_funcion(punto_unidimensional))
    print("Numérica:", derivada_numerica(funcion, punto_unidimensional))

    # Mostramos el gradiente como vector de derivadas parciales.
    punto_inicial = (2.5, 2.5)
    print("\n2. GRADIENTE")
    print("Gradiente en", punto_inicial, ":", gradiente_funcion_dos_variables(*punto_inicial))

    # Aplicamos descenso de gradiente sobre el tazón f(x, y) = x² + y².
    historial = descenso_gradiente(gradiente_funcion_dos_variables, punto_inicial)
    print("\n3. DESCENSO DE GRADIENTE")
    print("Punto final:", np.round(historial[-1], 5))
    print("Valor final de f:", funcion_dos_variables(*historial[-1]))

    # Generamos datos y entrenamos la regresión de consumo energético.
    temperatura, temperatura_normalizada, consumo = crear_datos_consumo()
    peso, sesgo, costos = entrenar_regresion(temperatura_normalizada, consumo)
    print("\n4. REGRESIÓN DE CONSUMO ENERGÉTICO")
    print(f"Peso final: {peso:.4f}; sesgo final: {sesgo:.4f}; MSE final: {costos[-1]:.4f}")

    # Dibujamos la curva de error para comprobar que el modelo aprendió.
    plt.plot(costos, color="crimson")
    plt.title("Convergencia del MSE durante el entrenamiento")
    plt.xlabel("Iteración")
    plt.ylabel("MSE")
    plt.grid(True)
    plt.show()
