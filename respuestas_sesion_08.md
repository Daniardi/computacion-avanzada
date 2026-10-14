# Sesión 8 — Series de tiempo

1. Al ampliar ACF/PACF a 168 lags puede aparecer un patrón semanal si la simulación incluye una estacionalidad de siete días. La simulación base solo contiene un ciclo diario, por lo que predominan picos en múltiplos de 24 horas.
2. El orden ARIMA debe seleccionarse comparando AIC y, principalmente, RMSE en un periodo de prueba cronológico. Un AIC bajo no garantiza mejor pronóstico fuera de muestra.
3. Una ventana de 6 horas contiene poca información del ciclo diario; una de 48 horas incluye dos ciclos y puede suavizar información reciente. Se comparan mediante MAE: 24 horas suele ser adecuada porque coincide con la estacionalidad diaria.
4. Un modelo multivariado puede mejorar el pronóstico al usar humedad, ya que está relacionada con el ciclo térmico. La mejora se confirma solo si MAE/RMSE bajan en el mismo test temporal.
5. Con datos reales de DHT22/InfluxDB se mantiene el flujo: frecuencia regular, descomposición, split cronológico, ajuste y evaluación.
6. Para una LSTM, una matriz de ventanas `(muestras, pasos)` se reforma como `(muestras, pasos, 1)`. Su desempeño se compara con regresión usando MAE y RMSE en el mismo conjunto de prueba.
