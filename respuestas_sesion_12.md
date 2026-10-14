# Sesión 12: analítica y visualización con PCA

**Estudiante:** Daniel Ardila Zabala  
**Tema:** consumo energético de una vivienda, visualización y componentes principales.

1. Un histograma muestra cómo se distribuye el consumo diario, pero no conserva el orden de las fechas. Por ello no permite identificar cuándo ocurrió un aumento o una disminución; el gráfico de línea sí permite responder esa pregunta temporal.

2. Un título con intención para el gráfico de línea es: **“El consumo diario presenta picos aislados que conviene investigar”**. Este título comunica una conclusión, en lugar de limitarse a describir el gráfico.

3. PC1 puede llamarse **“día activo”** porque resume el nivel global de consumo en las horas con pesos positivos altos. PC2 puede llamarse **“mañana frente a tarde”** cuando sus pesos contrastan horas de la mañana con las horas de la tarde. Los nombres deben confirmarse observando los pesos de cada componente.

4. Un día raro aparece lejos del centro de PC1–PC2 porque su perfil horario se diferencia mucho del día promedio. PCA proyecta esa diferencia en las direcciones que concentran más variación.

5. Con 50 sensores, PCA reduce las 50 mediciones a dos coordenadas, PC1 y PC2. Así es posible visualizar agrupamientos, valores atípicos y diferencias entre observaciones en un solo gráfico.

6. Para ayudar a ahorrar energía mostraría el gráfico de barras del consumo típico por hora, con el título: **“El consumo aumenta al final de la tarde: desconectar equipos en espera ayuda a reducirlo”**. Permite reconocer las horas prioritarias para cambiar hábitos.
