# Actividades de Computación Avanzada

## Sesión 2 — Vectores y matrices

`sesion_02_vectores_matrices.py` contiene el paso a paso de la guía y las soluciones de los tres ejercicios propuestos. Cada bloque de código está comentado en español.

`streamlit_app.py` convierte la actividad en una aplicación interactiva para desplegar en Streamlit Community Cloud.

## Sesión 3 — Cálculo aplicado y gradiente

`sesion_03_calculo_gradiente.py` desarrolla derivadas, gradiente, descenso de gradiente y el ajuste de un modelo de consumo energético. `app_gradiente.py` es la aplicación interactiva para desplegar esta sesión en Streamlit.

Para ejecutarlo:

```powershell
py -m pip install -r requirements.txt
py sesion_02_vectores_matrices.py
```

Para ejecutar la aplicación web localmente:

```powershell
py -m streamlit run streamlit_app.py
```

Para desplegar la Sesión 3 en Streamlit Community Cloud, usa `app_gradiente.py` como archivo principal.

## Sesión 4 — Lógica, Big-O y vectorización

`sesion_04_logica_big_o_vectorizacion.py` contiene el desarrollo comentado y la solución del reto con la condición de fin de semana. `app_vectorizacion.py` permite comparar interactivamente la lógica con loops y con NumPy.

Para desplegar la Sesión 4 en Streamlit Community Cloud, usa `app_vectorizacion.py` como archivo principal.

## Sesión 5 — Preparación de datos

`sesion_05_preparacion_datos.py` desarrolla el flujo de preparación con sensores IoT. `app_preparacion_datos.py` contiene las cinco páginas interactivas solicitadas. Las respuestas de la actividad están en `respuestas_sesion_05.md`.

Para desplegar la Sesión 5 en Streamlit Community Cloud, usa `app_preparacion_datos.py` como archivo principal.

## Sesión 6 — Aplicación de preparación de datos reales

`sesion_06_estacion_san_rafael.py` consulta y prepara datos reales de la estación 9, San Rafael (Aguas), para Daniel Ardila Zabala. `app_estacion_san_rafael.py` muestra nivel, outliers, ICD, estadísticas y split cronológico. La evidencia está en `evidencia_sesion_06.md`.

Para desplegar la Sesión 6 en Streamlit Community Cloud, usa `app_estacion_san_rafael.py` como archivo principal.

## Sesión 7 — Regresión lineal

`sesion_07_regresion_lineal.py` desarrolla regresión simple, múltiple, descenso de gradiente y métricas de evaluación. `app_regresion_lineal.py` permite variar α, iteraciones y variables predictoras. Las respuestas de práctica están en `respuestas_sesion_07.md`.

Para desplegar la Sesión 7 en Streamlit Community Cloud, usa `app_regresion_lineal.py` como archivo principal.

## Sesión 8 — Series de tiempo

`sesion_08_series_tiempo.py` desarrolla ventanas deslizantes y pronósticos clásicos. `app_series_tiempo.py` compara media móvil, Holt-Winters y ARIMA. Las respuestas están en `respuestas_sesion_08.md`.

Para desplegar la Sesión 8 en Streamlit Community Cloud, usa `app_series_tiempo.py` como archivo principal.

## Sesión 10 — IoT: captura y procesamiento

`sesion_10_iot_sensacion_termica.py` reproduce el pipeline de preparación y regresión. `app_iot_sensacion_termica.py` permite cargar un CSV IoT o usar datos DHT22 de demostración, analizar humedad y temperatura, y predecir la sensación térmica. Las respuestas están en `respuestas_sesion_10.md`.

Para desplegar la Sesión 10 en Streamlit Community Cloud, usa `app_iot_sensacion_termica.py` como archivo principal.
## Sesión 11: regresión logística

- `sesion_11_regresion_logistica.py`: desarrollo comentado de la práctica de clasificación de lluvia.
- `app_regresion_logistica.py`: aplicación Streamlit interactiva para variar el umbral y las variables.
- `respuestas_sesion_11.md`: respuestas razonadas de la actividad.

## Sesión 12: analítica y visualización con PCA

- `sesion_12_pca_energia.py`: desarrollo comentado de visualización, vectores propios y PCA.
- `app_pca_energia.py`: aplicación Streamlit para explorar perfiles diarios de consumo energético.
- `respuestas_sesion_12.md`: respuestas a las preguntas de reflexión de la actividad.

## Sesión 13: KNN y fertilidad de suelos

- `sesion_13_knn_fertilidad_suelos.py`: desarrollo comentado del clasificador KNN.
- `app_knn_fertilidad_suelos.py`: aplicación Streamlit para clasificar una muestra de suelo.
- `respuestas_sesion_13.md`: respuestas de las preguntas de la guía.

## Portafolio

- `app_portafolio.py`: página central con enlaces a todas las aplicaciones desplegadas.
