"""Aplicación interactiva de la Sesión 2: vectores y matrices."""

# Importamos NumPy para todas las operaciones de álgebra lineal.
import numpy as np
# Importamos Pandas para presentar matrices y resultados como tablas.
import pandas as pd
# Importamos Streamlit para construir la interfaz web.
import streamlit as st
# Importamos datasets reales para los ejercicios de la sesión.
from sklearn.datasets import load_digits, load_iris

# Configuramos el título que aparecerá en la pestaña del navegador.
st.set_page_config(page_title="Sesión 2 | Vectores y matrices", page_icon="📐", layout="wide")


def tabla(matriz):
    """Convierte un vector o matriz de NumPy en una tabla para Streamlit."""
    # Si el dato tiene una dimensión, lo mostramos como un vector fila.
    if matriz.ndim == 1:
        return pd.DataFrame([matriz])
    # Si el dato tiene dos dimensiones, conservamos filas y columnas.
    return pd.DataFrame(matriz)


def similitud_coseno(vector_a, vector_b):
    """Calcula la similitud coseno entre dos vectores no nulos."""
    # El producto punto es el numerador de la fórmula de similitud coseno.
    numerador = np.dot(vector_a, vector_b)
    # Multiplicamos las normas para calcular el denominador de la fórmula.
    denominador = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    # Devolvemos la medida de alineación entre -1 y 1.
    return numerador / denominador


# Mostramos el encabezado y el propósito de la actividad.
st.title("📐 Sesión 2 — Vectores y matrices")
st.write("Aplicación interactiva basada en la guía de Computación Avanzada.")

# Creamos la navegación lateral para organizar el paso a paso de la sesión.
seccion = st.sidebar.radio(
    "Selecciona una sección",
    ["Inicio", "Vectores", "Matrices", "Producto punto", "PCA y SVD", "Ejercicios resueltos"],
)

if seccion == "Inicio":
    # Explicamos la relación entre los conceptos y Machine Learning.
    st.header("¿Por qué son importantes?")
    st.markdown(
        "En Machine Learning, un **vector** representa un dato y una **matriz** "
        "representa muchos datos o una transformación. Esta app permite explorar "
        "esas ideas y verificar los resultados de los ejercicios propuestos."
    )
    # Indicamos el recorrido sugerido para la actividad de clase.
    st.info("Recorre el menú en orden: vectores → matrices → producto punto → PCA/SVD → ejercicios.")

elif seccion == "Vectores":
    # Permitimos que la persona defina dos vectores de dos dimensiones.
    st.header("1. Operaciones con vectores")
    columna_1, columna_2 = st.columns(2)
    # Leemos los valores del vector v desde controles numéricos.
    with columna_1:
        valor_vx = st.number_input("v₁", value=3.0)
        valor_vy = st.number_input("v₂", value=2.0)
    # Leemos los valores del vector u desde controles numéricos.
    with columna_2:
        valor_ux = st.number_input("u₁", value=1.0)
        valor_uy = st.number_input("u₂", value=3.0)
    # Construimos los arreglos NumPy con los valores ingresados.
    vector_v = np.array([valor_vx, valor_vy])
    vector_u = np.array([valor_ux, valor_uy])
    # Mostramos suma y multiplicación por escalar como en el cuaderno.
    resultado_1, resultado_2 = st.columns(2)
    resultado_1.metric("v + u", str(np.round(vector_v + vector_u, 3)))
    resultado_2.metric("2 × v", str(np.round(2 * vector_v, 3)))
    # Explicamos la interpretación geométrica de cada resultado.
    st.caption("La suma combina los desplazamientos; multiplicar por 2 duplica la magnitud de v.")

elif seccion == "Matrices":
    # Presentamos las matrices de ejemplo de la guía.
    st.header("2. Operaciones con matrices")
    matriz_a = np.array([[1, 2], [3, 4]])
    matriz_b = np.array([[2, 0], [1, 3]])
    # Mostramos ambas matrices de entrada en columnas separadas.
    columna_a, columna_b = st.columns(2)
    columna_a.write("Matriz A")
    columna_a.dataframe(tabla(matriz_a), use_container_width=True)
    columna_b.write("Matriz B")
    columna_b.dataframe(tabla(matriz_b), use_container_width=True)
    # Calculamos los tres resultados que compara la actividad.
    producto_matricial = matriz_a @ matriz_b
    producto_elemento = matriz_a * matriz_b
    transpuesta_a = matriz_a.T
    # Mostramos los resultados de cada operación.
    st.subheader("Resultados")
    st.write("A @ B — producto matricial")
    st.dataframe(tabla(producto_matricial), use_container_width=True)
    st.write("A * B — multiplicación elemento a elemento")
    st.dataframe(tabla(producto_elemento), use_container_width=True)
    st.write("A.T — transpuesta de A")
    st.dataframe(tabla(transpuesta_a), use_container_width=True)
    # Desglosamos una celda seleccionada para explicar fila por columna.
    fila = st.selectbox("Fila de A", [0, 1])
    columna = st.selectbox("Columna de B", [0, 1])
    # Extraemos los valores usados en la celda seleccionada.
    valores_fila = matriz_a[fila, :]
    valores_columna = matriz_b[:, columna]
    # Calculamos el producto punto que llena esa posición del resultado.
    valor_celda = np.dot(valores_fila, valores_columna)
    st.success(f"C[{fila}, {columna}] = {valores_fila} · {valores_columna} = {valor_celda}")

