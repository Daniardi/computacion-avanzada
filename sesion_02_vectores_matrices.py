"""Actividad de clase — Sesión 2: Vectores y matrices.

Cada sección reproduce los conceptos del cuaderno de clase y al final resuelve
los tres ejercicios propuestos. Ejecute: python sesion_02_vectores_matrices.py
"""

# Importamos NumPy para calcular con vectores, matrices, PCA y SVD.
import numpy as np
# Importamos Matplotlib para mostrar las representaciones gráficas.
import matplotlib.pyplot as plt
# Importamos los conjuntos de datos Iris y Digits usados en la actividad.
from sklearn.datasets import load_digits, load_iris

# Configuramos la impresión de arreglos para que los resultados sean legibles.
np.set_printoptions(precision=3, suppress=True)


def mostrar_vector_y_suma():
    """Crea dos vectores 2D y aplica suma y multiplicación por escalar."""
    # Definimos el vector v con sus coordenadas x e y.
    v = np.array([3, 2])
    # Definimos un segundo vector para operar con v.
    u = np.array([1, 3])
    # Mostramos cada operación vectorial solicitada en la guía.
    print("\n1. VECTORES\nv =", v, "\nu =", u, "\nv + u =", v + u, "\n2 * v =", 2 * v)

    # Creamos el plano cartesiano en el que se dibujarán los vectores.
    _, eje = plt.subplots(figsize=(6, 6))
    # Dibujamos v desde el origen en color azul.
    eje.quiver(0, 0, *v, angles="xy", scale_units="xy", scale=1, color="steelblue", label="v")
    # Dibujamos u desde el origen en color naranja.
    eje.quiver(0, 0, *u, angles="xy", scale_units="xy", scale=1, color="darkorange", label="u")
    # Dibujamos el vector suma para visualizar la regla del paralelogramo.
    eje.quiver(0, 0, *(v + u), angles="xy", scale_units="xy", scale=1, color="seagreen", label="v + u")
    # Fijamos límites, cuadrícula y referencias para facilitar la lectura del gráfico.
    eje.set(xlim=(-1, 6), ylim=(-1, 6), title="Suma de vectores")
    eje.grid(True)
    eje.legend()
    plt.show()


def explorar_iris():
    """Representa dos flores del dataset Iris como vectores de cuatro medidas."""
    # Cargamos el dataset que contiene 150 flores y sus cuatro características.
    iris = load_iris()
    # Guardamos las medidas en una matriz: filas=flor, columnas=característica.
    datos = iris.data
    # Seleccionamos una setosa y una versicolor para compararlas.
    flor_setosa, flor_versicolor = datos[0], datos[50]
    # Mostramos la diferencia componente a componente entre las dos flores.
    print("\nFlor setosa:", flor_setosa)
    print("Flor versicolor:", flor_versicolor)
    print("Diferencia:", flor_setosa - flor_versicolor)
    # Devolvemos los datos para reutilizarlos en los demás ejemplos.
    return iris


def operaciones_matrices():
    """Muestra producto matricial, producto elemento a elemento, transpuesta e inversa."""
    # Construimos la primera matriz cuadrada de tamaño 2 por 2.
    matriz_a = np.array([[1, 2], [3, 4]])
    # Construimos la segunda matriz compatible para multiplicación matricial.
    matriz_b = np.array([[2, 0], [1, 3]])
    # @ aplica el producto matricial: fila de A por columna de B.
    print("\n2. MATRICES\nA @ B =\n", matriz_a @ matriz_b)
    # * multiplica posición por posición y por eso da un resultado distinto.
    print("A * B =\n", matriz_a * matriz_b)
    # .T intercambia filas por columnas para calcular la transpuesta.
    print("A transpuesta =\n", matriz_a.T)
    # inv calcula la matriz inversa, útil para resolver sistemas lineales.
    print("Inversa de A =\n", np.linalg.inv(matriz_a))

    # Definimos las matrices usadas para explicar cada celda del producto.
    a2 = np.array([[1, 2, 3], [4, 5, 6]])
    b2 = np.array([[7, 8], [9, 10], [11, 12]])
    # Calculamos el resultado completo de 2x3 por 3x2, que será de 2x2.
    c2 = a2 @ b2
    # Recorremos cada celda del resultado para desglosar su producto punto.
    for fila in range(a2.shape[0]):
        for columna in range(b2.shape[1]):
            # Extraemos la fila de A y la columna de B que forman C[fila, columna].
            valores_fila, valores_columna = a2[fila, :], b2[:, columna]
            # Calculamos la suma de los productos de pares correspondientes.
            resultado = (valores_fila * valores_columna).sum()
            print(f"C[{fila},{columna}] = {valores_fila} · {valores_columna} = {resultado}")
    # Mostramos la matriz calculada después de explicar sus entradas.
    print("C completa =\n", c2)


