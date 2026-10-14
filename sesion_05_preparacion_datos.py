"""Actividad de clase — Sesión 5: preparación de datos.

Ejecute este archivo con: python sesion_05_preparacion_datos.py
Cada sección reproduce el paso a paso del cuaderno oficial.
"""

# Importamos NumPy para generar datos numéricos y aplicar transformaciones.
import numpy as np
# Importamos Pandas para organizar y limpiar los datos tabulares.
import pandas as pd
# Importamos train_test_split para dividir los datos de forma aleatoria.
from sklearn.model_selection import train_test_split

# Fijamos la semilla para que el dataset sintético sea reproducible.
np.random.seed(42)


def crear_dataset(n=500):
    """Construye el dataset sintético de sensores IoT del cuaderno."""
    # Creamos marcas de tiempo separadas por treinta minutos.
    fechas = pd.date_range("2026-01-01", periods=n, freq="30min")
    # Generamos las columnas categóricas de los sensores.
    tipos = np.random.choice(["DHT22", "BMP180", "LDR"], size=n, p=[0.5, 0.3, 0.2])
    ubicaciones = np.random.choice(["invernadero_1", "patio", "bodega"], size=n)
    calidad = np.random.choice(["baja", "media", "alta"], size=n, p=[0.1, 0.3, 0.6])
    # Generamos mediciones continuas y una variable discreta.
    temperaturas = np.random.normal(24, 3, n)
    humedades = np.random.normal(60, 10, n)
    presiones = np.random.normal(1013, 5, n)
    lecturas_hora = np.random.poisson(12, n)
    # Reunimos todas las columnas en un DataFrame.
    return pd.DataFrame({
        "timestamp": fechas, "tipo_sensor": tipos, "ubicacion": ubicaciones,
        "calidad_senal": calidad, "temperatura": temperaturas, "humedad": humedades,
        "presion": presiones, "lecturas_hora": lecturas_hora,
    })


def convertir_categorias(datos):
    """Convierte texto repetitivo en categorías nominales y ordinales."""
    # Copiamos el DataFrame para no modificar los datos originales.
    resultado = datos.copy()
    # Guardamos valores repetidos como códigos internos y categorías únicas.
    resultado["tipo_sensor"] = resultado["tipo_sensor"].astype("category")
    resultado["ubicacion"] = resultado["ubicacion"].astype("category")
    # Declaramos explícitamente que calidad_senal tiene un orden natural.
    resultado["calidad_senal"] = pd.Categorical(
        resultado["calidad_senal"], categories=["baja", "media", "alta"], ordered=True
    )
    # Retornamos el DataFrame con tipos corregidos.
    return resultado


def ensuciar_datos(datos):
    """Simula lecturas faltantes y valores extremos de un sensor."""
    # Copiamos los datos para preservar la versión limpia.
    resultado = datos.copy()
    # Seleccionamos filas para simular fallas de lectura en temperatura y humedad.
    faltantes_temp = np.random.choice(resultado.index, size=int(0.05 * len(resultado)), replace=False)
    faltantes_hum = np.random.choice(resultado.index, size=int(0.04 * len(resultado)), replace=False)
    resultado.loc[faltantes_temp, "temperatura"] = np.nan
    resultado.loc[faltantes_hum, "humedad"] = np.nan
    # Insertamos mediciones físicamente inusuales como posibles errores del sensor.
    outliers = np.random.choice(resultado.index, size=6, replace=False)
    resultado.loc[outliers, "temperatura"] = np.random.choice([-40, 95, 120], size=6)
    # Entregamos la versión con problemas simulados.
    return resultado


def detectar_outliers_iqr(serie, multiplicador=1.5):
    """Detecta valores fuera del rango intercuartílico configurable."""
    # Calculamos el primer y tercer cuartil de la variable.
    q1, q3 = serie.quantile(0.25), serie.quantile(0.75)
    # El IQR describe el rango central del 50 % de las observaciones.
    iqr = q3 - q1
    # Construimos los límites inferior y superior del método IQR.
    limite_inferior = q1 - multiplicador * iqr
    limite_superior = q3 + multiplicador * iqr
    # Marcamos como outlier todo valor por fuera de dichos límites.
    mascara = (serie < limite_inferior) | (serie > limite_superior)
    # Retornamos la máscara y los límites para poder explicarlos.
    return mascara, limite_inferior, limite_superior


def normalizar_min_max(matriz):
    """Lleva cada columna numérica al intervalo [0, 1]."""
    # Hallamos los mínimos y máximos de cada característica.
    minimo, maximo = matriz.min(axis=0), matriz.max(axis=0)
    # Aplicamos la fórmula Min-Max por columnas.
    return (matriz - minimo) / (maximo - minimo)


def estandarizar_zscore(matriz):
    """Centra cada columna en media 0 y desviación estándar 1."""
    # Calculamos media y desviación por característica.
    media, desviacion = matriz.mean(axis=0), matriz.std(axis=0)
    # Aplicamos la fórmula Z-score por columnas.
    return (matriz - media) / desviacion


if __name__ == "__main__":
    # Creamos y tipamos correctamente el dataset de trabajo.
    datos = convertir_categorias(crear_dataset())
    print("1. TIPOS DE DATOS\n", datos.dtypes)

    # Simulamos problemas de calidad y los resolvemos por interpolación temporal.
    datos_sucios = ensuciar_datos(datos)
    datos_limpios = datos_sucios.sort_values("timestamp").reset_index(drop=True)
    datos_limpios[["temperatura", "humedad"]] = datos_limpios[["temperatura", "humedad"]].interpolate()
    # Detectamos los valores extremos después de completar los faltantes.
    mascara_outliers, limite_inf, limite_sup = detectar_outliers_iqr(datos_limpios["temperatura"])
    print(f"\n2. OUTLIERS\nRango IQR: [{limite_inf:.2f}, {limite_sup:.2f}] | detectados: {mascara_outliers.sum()}")

    # Quitamos outliers para construir la matriz de características limpia.
    datos_modelo = datos_limpios.loc[~mascara_outliers]
    columnas = ["temperatura", "humedad", "presion", "lecturas_hora"]
    matriz = datos_modelo[columnas].dropna().to_numpy()
    # Generamos las dos escalas explicadas en la guía.
    matriz_normalizada = normalizar_min_max(matriz)
    matriz_estandarizada = estandarizar_zscore(matriz)
    print("\n3. ESCALAMIENTO")
    print("Min-Max, mínimos y máximos:", matriz_normalizada.min(axis=0), matriz_normalizada.max(axis=0))
    print("Z-score, medias y desviaciones:", matriz_estandarizada.mean(axis=0).round(3), matriz_estandarizada.std(axis=0).round(3))

    # Creamos el split aleatorio de train, validation y test.
    train_val, test = train_test_split(matriz, test_size=0.30, random_state=42)
    train, validacion = train_test_split(train_val, test_size=0.20, random_state=42)
    print(f"\n4. SPLIT ALEATORIO\nTrain={len(train)}, Validation={len(validacion)}, Test={len(test)}")

    # Calculamos la matriz de correlación como resumen de relaciones lineales.
    print("\n5. CORRELACIÓN\n", datos_modelo[columnas].corr().round(3))
