# Sesión 11: de la regresión lineal a la logística

**Estudiante:** Daniel Ardila Zabala  
**Actividad:** clasificación de lluvia con regresión logística

1. Al eliminar la velocidad del viento, la exactitud, precisión y recall pueden cambiar levemente. En estos datos la humedad concentra la mayor señal para predecir lluvia, por lo que la pérdida suele ser pequeña. La comparación correcta consiste en ejecutar ambos modelos sobre el mismo conjunto de prueba.

2. Al aumentar el umbral de 0.50 a 0.70 se exige mayor probabilidad para clasificar un día como lluvioso. Por ello se predicen menos días con lluvia; normalmente bajan los falsos positivos, pero pueden aumentar los falsos negativos y disminuir el recall.

3. El coeficiente de mayor magnitud positiva suele corresponder a la humedad. Esto es coherente con la forma en que se generaron los datos: una mayor humedad incrementa la probabilidad de lluvia. Los coeficientes se interpretan como cambios en los log-odds, no como porcentajes directos.

4. Con un umbral de 0.50, la cantidad de falsos positivos y falsos negativos depende de la muestra. Un falso positivo significa llevar paraguas y que no llueva; un falso negativo significa no llevarlo cuando sí llueve. Si se quiere reducir este último riesgo, se puede bajar el umbral, aceptando más falsos positivos.

La aplicación permite modificar el umbral e incluir o retirar el viento para verificar estas conclusiones con las métricas y la matriz de confusión.
