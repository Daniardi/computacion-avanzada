# Sesión 7 — Regresión lineal

## Ejercicios de práctica

**¿Agregar `Latitude` y `Longitude` mejora R²?** Puede mejorar R² porque la ubicación contiene información importante sobre los precios. El resultado debe compararse en el mismo conjunto de prueba; una mejora en entrenamiento por sí sola no prueba que el modelo generalice.

**¿Qué ocurre si α es muy grande o muy pequeño?** Un α muy pequeño hace que el descenso de gradiente converja correctamente pero muy lentamente. Uno demasiado grande salta el mínimo, oscila y puede divergir, aumentando el MSE.

**¿Qué ocurre al usar `AveRooms` en lugar de `MedInc`?** Se debe entrenar y comparar el MSE final. En general `MedInc` tiene relación lineal más fuerte con `MedHouseVal`, por lo que suele producir un error menor. La conclusión se valida con las métricas obtenidas en la app.
