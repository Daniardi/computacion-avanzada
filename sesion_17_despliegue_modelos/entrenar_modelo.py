"""Entrena y exporta el modelo JSON utilizado por la aplicación desplegada."""

# Importamos JSON y la ruta donde se guardará el modelo exportado.
import json
from pathlib import Path

# Importamos datos, división de conjuntos y regresión lineal de scikit-learn.
from sklearn.datasets import fetch_california_housing
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Descargamos el conjunto California Housing con sus nombres de columnas.
datos = fetch_california_housing(as_frame=True)
x = datos.data
y = datos.target
# Separamos entrenamiento y prueba para evaluar el modelo sin usar datos vistos.
x_entrenamiento, x_prueba, y_entrenamiento, y_prueba = train_test_split(
    x, y, test_size=0.2, random_state=42
)
# Calculamos los parámetros de normalización solo en entrenamiento.
media = x_entrenamiento.mean()
desviacion = x_entrenamiento.std()
# Transformamos ambos conjuntos con la misma escala.
x_entrenamiento_escalado = (x_entrenamiento - media) / desviacion
x_prueba_escalado = (x_prueba - media) / desviacion
# Ajustamos la regresión y evaluamos R2 en los datos de prueba.
modelo = LinearRegression().fit(x_entrenamiento_escalado, y_entrenamiento)
r2 = modelo.score(x_prueba_escalado, y_prueba)
# Reunimos todo lo necesario para predecir sin importar scikit-learn en producción.
modelo_json = {
    "nombre": "Regresión lineal - valor de vivienda en California",
    "variables": list(x.columns),
    "media": media.tolist(),
    "desviacion": desviacion.tolist(),
    "pesos": modelo.coef_.tolist(),
    "sesgo": float(modelo.intercept_),
    "r2_prueba": round(float(r2), 4),
    "unidad_salida": "cientos de miles de USD",
}
# Guardamos el modelo que consumirá la API FastAPI.
Path(__file__).with_name("modelo.json").write_text(
    json.dumps(modelo_json, indent=2, ensure_ascii=False), encoding="utf-8"
)
