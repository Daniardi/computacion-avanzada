# Proyecto final: arquitectura de datos y pronóstico

**Estudiante:** Daniel Ardila Zabala  
**Serie final:** temperatura medida por sensores IoT.

1. La arquitectura separa adquisición, transformación, modelo, API y visualización. InfluxDB conserva lecturas temporales; la API las regulariza por hora y el SARIMA produce el pronóstico.

2. La serie se consulta desde InfluxDB mediante secretos de entorno. El token se mantiene fuera del código, del repositorio y de la imagen Docker.

3. SARIMA se entrena en Colab con la misma frecuencia horaria que usa la API. El archivo JSON guarda órdenes y parámetros para reconstruir el modelo con observaciones recientes, sin reentrenar al consultar.

4. El frontend convierte las marcas UTC a hora de Colombia, muestra histórico, pronóstico, intervalo de confianza y un mensaje de error si la fuente no responde.

5. Docker permite ejecutar la misma aplicación en otro equipo. Las variables de InfluxDB se entregan al iniciar el contenedor con opciones -e, por lo que no quedan dentro de la imagen.

6. Antes de la entrega se debe reemplazar el modelo de demostración por sarima_config.json entrenado sobre la temperatura real, verificar /api/salud y registrar evidencia en video sin mostrar credenciales.
