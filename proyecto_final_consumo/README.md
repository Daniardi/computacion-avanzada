# Proyecto final: pronóstico de temperatura

Proyecto de **Daniel Ardila Zabala** para Computación Avanzada. La solución consulta una serie de temperatura de sensores IoT, reconstruye un modelo SARIMA y muestra el histórico junto con un pronóstico e intervalo de confianza.

Este documento es también la guía de sustentación presencial. Incluye comandos para GitHub Codespaces (recomendado para la presentación) y PowerShell en Windows.

## 1. Arquitectura que se debe explicar

```text
Sensores IoT -> InfluxDB -> app/influx.py -> modelo SARIMA -> API FastAPI -> interfaz web
                                              ^
                                              |
                                      models/sarima_config.json
```

- **InfluxDB:** conserva las mediciones de temperatura.
- **`app/influx.py`:** consulta, agrupa los datos por hora y completa huecos cortos.
- **`models/sarima_config.json`:** guarda los órdenes y parámetros del SARIMA; no se usa `pickle`, lo que hace el artefacto más portable.
- **FastAPI:** publica el servicio web y la documentación automática.
- **Frontend:** consume la API y grafica histórico, pronóstico e intervalo de confianza en horario de Colombia.
- **Docker:** empaqueta exactamente el mismo servicio para que pueda ejecutarse en otra máquina.

La serie objetivo por defecto usa `measurement=sensores` y `field=temperatura`. Si InfluxDB usa otros nombres, se cambian con variables de entorno, nunca directamente en el código.

## 2. Ruta recomendada: presentación desde GitHub Codespaces

Esta opción evita instalar Python o Docker en el computador de la universidad. El proyecto se ejecuta en una máquina virtual de GitHub y el navegador solo abre una URL temporal y privada.

### 2.1 Preparación única desde tu cuenta de GitHub

1. Sube los cambios del repositorio con `git push`.
2. En GitHub abre el repositorio, selecciona **Code**, luego **Codespaces** y elige **Create codespace on master**.
3. En el selector de configuración elige **Proyecto final - FastAPI y Docker**. Esta configuración instala Python, las dependencias y acceso a Docker dentro del Codespace.
4. Espera a que termine la creación. Se abrirán automáticamente este README y `app/main.py`.

La configuración está en `.devcontainer/final-project/devcontainer.json`. GitHub permite elegir entre varias configuraciones de dev container al crear un Codespace, por lo que las prácticas de Streamlit permanecen separadas del proyecto final.

### 2.2 Ejecutar la demostración Docker en Codespaces

En la terminal integrada del Codespace ejecutar:

```bash
cd proyecto_final_consumo
export DEMO_MODE=true
python scripts/crear_modelo_demo.py
docker build -t pronostico-temperatura:1.0 .
docker run --name pronostico-demo -d -p 8000:8000 -e DEMO_MODE=true pronostico-temperatura:1.0
docker ps
```

En la pestaña **PORTS** aparecerá el puerto `8000`. Presiona el icono de abrir en navegador; esa URL reemplaza a `localhost` durante la sustentación. Mantén su visibilidad en **Private**, pues al estar conectado a tu cuenta podrás abrirla desde el computador de la universidad sin exponer el proyecto públicamente.

Para la evidencia Docker, en la misma terminal ejecutar:

```bash
docker logs pronostico-demo
docker exec pronostico-demo hostname
```

Después abre en la URL reenviada las rutas `/`, `/docs` y `/api/salud`. No se debe escribir `localhost:8000` directamente en el navegador del computador de la universidad: se debe usar la URL que muestra la pestaña **PORTS** de Codespaces.

### 2.3 Secretos para la conexión real

Antes de usar InfluxDB real, crea secretos de Codespaces con los nombres `INFLUX_URL`, `INFLUX_TOKEN`, `INFLUX_ORG`, `INFLUX_BUCKET`, `INFLUX_MEASUREMENT` e `INFLUX_FIELD`. Se agregan desde la configuración de GitHub en **Codespaces secrets** y se autorizan para este repositorio. Los secretos aparecen como variables de entorno dentro del Codespace, pero no se guardan en Git ni se muestran en la terminal.

