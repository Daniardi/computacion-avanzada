# Sesión 15: POO para IA

**Estudiante:** Daniel Ardila Zabala  
**Tema:** encapsulación, herencia, polimorfismo, composición y empaquetado.

1. El modelo lento tiene R2 bajo porque realizó pocas iteraciones y su descenso de gradiente no alcanzó a converger. Se puede aumentar el atributo iteraciones sin modificar la tasa de aprendizaje.

2. Escribir fit una sola vez en ModeloBase evita duplicación. Si se descubre un error en el ciclo de descenso de gradiente, se corrige una vez y las clases hijas reciben la corrección.

3. En inferencia no debe llamarse preprocesador.fit con una lectura nueva. Esa acción recalcula media y desviación con un dato distinto, cambia su escala y hace que el modelo interprete mal las entradas. Se usa transform.

4. El método mae pertenece a RegresionLineal porque mide error absoluto sobre una salida numérica. No es necesario modificar ModeloBase, que mantiene solo lo común a los modelos.

5. ClasificadorEstricto hereda entrenamiento, pesos y probabilidades de RegresionLogistica; solo reemplaza el umbral por 0.8. Al ser más exigente predice menos consumos altos y puede aumentar falsos negativos.

6. FlujoModelo funciona con KNeighborsClassifier de scikit-learn porque ambos siguen el mismo contrato: fit, predict y score. Esta intercambiabilidad es polimorfismo.

7. Para usar escalado entre cero y uno se crea otro preprocesador en preprocesamiento.py. Los modelos y FlujoModelo se conservan, ya que el flujo solo necesita que el preprocesador tenga fit y transform.
