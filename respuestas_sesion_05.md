# Sesión 5 — Actividad de clase

**Nombre y apellido:** _Completar antes de entregar_  
**URL de la app de Streamlit:** _Completar después del despliegue_

## 1. Tipos de datos

Convertir `ubicacion` a `category` reduce memoria porque Pandas guarda un código pequeño para cada fila y una única tabla con los tres textos posibles; no repite cadenas como `invernadero_1`, `patio` y `bodega` cientos de veces. Tratar la ubicación como numérica introduciría un orden y una distancia inexistentes —por ejemplo, asumir que `bodega=2` está el doble de lejos de `invernadero_1=0` que `patio=1`—, lo que sesgaría al modelo. Se debe codificar como variable categórica, por ejemplo con one-hot encoding.

## 2. Missing values y outliers

Al aumentar el multiplicador IQR, los límites son más amplios y se detectan menos outliers; al reducirlo, el criterio se vuelve más estricto. IQR solo señala una observación estadísticamente inusual: no puede saber si una temperatura extrema fue un fallo del sensor o una ola de calor real. Para decidir se necesita contexto externo, como especificaciones y calibración del sensor, registros de mantenimiento, lecturas de sensores cercanos, datos meteorológicos y la fecha/hora del evento.

## 3. Normalización y estandarización

Min-Max y Z-score son transformaciones lineales: cambian ubicación y escala, pero conservan el orden y la forma relativa de la distribución. Por eso no corrigen asimetría ni eliminan outliers. Su objetivo es evitar que variables con escalas grandes, como `presion`, dominen distancias, gradientes o funciones de costo frente a variables con escala pequeña. Esto es importante para k-NN, regresión, redes neuronales y descenso de gradiente.

## 4. Train / Validation / Test

Un split aleatorio puede mezclar observaciones futuras en entrenamiento y observaciones pasadas en validación o prueba. Para una serie de tiempo eso produce fuga de información y una evaluación demasiado optimista: el modelo aprende patrones que todavía no existirían cuando se hiciera una predicción real. El split cronológico respeta el orden de disponibilidad de los datos: se entrena con el pasado, se valida con un periodo posterior y se prueba finalmente con el futuro.

## 5. Probabilidad y estadística

La covarianza depende de las unidades de las variables; la correlación la normaliza y por eso siempre está entre -1 y 1. Una correlación cercana a cero no significa que no haya ninguna relación: solo indica que no hay una relación lineal fuerte. Puede existir una relación no lineal, como una parábola, una relación circular o un efecto que ocurra solo después de un umbral.
