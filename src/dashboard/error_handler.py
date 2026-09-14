"""Manejo centralizado de errores para Vigía RH.

Proporciona graceful degradation y mensajes específicos al usuario
para mantener la funcionalidad del dashboard ante errores.
"""

import os
import sys
import traceback
from typing import Callable, Any, Optional
from functools import wraps


class VigiaError(Exception):
    """Excepción base para errores de Vigía RH."""
    pass


class ErrorDatos(VigiaError):
    """Error en carga/validación de datos."""
    pass


class ErrorMapeo(VigiaError):
    """Error en mapeo de columnas."""
    pass


class ErrorCalculo(VigiaError):
    """Error en cálculos analíticos."""
    pass


def manejar_error_ui(func: Callable) -> Callable:
    """Decorador para manejar errores en componentes UI con mensajes específicos.
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada con manejo de errores
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Optional[Any]:
        try:
            return func(*args, **kwargs)
        except ErrorDatos as e:
            return {"error": "error_datos", "mensaje": str(e), "recuperable": True}
        except ErrorMapeo as e:
            return {"error": "error_mapeo", "mensaje": str(e), "recuperable": True}
        except ErrorCalculo as e:
            return {"error": "error_calculo", "mensaje": str(e), "recuperable": False}
        except FileNotFoundError as e:
            return {"error": "archivo_no_encontrado", "mensaje": str(e), "recuperable": True}
        except Exception as e:
            return {
                "error": "error_desconocido", 
                "mensaje": f"Error inesperado: {str(e)}", 
                "recuperable": False,
                "traceback": traceback.format_exc()
            }
    return wrapper


def validar_csv_corrupto(df, ruta_archivo: str) -> None:
    """Valida si el CSV está corrupto o tiene problemas estructurales.
    
    Args:
        df: DataFrame a validar
        ruta_archivo: Ruta del archivo para mensajes de error
        
    Raises:
        ErrorDatos: Si el CSV tiene problemas
    """
    if df is None or df.empty:
        raise ErrorDatos(f"El archivo {ruta_archivo} está vacío o corrupto.")
    
    if len(df.columns) < 3:
        raise ErrorDatos(
            f"El archivo {ruta_archivo} tiene muy pocas columnas ({len(df.columns)}). "
            "Se esperan al menos 3 columnas."
        )


def validar_tamano_archivo(ruta_archivo: str, max_mb: int = 50) -> None:
    """Valida que el archivo no exceda el tamaño máximo permitido.
    
    Args:
        ruta_archivo: Ruta del archivo
        max_mb: Tamaño máximo en MB
        
    Raises:
        ErrorDatos: Si el archivo es demasiado grande
    """
    tamano_bytes = os.path.getsize(ruta_archivo)
    tamano_mb = tamano_bytes / (1024 * 1024)
    
    if tamano_mb > max_mb:
        raise ErrorDatos(
            f"El archivo excede el tamaño máximo permitido ({tamano_mb:.1f}MB > {max_mb}MB). "
            "Por favor optimiza el archivo o divídelo en partes."
        )
