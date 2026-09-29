"""App Streamlit de la Sesión 3: cálculo aplicado y descenso de gradiente."""

# Importamos NumPy para trabajar con vectores, gradientes y datos simulados.
import numpy as np
# Importamos Matplotlib para graficar la trayectoria y la curva de error.
import matplotlib.pyplot as plt
# Importamos Streamlit para crear los controles interactivos de la aplicación.
import streamlit as st

# Configuramos el título y el diseño visible en el navegador.
st.set_page_config(page_title="Sesión 3 | Cálculo y gradiente", page_icon="📉", layout="wide")


def funcion(x, y):
    """Calcula la función objetivo f(x, y) = x² + y²."""
    # Esta función tiene su mínimo global en las coordenadas (0, 0).
    return x**2 + y**2


def gradiente(x, y):
    """Devuelve el vector [2x, 2y], el gradiente de la función objetivo."""
    # El gradiente señala la dirección de máximo crecimiento de f.
    return np.array([2 * x, 2 * y])


def descenso_gradiente(punto_inicial, tasa_aprendizaje, iteraciones):
    """Ejecuta el algoritmo y devuelve los puntos y costos de cada paso."""
    # Copiamos el punto inicial como valores decimales que se pueden actualizar.
    punto = np.array(punto_inicial, dtype=float)
    # Guardamos el primer punto y su costo antes de iniciar los cambios.
    puntos, costos = [punto.copy()], [funcion(*punto)]
    # Repetimos el cálculo del gradiente y el movimiento hacia abajo.
    for _ in range(iteraciones):
        # Calculamos la dirección de mayor aumento en el punto actual.
        gradiente_actual = gradiente(*punto)
        # Restamos esa dirección multiplicada por eta para disminuir f.
        punto = punto - tasa_aprendizaje * gradiente_actual
        # Guardamos el nuevo estado para dibujar la trayectoria.
        puntos.append(punto.copy())
        costos.append(funcion(*punto))
    # Devolvemos los historiales como arreglos de NumPy.
    return np.array(puntos), np.array(costos)


def datos_consumo():
    """Genera siempre los mismos datos simulados de temperatura y consumo."""
    # Usamos un generador fijo para que la app sea reproducible al interactuar.
    generador = np.random.default_rng(42)
    # Creamos temperaturas ambientales de una planta industrial.
    temperatura = generador.uniform(10, 38, 60)
    # Simulamos el consumo con una relación lineal y ruido realista.
    consumo = 12.5 * temperatura + 40 + generador.normal(0, 8, 60)
    # Normalizamos temperatura para lograr actualizaciones estables.
    normalizada = (temperatura - temperatura.mean()) / temperatura.std()
    # Devolvemos temperatura original, entrada normalizada y consumo objetivo.
    return temperatura, normalizada, consumo


def entrenar_regresion(entradas, salidas, tasa_aprendizaje, iteraciones):
    """Entrena una recta y registra el error cuadrático medio en cada paso."""
    # Comenzamos con una recta sin pendiente ni sesgo.
    peso, sesgo = 0.0, 0.0
    # Reservamos una lista para ver cómo disminuye el MSE.
    historial_mse = []
    # Repetimos las actualizaciones de descenso de gradiente.
    for _ in range(iteraciones):
        # Calculamos las predicciones de la recta actual.
        predicciones = peso * entradas + sesgo
        # Calculamos el vector de errores entre consumo real y predicho.
        errores = salidas - predicciones
        # Derivamos el MSE respecto a cada parámetro.
        derivada_peso = -(2 / len(entradas)) * np.sum(entradas * errores)
        derivada_sesgo = -(2 / len(entradas)) * np.sum(errores)
        # Actualizamos peso y sesgo en la dirección de menor error.
        peso -= tasa_aprendizaje * derivada_peso
        sesgo -= tasa_aprendizaje * derivada_sesgo
        # Registramos el MSE después de actualizar los parámetros.
        historial_mse.append(np.mean((salidas - (peso * entradas + sesgo)) ** 2))
    # Entregamos los parámetros ajustados y la historia de convergencia.
    return peso, sesgo, historial_mse


# Escribimos el encabezado de la aplicación.
st.title("📉 Sesión 3 — Cálculo aplicado y descenso de gradiente")
st.write("Explora cómo derivadas y gradientes permiten minimizar errores en Machine Learning.")

# Colocamos los controles principales en la barra lateral.
st.sidebar.header("Parámetros del descenso")
# Permitimos definir el punto desde el cual comienza la búsqueda del mínimo.
coordenada_x = st.sidebar.slider("Punto inicial x", -5.0, 5.0, 2.5, 0.1)
coordenada_y = st.sidebar.slider("Punto inicial y", -5.0, 5.0, 2.5, 0.1)
# Permitimos comparar tasas de aprendizaje lentas, estables o divergentes.
eta = st.sidebar.slider("Tasa de aprendizaje η", 0.01, 1.20, 0.10, 0.01)
# Permitimos decidir cuántas actualizaciones ejecutará el algoritmo.
pasos = st.sidebar.slider("Iteraciones", 1, 100, 30)

