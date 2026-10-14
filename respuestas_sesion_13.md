# Sesión 13: KNN y fertilidad de suelos

**Estudiante:** Daniel Ardila Zabala  
**Caso de estudio:** clasificación didáctica de fertilidad de suelos.

1. Una muestra tomada en bloques aleatorios representa zonas distintas del conjunto de datos. Usar solo los primeros 5.000 registros puede concentrar observaciones ordenadas de forma similar y producir una muestra sesgada.

2. Con k=1, una muestra queda determinada por un solo vecino y el modelo es muy sensible al ruido. Con k=25 la decisión se suaviza por la votación de más vecinos. Una muestra en la frontera entre clases es difícil porque sus vecinos cercanos pueden pertenecer a categorías diferentes.

3. Sin escalado, el fósforo o el hierro, medidos en valores mucho mayores, dominan la distancia euclidiana. La estandarización convierte cada variable a una escala comparable y evita que una unidad de medida decida el resultado.

4. Con k=1 el desempeño en entrenamiento puede ser perfecto porque cada registro es su propio vecino. El mejor k se elige por validación cruzada; no debe ser el máximo porque demasiados vecinos suavizan diferencias reales y producen subajuste.

5. Las diferencias entre distancia euclidiana, Manhattan y pesos pueden ser pequeñas. En ese caso, el mayor esfuerzo debe dedicarse a limpiar los datos, escalar las variables y elegir k, antes que a probar muchas variantes de distancia.

6. Un resultado demasiado alto obliga a preguntar de dónde salió la etiqueta. Si se calculó con materia orgánica, fósforo y potasio, usarlos como entradas filtra la respuesta. CICE también se excluye porque incorpora potasio en su cálculo, lo cual es una fuga indirecta.

7. Añadir variables aleatorias perjudica KNN porque todas participan en la distancia y diluyen la cercanía útil. Antes de usar cien variables conviene seleccionar características, eliminar ruido y validar el desempeño.

8. La clase media puede confundirse más por estar cerca de los umbrales de baja y alta. KNN debe superar la línea base, pero un diagnóstico real de campo requeriría más variables, datos representativos y validación agronómica.

9. Los datos proceden de personas que pagaron un análisis, no de una muestra aleatoria nacional. Esto introduce sesgo de selección: las observaciones pueden concentrarse en regiones, cultivos o predios que requieren análisis.

10. A un agricultor le explicaría que la clasificación baja se debe a que, después de comparar las características de su suelo con muestras analizadas parecidas, la mayoría de los vecinos cercanos correspondió a fertilidad baja. Es una orientación, no una recomendación de fertilización definitiva.