Para una primera demostración presencial usa el modo demo. Luego, cuando el modelo esté entrenado con datos reales, se ejecuta Docker sin `-e DEMO_MODE=true` y con los secretos definidos.

### 2.4 Entrenar con la serie real dentro de Codespaces

Con los secretos ya configurados y con `DEMO_MODE` ausente o en `false`, ejecutar:

```bash
cd proyecto_final_consumo
unset DEMO_MODE
python scripts/entrenar_sarima.py --historial-horas 720 --horizonte-prueba 24
```

El script descarga la historia desde InfluxDB, separa las últimas 24 horas para validación cronológica, informa MAE y RMSE, y guarda `models/sarima_config.json`. El archivo contiene parámetros y métricas, pero no secretos. Para usar el modelo nuevo, reconstruir y ejecutar la imagen:

```bash
docker rm -f pronostico-demo 2>/dev/null || true
docker build -t pronostico-temperatura:1.0 .
docker run --name pronostico-real -d -p 8000:8000 -e INFLUX_URL -e INFLUX_TOKEN -e INFLUX_ORG -e INFLUX_BUCKET -e INFLUX_MEASUREMENT -e INFLUX_FIELD pronostico-temperatura:1.0
```

## 3. Requisitos antes de la sustentación local

1. Tener instalado Python 3.12 o superior y Docker Desktop.
2. Abrir Docker Desktop y esperar el mensaje de que el motor está ejecutándose.
3. Abrir PowerShell dentro de la carpeta `proyecto_final_consumo`.
4. Comprobar las herramientas:

```powershell
python --version
docker --version
docker info
```

Si el equipo reconoce `py` en lugar de `python`, se puede sustituir `python` por `py` en todos los comandos siguientes.

## 4. Demostración segura sin credenciales: modo demo

Este modo es apropiado para comprobar toda la arquitectura cuando no hay conexión a InfluxDB. Genera una serie didáctica de temperatura; debe presentarse como demostración, no como dato real.

Desde esta carpeta, ejecutar una sola vez:

```powershell
python -m pip install -r requirements.txt
$env:DEMO_MODE = "true"
python scripts/crear_modelo_demo.py
```

El último comando crea `models/sarima_config.json`. Ese archivo debe existir antes de construir la imagen Docker, porque Docker lo copia dentro del contenedor.

### 4.1 Ejecutar sin Docker

```powershell
$env:DEMO_MODE = "true"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Abrir estas rutas en el navegador:

- `http://127.0.0.1:8000/` muestra la interfaz.
- `http://127.0.0.1:8000/docs` muestra la documentación automática de FastAPI.
- `http://127.0.0.1:8000/api/salud` muestra estado del servicio sin revelar secretos.

En la interfaz, variar las horas a pronosticar y el intervalo de confianza. Luego detener el servidor con `Ctrl + C`.

## 5. Demostración con Docker en el equipo local

Primero confirmar que Docker Desktop está abierto y que el modelo demo fue creado en el paso anterior. En la carpeta del proyecto ejecutar:

```powershell
docker build -t pronostico-temperatura:1.0 .
docker images pronostico-temperatura:1.0
docker run --name pronostico-demo -d -p 8000:8000 -e DEMO_MODE=true pronostico-temperatura:1.0
docker ps
```

Abrir de nuevo `http://127.0.0.1:8000/` y `http://127.0.0.1:8000/docs`. La interfaz será la misma; la diferencia es que ahora FastAPI se ejecuta dentro del contenedor.

Para evidenciar que el proceso pertenece al contenedor:

```powershell
docker logs pronostico-demo
docker exec pronostico-demo hostname
```

El campo `atendido_por` de `http://127.0.0.1:8000/api/salud` también coincide con ese nombre de contenedor.

Al terminar, detener y eliminar solo el contenedor de demostración:

```powershell
docker stop pronostico-demo
docker rm pronostico-demo
```

## 6. Conexión real con InfluxDB

No copiar tokens en el repositorio, el README, capturas ni diapositivas. Para trabajo local, copiar `.env.example` como `.env` y completar únicamente en ese archivo privado:

```powershell
Copy-Item .env.example .env
```

Variables requeridas:

```text
INFLUX_URL=
INFLUX_TOKEN=
INFLUX_ORG=
INFLUX_BUCKET=
INFLUX_MEASUREMENT=sensores
INFLUX_FIELD=temperatura
DEMO_MODE=false
```

