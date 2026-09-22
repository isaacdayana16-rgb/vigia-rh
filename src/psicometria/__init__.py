"""Paquete de psicometría para Vigía RH.

Proporciona un pipeline de validez científica para medir factores de riesgo
psicosocial con el instrumento OFICIAL del Ministerio del Trabajo del Ecuador
(Cuestionario de Evaluación de Riesgo Psicosocial, 58 ítems, escala Likert 1-4,
sumatoria simple con puntos de corte oficiales), en lugar del índice JD-R
exploratorio o del subset COPSOQ anterior.

⚠️ Aviso ético: Este módulo mide constructos psicosociales a nivel grupal.
NO es diagnóstico clínico, NO clasifica individuos, y NO debe usarse para
decisiones individuales de contratación, despido, ascenso o sanción.
"""

from .instrumento import (
    ITEMS,
    DIMENSIONES,
    SUBESCALAS_OTROS,
    PUNTOS_CORTE,
    RIESGO_GLOBAL,
    CAMPOS_GENERALES,
    ESCALA,
    CRITERIO_ITEMS,
    items_de_dimension,
    items_de_subescala,
    clasificar_riesgo_dimension,
    clasificar_riesgo_global,
    validar_instrumento,
)
from .puntuaciones import (
    aplicar_reversa,
    calcular_puntuaciones,
    calcular_puntuaciones_subescala,
    calcular_suma_global,
    validar_datos_respuestas,
)
from .fiabilidad import (
    cronbach_alpha,
    mcdonald_omega,
    spearman_brown,
    clasificar_subescala,
)
from .validacion import analisis_factorial, regresion_logistica, validacion_cruzada_estratificada
from .ejemplos_datos import generar_datos_ejemplo
from .simulador_muestra import simular_fiabilidad_n, recomendar_n
from .reporte import generar_reporte_texto, generar_reporte_pdf
from .calidad_datos import reporte_calidad_datos

__all__ = [
    "ITEMS",
    "DIMENSIONES",
    "SUBESCALAS_OTROS",
    "PUNTOS_CORTE",
    "RIESGO_GLOBAL",
    "CAMPOS_GENERALES",
    "ESCALA",
    "CRITERIO_ITEMS",
    "items_de_dimension",
    "items_de_subescala",
    "clasificar_riesgo_dimension",
    "clasificar_riesgo_global",
    "validar_instrumento",
    "aplicar_reversa",
    "calcular_puntuaciones",
    "calcular_puntuaciones_subescala",
    "calcular_suma_global",
    "validar_datos_respuestas",
    "cronbach_alpha",
    "mcdonald_omega",
    "spearman_brown",
    "clasificar_subescala",
    "analisis_factorial",
    "regresion_logistica",
    "validacion_cruzada_estratificada",
    "generar_datos_ejemplo",
    "simular_fiabilidad_n",
    "recomendar_n",
    "generar_reporte_texto",
    "generar_reporte_pdf",
    "reporte_calidad_datos",
]
