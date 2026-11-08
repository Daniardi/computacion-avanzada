"""API FastAPI del proyecto final de pronóstico de temperatura."""

# Importamos hostname, FastAPI, respuestas estáticas y consulta de parámetros.
import socket
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Importamos módulos propios para configuración, datos y modelo.
from . import config, influx
from .model import cargar_modelo

# Cargamos el modelo una vez al iniciar el proceso del servidor.
MODELO = cargar_modelo(config.MODEL_PATH)

# Creamos la API y habilitamos documentación automática en la ruta docs.
app = FastAPI(title="Pronóstico de temperatura con SARIMA", version="1.0.0")

# Montamos los recursos del frontend para que el navegador pueda abrirlos.
FRONTEND = config.BASE_DIR / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND), name="static")


def verificar_servicio():
    """Comprueba que existe modelo y que la fuente real o demo está disponible."""
    # Informamos si aún falta ejecutar el entrenamiento en Colab.
    if MODELO is None:
        raise HTTPException(503, "No hay modelo cargado. Ejecute crear_modelo_demo.py o suba sarima_config.json.")
    # Exigimos credenciales solo cuando no se está usando modo de demostración.
    if not config.DEMO_MODE and not config.influx_configurado():
        raise HTTPException(503, "Faltan secretos de InfluxDB. Configure .env o Codespaces secrets.")


@app.get("/", include_in_schema=False)
def inicio():
    """Entrega la interfaz web del pronóstico."""
    # Enviamos el archivo HTML principal.
    return FileResponse(FRONTEND / "index.html")


@app.get("/api/salud")
def salud():
    """Devuelve estado del contenedor, fuente y modelo sin exponer secretos."""
    # Permitimos verificar modo demo y origen de la respuesta.
    return {
        "estado": "ok",
        "atendido_por": socket.gethostname(),
        "modo_demo": config.DEMO_MODE,
        "modelo_cargado": MODELO is not None,
        "influx_configurado": config.influx_configurado(),
        "measurement": config.INFLUX_MEASUREMENT,
        "field": config.INFLUX_FIELD,
    }


@app.get("/api/prediccion")
def prediccion(
    horas: int = Query(12, ge=1, le=config.MAX_HORAS_PREDICCION),
    historia: int = Query(48, ge=24, le=720),
    confianza: float = Query(0.95, gt=0.5, lt=1.0),
):
    """Entrega histórico y pronóstico para que el frontend los grafique."""
    # Verificamos los recursos necesarios antes de consultar o calcular.
    verificar_servicio()
    try:
        # Pedimos suficiente contexto para cubrir estacionalidad diaria del SARIMA.
        serie = influx.leer_serie_horaria(max(config.HORAS_CONTEXTO, historia))
        pronostico = MODELO.pronosticar(serie, horas, confianza)
    except Exception as error:
        # Convertimos errores de datos o de modelo en una respuesta web comprensible.
        raise HTTPException(502, f"No se pudo generar el pronóstico: {error}")
    # Serializamos fechas y números para enviarlos en JSON al navegador.
    return {
        "ultima_observacion": serie.index[-1].strftime("%Y-%m-%dT%H:%M:%SZ"),
        "confianza": confianza,
        "historico": [
            {"tiempo": fecha.strftime("%Y-%m-%dT%H:%M:%SZ"), "valor": round(float(valor), 3)}
            for fecha, valor in serie.iloc[-historia:].items()
        ],
        "prediccion": [
            {
                "tiempo": fecha.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "prediccion": round(float(fila.prediccion), 3),
                "limite_inferior": round(float(fila.limite_inferior), 3),
                "limite_superior": round(float(fila.limite_superior), 3),
            }
            for fecha, fila in pronostico.iterrows()
        ],
    }