# Ejecutamos el algoritmo con los valores seleccionados por la persona usuaria.
trayectoria, costos = descenso_gradiente((coordenada_x, coordenada_y), eta, pasos)
# Clasificamos el comportamiento final según la magnitud del punto alcanzado.
if np.linalg.norm(trayectoria[-1]) < 0.01:
    estado = "Convergió al mínimo ✅"
elif np.linalg.norm(trayectoria[-1]) > np.linalg.norm(trayectoria[0]) * 2:
    estado = "Diverge: η es demasiado grande ⚠️"
else:
    estado = "Aún está acercándose al mínimo ⏳"

# Mostramos una explicación breve de la regla de actualización.
st.info("Regla usada: **punto nuevo = punto actual − η × gradiente**. El gradiente apunta cuesta arriba; por eso se resta.")
# Mostramos el estado final y dos métricas importantes.
columna_1, columna_2, columna_3 = st.columns(3)
columna_1.metric("Estado", estado)
columna_2.metric("f(inicial)", f"{costos[0]:.4f}")
columna_3.metric("f(final)", f"{costos[-1]:.4f}")

# Creamos el mapa de contornos y la curva de convergencia lado a lado.
figura, ejes = plt.subplots(1, 2, figsize=(13, 5))
# Construimos una cuadrícula sobre la que se evalúa la función f(x, y).
eje_x = np.linspace(-5, 5, 150)
eje_y = np.linspace(-5, 5, 150)
rejilla_x, rejilla_y = np.meshgrid(eje_x, eje_y)
valores_z = funcion(rejilla_x, rejilla_y)
# Dibujamos curvas de nivel y la trayectoria del algoritmo.
ejes[0].contour(rejilla_x, rejilla_y, valores_z, levels=25, cmap="viridis")
ejes[0].plot(trayectoria[:, 0], trayectoria[:, 1], "o-", color="crimson", markersize=3, label="Trayectoria")
ejes[0].scatter([0], [0], color="gold", edgecolor="black", s=100, label="Mínimo")
ejes[0].set(title="Descenso de gradiente sobre f(x,y)=x²+y²", xlabel="x", ylabel="y", xlim=(-5, 5), ylim=(-5, 5))
ejes[0].legend()
# Dibujamos cómo disminuye o aumenta el costo en cada iteración.
ejes[1].plot(costos, color="crimson", linewidth=2)
ejes[1].set(title="Evolución del costo", xlabel="Iteración", ylabel="f(x, y)")
ejes[1].grid(True)
# Enviamos la figura terminada a la interfaz de Streamlit.
st.pyplot(figura, clear_figure=True)

# Agregamos el caso aplicado que aparece al final del cuaderno oficial.
st.header("Caso aplicado: consumo energético")
# Obtenemos los datos reproducibles de temperatura y consumo.
temperatura, temperatura_normalizada, consumo = datos_consumo()
# Entrenamos una regresión lineal con la misma tasa seleccionada, limitada para estabilidad.
tasa_regresion = min(eta, 0.3)
peso, sesgo, mse = entrenar_regresion(temperatura_normalizada, consumo, tasa_regresion, 200)
# Informamos los parámetros aprendidos y el error del modelo.
dato_1, dato_2, dato_3 = st.columns(3)
dato_1.metric("Peso aprendido", f"{peso:.2f}")
dato_2.metric("Sesgo aprendido", f"{sesgo:.2f}")
dato_3.metric("MSE final", f"{mse[-1]:.2f}")

# Creamos las gráficas del ajuste lineal y de la convergencia del MSE.
figura_regresion, ejes_regresion = plt.subplots(1, 2, figsize=(13, 5))
# Ordenamos la temperatura para dibujar una recta continua sobre los datos.
orden = np.argsort(temperatura)
ejes_regresion[0].scatter(temperatura, consumo, color="teal", alpha=0.7, label="Datos simulados")
ejes_regresion[0].plot(temperatura[orden], peso * temperatura_normalizada[orden] + sesgo, color="crimson", linewidth=2, label="Recta ajustada")
ejes_regresion[0].set(title="Temperatura vs. consumo energético", xlabel="Temperatura (°C)", ylabel="Consumo (kWh)")
ejes_regresion[0].legend()
# Mostramos si el MSE disminuye durante el ajuste de los parámetros.
ejes_regresion[1].plot(mse, color="navy", linewidth=2)
ejes_regresion[1].set(title="Convergencia del MSE", xlabel="Iteración", ylabel="MSE")
ejes_regresion[1].grid(True)
# Enviamos la segunda figura a Streamlit.
st.pyplot(figura_regresion, clear_figure=True)
