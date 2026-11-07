# Sesión 17: despliegue de modelos

**Estudiante:** Daniel Ardila Zabala  
**Tema:** exportación de modelo, API FastAPI y despliegue en Vercel.

1. Un modelo entrenado puede exportarse como JSON porque para inferir solo se necesitan sus variables, medias, desviaciones, pesos y sesgo. No es necesario llevar todo el conjunto de entrenamiento.

2. Guardar la media y desviación es indispensable. La API debe aplicar exactamente la normalización usada en entrenamiento; de lo contrario, los valores de entrada quedan en otra escala y las predicciones son incorrectas.

3. Separar API y página web permite que el navegador solicite una predicción mediante POST a la ruta predict. La misma API también puede ser consumida por otra app o servicio.

4. La validación de Pydantic rechaza datos inválidos antes de llegar al modelo. Por ejemplo, una latitud fuera de California o texto donde se espera un número genera una respuesta de error clara.

5. Desplegar en Vercel transforma el proyecto del repositorio en una URL pública. Para ello se selecciona como directorio raíz la carpeta sesion_17_despliegue_modelos y se configura el proyecto desde GitHub.

6. El archivo JSON hace el despliegue más liviano: la API predice con Python puro y evita cargar herramientas de entrenamiento cuando solo se necesita inferencia.
