"""Clases de preprocesamiento reutilizables."""

# Importamos NumPy para operar con matrices de datos.
import numpy as np


class Estandarizador:
    """Aprende media y desviación del entrenamiento para reutilizarlas en inferencia."""

    def fit(self, x):
        """Calcula los valores que definen la escala usando solo datos de entrenamiento."""
        # Convertimos la entrada a arreglo numérico para garantizar operaciones matriciales.
        x = np.asarray(x, dtype=float)
        # Guardamos media y desviación como estado del objeto.
        self.media = x.mean(axis=0)
        self.desviacion = x.std(axis=0)
        # Evitamos dividir por cero si una variable es constante.
        self.desviacion[self.desviacion == 0] = 1
        # Devolvemos el propio objeto para permitir encadenar métodos.
        return self

    def transform(self, x):
        """Aplica la escala aprendida, sin volver a calcular sus parámetros."""
        # Convertimos los datos nuevos a una matriz numérica.
        x = np.asarray(x, dtype=float)
        # Restamos la media de entrenamiento y dividimos por su desviación.
        return (x - self.media) / self.desviacion
