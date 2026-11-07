"""API FastAPI para desplegar un estimador de valor de vivienda."""

# Importamos JSON y rutas para cargar el modelo junto al archivo de la API.
import json
from pathlib import Path

# Importamos FastAPI, respuestas HTML y validación de datos de entrada.
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

# Ubicamos la carpeta actual para que el despliegue encuentre sus archivos.
CARPETA = Path(__file__).parent
# Cargamos pesos, escalas y sesgo exportados en formato JSON.
MODELO = json.loads((CARPETA / "modelo.json").read_text(encoding="utf-8"))

# Creamos la aplicación y sus metadatos visibles en la documentación automática.
app = FastAPI(
    title="Estimador de valor de vivienda",
    description="Modelo de regresión lineal exportado a JSON para despliegue.",
    version="1.0.0",
)


class Vivienda(BaseModel):
    """Define y valida las ocho variables requeridas por el modelo."""

    # Cada atributo corresponde a una variable de California Housing.
    MedInc: float = Field(..., ge=0, description="Ingreso medio en decenas de miles de USD")
    HouseAge: float = Field(..., ge=0, description="Edad media de viviendas en años")
    AveRooms: float = Field(..., ge=0, description="Habitaciones promedio por vivienda")
    AveBedrms: float = Field(..., ge=0, description="Dormitorios promedio por vivienda")
    Population: float = Field(..., ge=0, description="Población del sector")
    AveOccup: float = Field(..., gt=0, description="Personas promedio por hogar")
    Latitude: float = Field(..., ge=30, le=45, description="Latitud de California")
    Longitude: float = Field(..., ge=-125, le=-110, description="Longitud de California")


def predecir(datos):
    """Calcula la ecuación lineal usando Python puro y el modelo exportado."""
    # Iniciamos la predicción en el sesgo aprendido durante el entrenamiento.
    prediccion = MODELO["sesgo"]
    # Estandarizamos cada valor con sus parámetros y sumamos su aporte ponderado.
    for nombre, media, desviacion, peso in zip(
        MODELO["variables"], MODELO["media"], MODELO["desviacion"], MODELO["pesos"]
    ):
        prediccion += peso * (datos[nombre] - media) / desviacion
    # Devolvemos la predicción en cientos de miles de dólares.
    return max(prediccion, 0.0)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def pagina_principal():
    """Entrega la página HTML que contiene el formulario de predicción."""
    # Leemos el archivo estático para mantener interfaz y API separadas.
    return (CARPETA / "index.html").read_text(encoding="utf-8")


@app.get("/modelo")
def informacion_modelo():
    """Expone información pública del modelo sin revelar detalles innecesarios."""
    # Devolvemos metadatos útiles para la interfaz y la persona usuaria.
    return {
        "nombre": MODELO["nombre"],
        "variables": MODELO["variables"],
        "r2_prueba": MODELO["r2_prueba"],
        "unidad_salida": MODELO["unidad_salida"],
    }


@app.post("/predict")
def estimar_vivienda(vivienda: Vivienda):
    """Recibe una vivienda validada y responde su valor estimado."""
    # Convertimos el objeto validado en diccionario para recorrer sus variables.
    datos = vivienda.model_dump()
    # Aplicamos el modelo exportado y redondeamos las dos unidades de salida.
    valor = predecir(datos)
    return {
        "prediccion": round(valor, 4),
        "valor_usd": round(valor * 100_000),
        "nota": "Estimación didáctica basada en California Housing, censo de 1990.",
    }
