# Sesión 10 — IoT y sensación térmica

1. Eliminar faltantes reduce las observaciones disponibles y puede romper la continuidad temporal. La interpolación conserva la serie, pero solo es razonable para huecos cortos y tras revisar su duración.
2. Si se usa solo temperatura, el RMSE normalmente sube porque el modelo pierde la información adicional de humedad que afecta la sensación térmica.
3. El modelo debe reevaluarse en un clima mucho más seco: sus coeficientes fueron aprendidos bajo una distribución concreta de temperatura y humedad, por lo que puede no generalizar fuera de ese rango.
4. RMSE penaliza más los errores puntuales grandes porque los eleva al cuadrado. Se prefiere cuando los errores extremos son especialmente costosos; MAE es más fácil de interpretar y menos sensible a valores extremos.

**URL de la app:** _Completar tras el despliegue de Streamlit_.