elif seccion == "Producto punto":
    # Definimos los vectores del ejemplo original de la guía.
    st.header("3. Producto punto, norma y similitud coseno")
    vector_u = np.array([4, 1])
    vector_v = np.array([1, 3])
    # Calculamos las tres medidas principales de esta sección.
    norma_u = np.linalg.norm(vector_u)
    punto = np.dot(vector_u, vector_v)
    coseno = similitud_coseno(vector_u, vector_v)
    # Mostramos las medidas en tarjetas.
    metrica_1, metrica_2, metrica_3 = st.columns(3)
    metrica_1.metric("Norma de u", f"{norma_u:.3f}")
    metrica_2.metric("u · v", f"{punto:.3f}")
    metrica_3.metric("Similitud coseno", f"{coseno:.3f}")
    # Indicamos la interpretación del resultado obtenido.
    st.info("Un coseno cercano a 1 significa que ambos vectores apuntan en direcciones similares.")

elif seccion == "PCA y SVD":
    # Cargamos Iris para demostrar la reducción de dimensionalidad.
    st.header("4. Autovalores, PCA y SVD")
    iris = load_iris()
    # Centramos cada columna antes de calcular la matriz de covarianza.
    datos_centrados = iris.data - iris.data.mean(axis=0)
    # Calculamos autovalores y autovectores de la covarianza de Iris.
    valores, _ = np.linalg.eig(np.cov(datos_centrados, rowvar=False))
    # Ordenamos los autovalores de mayor a menor para medir la varianza principal.
    valores = np.sort(valores)[::-1]
    # Calculamos la proporción acumulada de varianza explicada por PCA.
    varianza = np.cumsum(valores) / valores.sum()
    # Calculamos la SVD de Iris centrado para analizar su energía acumulada.
    _, singulares, _ = np.linalg.svd(datos_centrados, full_matrices=False)
    energia = np.cumsum(singulares ** 2) / np.sum(singulares ** 2)
    # Presentamos ambos resultados en una tabla comparativa.
    st.dataframe(
        pd.DataFrame(
            {"Componente": range(1, len(valores) + 1), "Varianza PCA acumulada": varianza, "Energía SVD acumulada": energia}
        ),
        use_container_width=True,
    )
    # Destacamos la información retenida con los dos primeros componentes.
    st.success(f"Los dos primeros componentes de PCA explican {varianza[1] * 100:.1f}% de la varianza de Iris.")

else:
    # Cargamos Digits para resolver el primer ejercicio propuesto.
    st.header("5. Ejercicios propuestos — soluciones")
    digitos = load_digits()
    # Localizamos dos imágenes de la clase 0 y una imagen de la clase 1.
    ceros = np.where(digitos.target == 0)[0]
    indice_uno = np.where(digitos.target == 1)[0][0]
    # Comparamos dos dígitos iguales y dos dígitos de clases diferentes.
    coseno_misma_clase = similitud_coseno(digitos.data[ceros[0]], digitos.data[ceros[1]])
    coseno_distinta_clase = similitud_coseno(digitos.data[ceros[0]], digitos.data[indice_uno])
    # Mostramos la respuesta al primer ejercicio.
    st.subheader("Ejercicio 1 — Similitud coseno")
    dato_1, dato_2 = st.columns(2)
    dato_1.metric("Dos dígitos 0", f"{coseno_misma_clase:.4f}")
    dato_2.metric("Un 0 y un 1", f"{coseno_distinta_clase:.4f}")
    # Resolvemos el segundo ejercicio: rotar y escalar el vector [2, 0].
    st.subheader("Ejercicio 2 — Rotación con escalado")
    grados = st.slider("Ángulo de rotación", min_value=0, max_value=360, value=45)
    escala = st.slider("Factor de escala", min_value=1.0, max_value=5.0, value=2.0, step=0.5)
    # Convertimos grados a radianes para construir la matriz de rotación.
    angulo = np.radians(grados)
    matriz_rotacion = np.array([[np.cos(angulo), -np.sin(angulo)], [np.sin(angulo), np.cos(angulo)]])
    # Multiplicamos por la escala antes de aplicar la transformación al vector.
    vector_transformado = (escala * matriz_rotacion) @ np.array([2, 0])
    st.write("Vector [2, 0] transformado:", np.round(vector_transformado, 3))
    # Resolvemos el tercer ejercicio usando la SVD de Iris centrado.
    st.subheader("Ejercicio 3 — SVD de Iris y 95% de energía")
    iris = load_iris()
    iris_centrado = iris.data - iris.data.mean(axis=0)
    _, singulares, _ = np.linalg.svd(iris_centrado, full_matrices=False)
    energia = np.cumsum(singulares ** 2) / np.sum(singulares ** 2)
    # Buscamos la primera cantidad de componentes que supera el umbral del 95%.
    componentes = np.argmax(energia >= 0.95) + 1
    st.success(f"Se necesitan {componentes} componentes para explicar {energia[componentes - 1] * 100:.2f}% de la energía.")
