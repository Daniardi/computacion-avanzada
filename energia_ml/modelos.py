"""Modelos entrenados con descenso de gradiente."""

# Importamos NumPy para cálculos numéricos y vectores.
import numpy as np


class ModeloBase:
    """Clase madre que comparte el ciclo de entrenamiento entre modelos."""

    def __init__(self, tasa=0.1, iteraciones=500):
        # Guardamos hiperparámetros y valores iniciales que pertenecen a cada objeto.
        self.tasa = tasa
        self.iteraciones = iteraciones
        self.pesos = None
        self.sesgo = 0.0
        self.historial = []

    def _activacion(self, z):
        """Obliga a cada clase hija a definir su propia activación."""
        raise NotImplementedError("Cada modelo debe definir su activación.")

    def _costo(self, y, y_estimado):
        """Obliga a cada clase hija a definir su propia función de costo."""
        raise NotImplementedError("Cada modelo debe definir su costo.")

    def fit(self, x, y):
        """Entrena pesos y sesgo con el ciclo común de descenso de gradiente."""
        # Aseguramos matrices de punto flotante y un vector objetivo unidimensional.
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float).ravel()
        # Inicializamos el estado del modelo según el número de variables de entrada.
        cantidad, variables = x.shape
        self.pesos = np.zeros(variables)
        self.sesgo = 0.0
        self.historial = []
        # Repetimos el cálculo de predicción, error y actualización de parámetros.
        for _ in range(self.iteraciones):
            y_estimado = self._activacion(x @ self.pesos + self.sesgo)
            error = y_estimado - y
            self.pesos -= self.tasa * (x.T @ error) / cantidad
            self.sesgo -= self.tasa * error.mean()
            self.historial.append(self._costo(y, y_estimado))
        # Devolvemos la instancia entrenada.
        return self

    def __repr__(self):
        """Representa el objeto con sus hiperparámetros principales."""
        return f"{type(self).__name__}(tasa={self.tasa}, iteraciones={self.iteraciones})"


class RegresionLineal(ModeloBase):
    """Regresión lineal con error cuadrático medio."""

    def _activacion(self, z):
        # La regresión lineal no transforma el valor lineal.
        return z

    def _costo(self, y, y_estimado):
        # Calculamos el MSE para guardar su evolución durante el entrenamiento.
        return np.mean((y - y_estimado) ** 2)

    def predict(self, x):
        """Predice consumo numérico en kWh."""
        # Aplicamos la ecuación lineal usando los pesos aprendidos.
        return np.asarray(x, dtype=float) @ self.pesos + self.sesgo

    def score(self, x, y):
        """Calcula R², proporción de variación explicada por el regresor."""
        # Comparamos la suma de errores con la variación total del objetivo.
        y = np.asarray(y, dtype=float)
        y_estimado = self.predict(x)
        return 1 - np.sum((y - y_estimado) ** 2) / np.sum((y - y.mean()) ** 2)

    def mae(self, x, y):
        """Calcula el error absoluto medio solicitado en el reto 1."""
        # Promediamos la diferencia absoluta entre valor real y predicción.
        return np.mean(np.abs(np.asarray(y, dtype=float) - self.predict(x)))


class RegresionLogistica(ModeloBase):
    """Clasificador binario con sigmoide y entropía cruzada."""

    def _activacion(self, z):
        # Limitamos z para evitar desbordamientos al calcular la exponencial.
        z = np.clip(z, -500, 500)
        # Convertimos la salida lineal en una probabilidad entre cero y uno.
        return 1 / (1 + np.exp(-z))

    def _costo(self, y, y_estimado):
        # Protegemos los extremos para que logaritmo no reciba cero.
        y_estimado = np.clip(y_estimado, 1e-9, 1 - 1e-9)
        # Calculamos la pérdida de entropía cruzada binaria.
        return -np.mean(y * np.log(y_estimado) + (1 - y) * np.log(1 - y_estimado))

    def predict_proba(self, x):
        """Devuelve probabilidades de consumo alto."""
        # Aplicamos la sigmoide sobre la combinación lineal aprendida.
        x = np.asarray(x, dtype=float)
        return self._activacion(x @ self.pesos + self.sesgo)

    def predict(self, x):
        """Devuelve clase 0 o 1 usando un umbral estándar de 0.5."""
        # Convertimos probabilidades en decisiones binarias.
        return (self.predict_proba(x) >= 0.5).astype(int)

    def score(self, x, y):
        """Calcula exactitud de clasificación."""
        # Promediamos los casos donde la clase predicha coincide con la real.
        return np.mean(self.predict(x) == np.asarray(y, dtype=int))


class ClasificadorEstricto(RegresionLogistica):
    """Clasificador que exige probabilidad de al menos 0.8 para marcar consumo alto."""

    def predict(self, x):
        # Sobrescribimos únicamente la regla de decisión heredada.
        return (self.predict_proba(x) >= 0.8).astype(int)