def producto_punto_y_pca(iris):
    """Calcula norma, similitud coseno, autovalores y PCA manual para Iris."""
    # Definimos dos vectores para estudiar su magnitud y alineación.
    u, v = np.array([4, 1]), np.array([1, 3])
    # La norma euclidiana mide la longitud del vector u.
    norma_u = np.linalg.norm(u)
    # El producto punto combina los valores de ambos vectores.
    producto = np.dot(u, v)
    # Dividimos por las normas para obtener similitud coseno entre -1 y 1.
    coseno = producto / (np.linalg.norm(u) * np.linalg.norm(v))
    print(f"\n3. PRODUCTO PUNTO\n||u|| = {norma_u:.3f}; u·v = {producto}; coseno = {coseno:.3f}")

    # Centramos cada característica de Iris antes de calcular su covarianza.
    datos_centrados = iris.data - iris.data.mean(axis=0)
    # Creamos la matriz que describe cómo varían conjuntamente las características.
    covarianza = np.cov(datos_centrados, rowvar=False)
    # Obtenemos autovalores y autovectores de la matriz de covarianza.
    valores, vectores = np.linalg.eig(covarianza)
    # Ordenamos los componentes de mayor a menor varianza explicada.
    orden = np.argsort(valores)[::-1]
    valores, vectores = valores[orden], vectores[:, orden]
    # Sumamos los dos primeros componentes para conocer su porcentaje de información.
    porcentaje = 100 * valores[:2].sum() / valores.sum()
    print(f"\n4. PCA MANUAL\nVarianza explicada por 2 componentes: {porcentaje:.1f}%")
    # Proyectamos los cuatro atributos originales en los dos componentes principales.
    proyeccion = datos_centrados @ vectores[:, :2]
    # Dibujamos las flores en el nuevo plano reducido a dos dimensiones.
    plt.scatter(proyeccion[:, 0], proyeccion[:, 1], c=iris.target, cmap="viridis")
    plt.title("PCA manual del dataset Iris")
    plt.xlabel("Componente principal 1")
    plt.ylabel("Componente principal 2")
    plt.grid(True)
    plt.show()


def ejercicios_propuestos(iris):
    """Resuelve los tres ejercicios finales indicados en el cuaderno de clase."""
    # EJERCICIO 1: cargamos imágenes de dígitos representadas como vectores de 64 píxeles.
    digitos = load_digits()
    # Elegimos dos ceros y un uno para comparar misma clase contra clase distinta.
    indice_cero_1, indice_cero_2 = np.where(digitos.target == 0)[0][:2]
    indice_uno = np.where(digitos.target == 1)[0][0]
    # Definimos una función reutilizable para calcular la similitud coseno.
    def similitud_coseno(a, b):
        # np.dot calcula el numerador y las normas calculan el denominador.
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    # Mostramos la similitud entre dos ceros y después entre un cero y un uno.
    print("\nEJERCICIO 1 — Similitud coseno")
    print("Dos dígitos 0:", round(similitud_coseno(digitos.data[indice_cero_1], digitos.data[indice_cero_2]), 4))
    print("Un dígito 0 y un dígito 1:", round(similitud_coseno(digitos.data[indice_cero_1], digitos.data[indice_uno]), 4))

    # EJERCICIO 2: convertimos 45 grados a radianes para usar funciones trigonométricas.
    angulo = np.radians(45)
    # Construimos la matriz que rota cualquier vector 45 grados en el plano.
    rotacion = np.array([[np.cos(angulo), -np.sin(angulo)], [np.sin(angulo), np.cos(angulo)]])
    # Multiplicamos la rotación por 2 para añadir el escalado pedido.
    rotacion_y_escala = 2 * rotacion
    # Aplicamos la transformación al vector de ejemplo.
    vector_original = np.array([2, 0])
    print("\nEJERCICIO 2 — Rotación y escalado\nVector transformado:", rotacion_y_escala @ vector_original)

    # EJERCICIO 3: centramos Iris porque SVD analiza mejor su variación sin el promedio.
    iris_centrado = iris.data - iris.data.mean(axis=0)
    # S contiene los valores singulares ordenados de mayor a menor.
    _, valores_singulares, _ = np.linalg.svd(iris_centrado, full_matrices=False)
    # Elevamos al cuadrado los valores singulares para calcular la energía total.
    energia_acumulada = np.cumsum(valores_singulares ** 2) / np.sum(valores_singulares ** 2)
    # localizamos el primer número de componentes que alcanza al menos el 95%.
    componentes_95 = np.argmax(energia_acumulada >= 0.95) + 1
    print("\nEJERCICIO 3 — SVD de Iris")
    print("Valores singulares:", np.round(valores_singulares, 3))
    print(f"Componentes necesarios para 95% de energía: {componentes_95}")
    print(f"Energía acumulada: {energia_acumulada[componentes_95 - 1] * 100:.2f}%")


if __name__ == "__main__":
    # Ejecutamos en orden todo el paso a paso de la sesión.
    mostrar_vector_y_suma()
    # Cargamos Iris una sola vez y reutilizamos sus datos.
    dataset_iris = explorar_iris()
    # Ejecutamos los ejemplos de operaciones entre matrices.
    operaciones_matrices()
    # Ejecutamos los cálculos de producto punto y PCA.
    producto_punto_y_pca(dataset_iris)
    # Ejecutamos y mostramos las respuestas de los ejercicios propuestos.
    ejercicios_propuestos(dataset_iris)
