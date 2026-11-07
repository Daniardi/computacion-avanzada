# Sesión 16: introducción al procesamiento en paralelo

**Estudiante:** Daniel Ardila Zabala  
**Tema:** hilos, procesos, vectorización y ley de Amdahl.

1. Los hilos mejoran la lectura de sensores porque la mayor parte de cada tarea consiste en esperar una respuesta de red. Mientras un hilo espera, otro puede atender otro sensor.

2. Para un cálculo intensivo los hilos no suelen acelerar Python debido al GIL, que limita la ejecución simultánea de código Python en CPU. Los procesos son más adecuados porque cada proceso tiene su propio intérprete y puede usar otro núcleo.

3. No se deben crear más workers que tareas: los workers adicionales quedan sin trabajo y añaden costo de coordinación. Para CPU se toma como referencia la cantidad de núcleos disponibles.

4. Vectorizar con NumPy suele ser la primera alternativa porque reemplaza ciclos Python por operaciones internas optimizadas. Puede superar a procesos aun usando un núcleo, ya que reduce el costo de ejecutar instrucciones una por una.

5. La ley de Amdahl indica que el speedup depende de la fracción paralelizable p. Por ejemplo, si p es 0.80, el máximo teórico es 5x aunque se disponga de infinitos workers; el 20 % serial limita la mejora.

6. El orden recomendado para optimizar es medir el cuello de botella, vectorizar los cálculos posibles y paralelizar con hilos o procesos solamente la parte que continúe lenta.
