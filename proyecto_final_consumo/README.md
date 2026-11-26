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
3. En el selector de configuración puedes elegir **Proyecto final - FastAPI y Docker**. La configuración predeterminada **Computación Avanzada - Apps y Proyecto Final** también está preparada con Python y las dependencias requeridas.
4. Espera a que termine la creación. Se abrirán automáticamente este README y `app/main.py`.

Las configuraciones están en `.devcontainer/devcontainer.json` y `.devcontainer/final-project/devcontainer.json`. GitHub permite elegir entre varias configuraciones de dev container al crear un Codespace; ambas son compatibles con el proyecto final.

### 2.2 Ejecutar la aplicación en Codespaces

En la terminal integrada del Codespace ejecutar:

```bash
cd proyecto_final_consumo
export DEMO_MODE=true
python scripts/crear_modelo_demo.py
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

En la pestaña **PORTS** aparecerá el puerto `8000`. Presiona el icono de abrir en navegador; esa URL reemplaza a `localhost` durante la sustentación. Mantén su visibilidad en **Private**, pues al estar conectado a tu cuenta podrás abrirla desde el computador de la universidad sin exponer el proyecto públicamente.

Después abre en la URL reenviada las rutas `/`, `/docs` y `/api/salud`. No se debe escribir `localhost:8000` directamente en el navegador del computador de la universidad: se debe usar la URL que muestra la pestaña **PORTS** de Codespaces.

### 2.3 Evidencia Docker en GitHub Actions

El repositorio valida Docker en la nube mediante el flujo **Verificar Docker del proyecto final**. GitHub Actions crea un servidor temporal, construye la imagen, inicia el contenedor, consulta `/api/salud` y `/api/prediccion`, muestra los registros y elimina el contenedor.

Para mostrarlo al profesor:

1. En GitHub abre la pestaña **Actions**.
2. Selecciona **Verificar Docker del proyecto final**.
3. Abre la ejecución con marca verde.
4. Muestra los pasos **Construir imagen Docker**, **Iniciar contenedor** y **Verificar API dentro del contenedor**.

También se puede iniciar manualmente con el botón **Run workflow**. Este flujo trabaja con `DEMO_MODE=true`, por lo cual no expone secretos de InfluxDB.

### 2.4 Crear y configurar InfluxDB Cloud Serverless

Las cuentas nuevas de InfluxDB Cloud usan Cloud Serverless v3. Esta aplicación es compatible con esa versión y con la API v2 clásica de la guía original.

1. Abre `https://cloud2.influxdata.com/` y crea una cuenta gratuita.
2. En la consola, crea un bucket o base de datos llamado `computacion_avanzada`.
3. Crea un token con permisos de lectura y escritura para ese bucket. La escritura solo se necesita si se cargan los datos demo; para datos de un sensor real basta lectura.
4. Conserva el token en un lugar seguro: no se puede volver a ver su valor completo después de crearlo.

Para una cuenta nueva, configura estos valores en GitHub Codespaces secrets:

```text
INFLUX_VERSION=3
INFLUX_URL=<URL de la instancia Cloud Serverless>
INFLUX_TOKEN=<token privado>
INFLUX_BUCKET=computacion_avanzada
INFLUX_MEASUREMENT=sensores
INFLUX_FIELD=temperatura
```

### 2.5 Secretos para la conexión real

Antes de usar InfluxDB real, crea secretos de Codespaces con los nombres `INFLUX_VERSION`, `INFLUX_URL`, `INFLUX_TOKEN`, `INFLUX_BUCKET`, `INFLUX_MEASUREMENT` e `INFLUX_FIELD`. Para una instancia v2 clásica agrega también `INFLUX_ORG`. Se agregan desde la configuración de GitHub en **Codespaces secrets** y se autorizan para este repositorio. Los secretos aparecen como variables de entorno dentro del Codespace, pero no se guardan en Git ni se muestran en la terminal.

Para una primera demostración presencial usa el modo demo. Luego, cuando el modelo esté entrenado con datos reales, se ejecuta la API sin `DEMO_MODE=true` y con los secretos definidos.

### 2.6 Cargar datos demo o entrenar con la serie real

Si todavía no existe un sensor real, se puede cargar una serie sintética identificada como **DEMO** en InfluxDB. No debe presentarse como medición física real:

```bash
cd proyecto_final_consumo
python scripts/cargar_demo_influx3.py
```

Si se dispone de una serie real, no ejecutar el script anterior y continuar directamente con el entrenamiento.

Con los secretos ya configurados y con `DEMO_MODE` ausente o en `false`, ejecutar:

```bash
cd proyecto_final_consumo
unset DEMO_MODE
python scripts/entrenar_sarima.py --historial-horas 720 --horizonte-prueba 24
```

El script descarga la historia desde InfluxDB, separa las últimas 24 horas para validación cronológica, informa MAE y RMSE, y guarda `models/sarima_config.json`. El archivo contiene parámetros y métricas, pero no secretos. Para usar el modelo nuevo desde Codespaces, ejecutar:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
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
6. **Docker (45 segundos).** Abrir la ejecución verde de **Verificar Docker del proyecto final** en GitHub Actions. Mostrar que construye la imagen, inicia el contenedor y consulta la API. Concluir: la imagen permite reproducir el servicio sin instalar manualmente cada dependencia.
7. **Seguridad (15 segundos).** “Los secretos se cargan como variables de entorno y `.env` está excluido de Git. Por eso no expongo el token en la demostración.”

## 8. Relación con las demás aplicaciones

El portafolio Streamlit reúne las actividades previas de la asignatura. Este proyecto final es distinto: utiliza **FastAPI y Docker**, por eso se demuestra desde el puerto privado de Codespaces y con la validación Docker de GitHub Actions, no como una aplicación Streamlit adicional.

## 9. Solución rápida de problemas

| Situación | Acción |
| --- | --- |
| `docker` no se reconoce o no conecta | Instalar/abrir Docker Desktop y confirmar con `docker info`. |
| Docker no está disponible en Codespaces | Ejecutar la API directamente con Uvicorn en Codespaces; la construcción Docker se valida en GitHub Actions. |
| Puerto 8000 ocupado | Detener el servidor anterior o cambiar ambos puertos, por ejemplo `-p 8001:8000`, y abrir `http://127.0.0.1:8001`. |
| La API indica que no hay modelo | Ejecutar `python scripts/crear_modelo_demo.py` para demo, o guardar el JSON entrenado para datos reales. |
| Error de credenciales InfluxDB | Confirmar URL, token, organización, bucket, measurement y field; nunca publicar esos valores. |
| La gráfica muestra error | Abrir `/api/salud` y `/docs`; después revisar `docker logs pronostico-demo` o la consola de Uvicorn. |

## 10. Evidencias a entregar

- Repositorio con código comentado y este README.
- Captura de la interfaz y de `/docs`.
- Captura de la ejecución verde de GitHub Actions con los pasos de construcción y prueba del contenedor.
- Archivo `models/sarima_config.json` obtenido del entrenamiento real, si la entrega exige datos reales.
- Video de máximo cinco minutos siguiendo el guion anterior, si el profesor lo solicita.
