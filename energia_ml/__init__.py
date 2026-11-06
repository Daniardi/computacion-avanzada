"""Paquete reutilizable de preprocesamiento y modelos para energía."""

# Exportamos las clases principales para importarlas desde energia_ml directamente.
from .preprocesamiento import Estandarizador
from .modelos import ClasificadorEstricto, RegresionLineal, RegresionLogistica
from .flujo import FlujoModelo
