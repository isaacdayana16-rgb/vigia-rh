"""Paquete de psicometría para Vigía RH.

Proporciona un pipeline de validez científica para medir constructos
psicosociales (Job Demands y Job Resources) con un instrumento basado en
COPSOQ-ISTAS21 (Moncada et al., 2014), en lugar del índice JD-R exploratorio.

⚠️ Aviso ético: Este módulo mide constructos psicosociales a nivel grupal.
NO es diagnóstico clínico, NO clasifica individuos, y NO debe usarse para
decisiones individuales de contratación, despido, ascenso o sanción.
"""

from .instrumento import (
    ITEMS,
    CRITERIO_ITEMS,
    DIMENSIONES,
    items_de_dimension,
    validar_instrumento,
)
from .puntuaciones import aplicar_reversa, calcular_puntuaciones
from .fiabilidad import cronbach_alpha, mcdonald_omega
from .validacion import analisis_factorial, regresion_logistica
from .ejemplos_datos import generar_datos_ejemplo

__all__ = [
    "ITEMS",
    "CRITERIO_ITEMS",
    "DIMENSIONES",
    "items_de_dimension",
    "validar_instrumento",
    "aplicar_reversa",
    "calcular_puntuaciones",
    "cronbach_alpha",
    "mcdonald_omega",
    "analisis_factorial",
    "regresion_logistica",
    "generar_datos_ejemplo",
]