Después se debe entrenar el SARIMA con la serie real y guardar el resultado en `models/sarima_config.json`. Se puede usar el cuaderno de la asignatura o el script `scripts/entrenar_sarima.py`, que además calcula MAE y RMSE con una validación temporal. Con ello se ejecuta el mismo comando de Uvicorn, pero sin definir `DEMO_MODE=true`.

Para Docker con datos reales, definir las variables solo en la sesión actual de PowerShell y arrancar el contenedor:

```powershell
$env:INFLUX_URL = "https://..."
$env:INFLUX_TOKEN = "token-privado"
$env:INFLUX_ORG = "organizacion"
$env:INFLUX_BUCKET = "bucket"
$env:INFLUX_MEASUREMENT = "sensores"
$env:INFLUX_FIELD = "temperatura"
docker run --name pronostico-real -d -p 8000:8000 -e INFLUX_URL -e INFLUX_TOKEN -e INFLUX_ORG -e INFLUX_BUCKET -e INFLUX_MEASUREMENT -e INFLUX_FIELD pronostico-temperatura:1.0
```

Docker recibe los secretos en tiempo de ejecución con `-e`; no quedan incluidos en la imagen.

## 7. Guion recomendado para la explicación presencial

1. **Problema (20 segundos).** “El proyecto pronostica las próximas horas de temperatura a partir de mediciones IoT. El objetivo es transformar una serie almacenada en InfluxDB en una predicción interpretable.”
2. **Datos (30 segundos).** Mostrar `app/influx.py` y explicar la consulta, el promedio por hora y el tratamiento de huecos. Aclarar cuál es el measurement y field real utilizados.
3. **Modelo (30 segundos).** Mostrar `models/sarima_config.json` y explicar que SARIMA incorpora dependencia temporal y estacionalidad diaria. El JSON contiene parámetros, no credenciales.
4. **API (30 segundos).** Abrir `/docs`, ejecutar `GET /api/salud` y `GET /api/prediccion`. Explicar que FastAPI separa la lógica de datos/modelo de la interfaz.
5. **Interfaz (30 segundos).** Abrir `/`, cambiar el horizonte y el nivel de confianza. Señalar histórico, línea de pronóstico y límites del intervalo.
6. **Docker (45 segundos).** Ejecutar `docker ps`, `docker logs pronostico-demo` y abrir la misma interfaz. Concluir: la imagen permite reproducir el servicio sin instalar manualmente cada dependencia.
7. **Seguridad (15 segundos).** “Los secretos se cargan como variables de entorno y `.env` está excluido de Git. Por eso no expongo el token en la demostración.”

## 8. Relación con las demás aplicaciones

El portafolio Streamlit reúne las actividades previas de la asignatura. Este proyecto final es distinto: utiliza **FastAPI y Docker**, por eso se demuestra en `http://127.0.0.1:8000/` y no se despliega como una aplicación Streamlit adicional.

## 9. Solución rápida de problemas

| Situación | Acción |
| --- | --- |
| `docker` no se reconoce o no conecta | Instalar/abrir Docker Desktop y confirmar con `docker info`. |
| Puerto 8000 ocupado | Detener el servidor anterior o cambiar ambos puertos, por ejemplo `-p 8001:8000`, y abrir `http://127.0.0.1:8001`. |
| La API indica que no hay modelo | Ejecutar `python scripts/crear_modelo_demo.py` para demo, o guardar el JSON entrenado para datos reales. |
| Error de credenciales InfluxDB | Confirmar URL, token, organización, bucket, measurement y field; nunca publicar esos valores. |
| La gráfica muestra error | Abrir `/api/salud` y `/docs`; después revisar `docker logs pronostico-demo` o la consola de Uvicorn. |

## 10. Evidencias a entregar

- Repositorio con código comentado y este README.
- Captura de la interfaz y de `/docs`.
- Captura de `docker ps` y de la interfaz funcionando desde el contenedor.
- Archivo `models/sarima_config.json` obtenido del entrenamiento real, si la entrega exige datos reales.
- Video de máximo cinco minutos siguiendo el guion anterior, si el profesor lo solicita.
