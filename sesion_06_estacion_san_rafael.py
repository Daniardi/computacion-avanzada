"""Sesión 6 — Preparación de datos reales de CORNARE.

Consulta la estación 9 (San Rafael) entre el 1 y el 5 de septiembre de 2026.
"""

# Importamos requests para consultar la API pública de MARCO-CORNARE.
import requests
# Importamos NumPy y Pandas para analizar la serie de tiempo.
import numpy as np
import pandas as pd

# Definimos los datos personalizados de la actividad.
NOMBRE_ESTUDIANTE = "Daniel Ardila Zabala"
CODIGO_ESTACION = "9"
NOMBRE_ESTACION = "San Rafael (Aguas)"
FECHA_DESDE = "2026-09-01"
FECHA_HASTA = "2026-09-05"
CALIDAD = 1
API_BASE_URL = "https://marco.cornare.gov.co/api/v1/estaciones"


def consultar_nivel(codigo, desde, hasta, calidad=1):
    """Consulta todas las páginas del endpoint de nivel de una estación."""
    # Construimos el endpoint específico para nivel de río o quebrada.
    url = f"{API_BASE_URL}/{codigo}/nivel"
    # Enviamos el rango temporal y el filtro de calidad como parámetros.
    parametros = {"desde": desde, "hasta": hasta, "calidad": calidad}
    # Solicitamos los datos a la API con un tiempo máximo de espera.
    respuesta = requests.get(url, params=parametros, timeout=30, verify=False)
    # Detenemos la ejecución si la API responde con un error HTTP.
    respuesta.raise_for_status()
    # Convertimos la primera página de JSON a diccionario Python.
    pagina = respuesta.json()
    # Acumulamos los registros de la primera página.
    registros = list(pagina.get("values", []))
    # Seguimos el enlace next hasta haber recibido todas las páginas.
    while pagina.get("next"):
        respuesta = requests.get(pagina["next"], timeout=30, verify=False)
        respuesta.raise_for_status()
        pagina = respuesta.json()
        registros.extend(pagina.get("values", []))
    # Devolvemos todas las observaciones descargadas.
    return registros


def preparar_serie(registros):
    """Convierte registros de API en una serie ordenada, regular y limpia."""
    # Construimos un DataFrame con las columnas entregadas por MARCO.
    datos = pd.DataFrame(registros)
    # Convertimos fecha y nivel a los tipos adecuados para análisis temporal.
    datos["fecha"] = pd.to_datetime(datos["fecha"], errors="coerce", utc=True)
    datos["nivel"] = pd.to_numeric(datos["nivel"], errors="coerce")
    # Ordenamos cronológicamente y eliminamos fechas inválidas.
    datos = datos.dropna(subset=["fecha"]).sort_values("fecha").drop_duplicates("fecha")
    # Calculamos la frecuencia habitual de reporte de la estación.
    frecuencia = datos["fecha"].diff().dropna().mode().iloc[0]
    # Reindexamos para revelar huecos que no aparecían como NaN explícitos.
    rango = pd.date_range(datos["fecha"].min(), datos["fecha"].max(), freq=frecuencia)
    regular = datos.set_index("fecha").reindex(rango)
    # Contamos las lecturas ausentes antes de imputarlas.
    huecos = int(regular["nivel"].isna().sum())
    # Interpolamos según tiempo y completamos extremos si quedaron vacíos.
    regular["nivel"] = regular["nivel"].interpolate(method="time").ffill().bfill()
    # Volvemos a convertir el índice temporal en una columna.
    limpio = regular.reset_index().rename(columns={"index": "fecha"})
    # Entregamos la serie limpia, frecuencia y huecos originales.
    return datos.reset_index(drop=True), limpio, frecuencia, huecos


def detectar_outliers(serie, multiplicador=1.5):
    """Combina IQR y la regla física de que un nivel no puede ser negativo."""
    # Calculamos los cuartiles necesarios para el rango intercuartílico.
    q1, q3 = serie.quantile(0.25), serie.quantile(0.75)
    # Calculamos límites estadísticos configurables.
    iqr = q3 - q1
    inferior, superior = q1 - multiplicador * iqr, q3 + multiplicador * iqr
    # Marcamos anomalías estadísticas y valores físicamente imposibles.
    return (serie < inferior) | (serie > superior) | (serie < 0), inferior, superior


if __name__ == "__main__":
    # Descargamos los registros reales de la estación seleccionada.
    registros = consultar_nivel(CODIGO_ESTACION, FECHA_DESDE, FECHA_HASTA, CALIDAD)
    # Limpiamos y regularizamos la serie temporal descargada.
    crudos, limpios, frecuencia, huecos = preparar_serie(registros)
    # Detectamos anomalías antes de construir los conjuntos de modelado.
    mascara, limite_inf, limite_sup = detectar_outliers(limpios["nivel"])
    sin_outliers = limpios.loc[~mascara].copy()
    # Aplicamos el split cronológico 70/15/15.
    corte_train, corte_val = int(len(sin_outliers) * 0.70), int(len(sin_outliers) * 0.85)
    train = sin_outliers.iloc[:corte_train]
    validacion = sin_outliers.iloc[corte_train:corte_val]
    test = sin_outliers.iloc[corte_val:]
    # Calculamos un ICD simple con completitud y validez de las observaciones.
    completitud = 100 * (1 - huecos / len(limpios))
    validez = 100 * (1 - mascara.mean())
    icd = (completitud + validez) / 2
    # Imprimimos la evidencia principal de la consulta individual.
    print(f"Estudiante: {NOMBRE_ESTUDIANTE}")
    print(f"Estación: {CODIGO_ESTACION} — {NOMBRE_ESTACION}")
    print(f"Periodo: {FECHA_DESDE} a {FECHA_HASTA}")
    print(f"Lecturas crudas: {len(crudos)} | Huecos: {huecos} | Outliers: {mascara.sum()}")
    print(f"IQR: [{limite_inf:.2f}, {limite_sup:.2f}] | ICD: {icd:.2f}/100")
    print(f"Train={len(train)} | Validation={len(validacion)} | Test={len(test)}")
