"""Componentes del dashboard para Vigía RH."""

from .error_handler import (
    VigiaError,
    ErrorDatos,
    ErrorMapeo,
    ErrorCalculo,
    manejar_error_ui,
    validar_csv_corrupto,
    validar_tamano_archivo
)
from .ui_components import (
    componente_carga_archivo,
    componente_metricas_principales,
    componente_filtro_departamento,
    componente_graficas_rotacion,
    componente_indice_jdr,
    componente_explicabilidad_shap
)

__all__ = [
    'VigiaError',
    'ErrorDatos', 
    'ErrorMapeo',
    'ErrorCalculo',
    'manejar_error_ui',
    'validar_csv_corrupto',
    'validar_tamano_archivo',
    'componente_carga_archivo',
    'componente_metricas_principales',
    'componente_filtro_departamento',
    'componente_graficas_rotacion',
    'componente_indice_jdr',
    'componente_explicabilidad_shap'
]
