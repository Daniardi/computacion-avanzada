"""Flujo que compone preprocesamiento, entrenamiento e inferencia."""


class FlujoModelo:
    """Une un preprocesador con cualquier modelo que tenga fit, predict y score."""

    def __init__(self, preprocesador, modelo):
        # Guardamos los dos objetos que colaboran dentro del flujo.
        self.preprocesador = preprocesador
        self.modelo = modelo

    def entrenar(self, x, y):
        """Aprende la escala en entrenamiento y ajusta el modelo con datos escalados."""
        # Ajustamos el preprocesador una única vez con los datos de entrenamiento.
        self.preprocesador.fit(x)
        # Transformamos entrenamiento y entrenamos el modelo que contiene el flujo.
        self.modelo.fit(self.preprocesador.transform(x), y)
        # Devolvemos el flujo entrenado.
        return self

    def predecir(self, x):
        """Predice nuevos datos usando la misma escala aprendida."""
        # Transformamos sin recalcular media ni desviación para evitar inconsistencias.
        return self.modelo.predict(self.preprocesador.transform(x))

    def evaluar(self, x, y):
        """Evalúa el modelo usando datos transformados con la escala de entrenamiento."""
        # Delegamos el cálculo de métrica al modelo que compone el flujo.
        return self.modelo.score(self.preprocesador.transform(x), y)
