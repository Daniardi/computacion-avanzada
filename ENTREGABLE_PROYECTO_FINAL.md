# Entregable final: pronóstico de temperatura con IoT

**Asignatura:** Computación Avanzada  
**Estudiante:** Daniel Ardila Zabala  
**Repositorio:** [Daniardi/computacion-avanzada](https://github.com/Daniardi/computacion-avanzada)  
**Fecha:** 26 de noviembre de 2026

## 1. Resumen

Se desarrolló una aplicación web para pronosticar temperatura horaria. El proyecto integra una base de datos temporal InfluxDB Cloud, un modelo SARIMA, una API FastAPI, una interfaz web y una estrategia de despliegue reproducible con Docker.

El flujo completo se ejecutó de extremo a extremo: carga de datos en InfluxDB, entrenamiento, validación temporal, generación del modelo, consulta desde la API y visualización del pronóstico.

## 2. Objetivo

Construir un sistema que permita consultar una serie de temperatura, estimar sus próximas horas y comunicar el resultado mediante una interfaz web con histórico, pronóstico e intervalo de confianza.

## 3. Arquitectura implementada

```text
Serie de sensores -> InfluxDB Cloud -> preparación horaria -> SARIMA
                                                        |
                                                        v
Frontend web <- FastAPI <- models/sarima_config.json <- validación temporal
```

- **InfluxDB Cloud Serverless v3:** almacena la serie temporal.
- **Procesamiento:** regulariza la frecuencia a una hora y completa huecos breves.
- **Modelo SARIMA:** aprende dependencia temporal y estacionalidad diaria.
- **FastAPI:** expone la interfaz y los endpoints de salud y predicción.
- **Frontend:** presenta temperatura histórica, pronóstico e intervalo de confianza en horario de Colombia.
- **Docker:** empaqueta la API; GitHub Actions valida la imagen en la nube.

## 4. Datos utilizados

Para esta entrega se cargaron **672 observaciones horarias**, equivalentes a 28 días, en el bucket `computacion_avanzada` de InfluxDB Cloud.

Los datos son **sintéticos y están etiquetados como `origen=demo`**. Se usaron para demostrar de forma transparente el pipeline técnico completo mientras no se disponga de un sensor físico enviando mediciones. No se presentan como lecturas físicas reales.

La estructura queda lista para reemplazar esos datos por lecturas de un sensor IoT real usando el mismo measurement `sensores` y el field `temperatura`.

## 5. Modelo y resultados

Se entrenó un modelo SARIMA con validación cronológica: las últimas 24 horas se reservaron para prueba y las observaciones anteriores se usaron para el ajuste.

| Métrica | Resultado |
| --- | ---: |
| MAE | 0.3664 °C |
| RMSE | 0.4455 °C |
| Horizonte de prueba | 24 horas |
| Observaciones disponibles | 672 |

El archivo de parámetros se generó en `proyecto_final_consumo/models/sarima_config.json`. El artefacto guarda órdenes y parámetros del modelo, pero no incluye tokens ni credenciales.

## 6. API e interfaz

La aplicación ofrece las siguientes rutas:

| Ruta | Propósito |
| --- | --- |
| `/` | Interfaz web con gráfico y controles del pronóstico. |
| `/docs` | Documentación interactiva de FastAPI. |
| `/api/salud` | Estado del servicio sin exponer secretos. |
| `/api/prediccion` | Histórico y predicción con límites de confianza. |

La aplicación se ejecutó desde GitHub Codespaces y se expuso mediante el puerto privado `8000`.

## 7. Docker y validación en la nube

El archivo `proyecto_final_consumo/Dockerfile` crea una imagen basada en Python 3.12. La verificación automática está definida en `.github/workflows/verificar-docker-proyecto-final.yml`.

El flujo **Verificar Docker del proyecto final**, disponible en la pestaña [Actions del repositorio](https://github.com/Daniardi/computacion-avanzada/actions), realiza estas acciones:

1. Construye la imagen Docker.
2. Inicia el contenedor en modo demo.
3. Consulta `/api/salud`.
4. Consulta `/api/prediccion`.
5. Publica registros y elimina el contenedor temporal.

La ejecución quedó validada correctamente con marca verde en GitHub Actions.

## 8. Seguridad

Las credenciales de InfluxDB se almacenan como secretos de GitHub Codespaces. No se guardan en el código, en los commits, en el archivo Docker ni en las capturas de evidencia.

Los nombres de las variables utilizadas son:

```text
INFLUX_VERSION
INFLUX_URL
INFLUX_TOKEN
INFLUX_BUCKET
INFLUX_MEASUREMENT
INFLUX_FIELD
```

## 9. Evidencias para adjuntar

- Captura de la interfaz web en el puerto 8000.
- Captura de `/docs` con los endpoints FastAPI.
- Captura de la salida de entrenamiento con MAE y RMSE.
- Captura del bucket `computacion_avanzada` en InfluxDB Cloud, sin mostrar token.
- Captura de la ejecución verde de GitHub Actions.
- Enlace al repositorio y al README técnico.

## 10. Próximo paso

Conectar un sensor físico o una fuente histórica real a InfluxDB y volver a ejecutar `scripts/entrenar_sarima.py`. Así se actualizarán las métricas y el modelo usando observaciones reales, sin modificar API, frontend o Docker.
