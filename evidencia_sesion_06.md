# Sesión 6 — Datos hidrológicos reales

**Estudiante:** Daniel Ardila Zabala  
**Estación:** 9 — San Rafael (Aguas), San Rafael, Antioquia  
**Periodo consultado:** 2026-09-01 a 2026-09-05  
**URL de la app:** _Completar tras el despliegue en Streamlit_

## Consulta personalizada

La app consulta la API MARCO de CORNARE en el endpoint:

```text
https://marco.cornare.gov.co/api/v1/estaciones/9/nivel?desde=2026-09-01&hasta=2026-09-05&calidad=1
```

Se identificaron 5.756 registros validados para la estación y el periodo seleccionados. La aplicación calcula de forma dinámica huecos temporales, outliers, estadísticas, el máximo de nivel, split cronológico e Índice de Calidad de Datos (ICD).

## Respuestas de análisis

- Dos rangos de fechas de la misma estación pueden verse muy diferentes porque la precipitación, una crecida, una sequía o fallos de medición cambian el nivel registrado en cada periodo.
- `fecha` debe ser `datetime` para ordenar correctamente, calcular diferencias temporales, detectar huecos y agrupar datos por hora o día. Como texto, esas operaciones pueden fallar o dar resultados incorrectos.
- `interpolate(method="time")` usa la distancia temporal real; la interpolación lineal por posición asumiría que todas las filas están igualmente separadas, incluso cuando hay huecos de distinta duración.
- Un hueco de pocos minutos puede interpolarse con prudencia. Para huecos de horas o días se debe revisar la causa, usar información externa o recortar el tramo, porque el nivel pudo cambiar mucho durante ese intervalo.
- Un pico IQR no debe eliminarse automáticamente: una crecida real es precisamente un evento hidrológico importante. Conviene contrastarlo con lluvia, estaciones cercanas, metadatos y el estado del sensor.
- El test debe ser el tramo más reciente para evaluar el modelo en condiciones parecidas a una predicción real: entrenar con pasado y predecir futuro evita fuga de información.
- Un periodo de solo dos días suele ser insuficiente para una división train/validation/test robusta; conviene ampliar el rango temporal o usar validación temporal acumulativa.
