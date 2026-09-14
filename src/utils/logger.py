"""Sistema de logging estructurado para Vigía RH.

Proporciona trazabilidad de operaciones, auditoría y debugging
para cumplimiento corporativo y troubleshooting en producción.
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class VigiaLogger:
    """Logger centralizado para operaciones del sistema."""
    
    def __init__(self, nombre: str = "vigia_rh", nivel: int = logging.INFO):
        """Inicializa el logger con configuración estructurada.
        
        Args:
            nombre: Nombre del logger
            nivel: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(nombre)
        self.logger.setLevel(nivel)
        
        # Evitar duplicación de handlers
        if not self.logger.handlers:
            self._configurar_handlers()
    
    def _configurar_handlers(self):
        """Configura handlers para consola y archivo."""
        # Formato estructurado con timestamp
        formato = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formato)
        self.logger.addHandler(console_handler)
        
        # Handler para archivo (logs/)
        logs_dir = Path.cwd() / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        archivo_handler = logging.FileHandler(
            logs_dir / f"vigia_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        archivo_handler.setFormatter(formato)
        self.logger.addHandler(archivo_handler)
    
    def info(self, mensaje: str):
        """Registra mensaje informativo."""
        self.logger.info(mensaje)
    
    def warning(self, mensaje: str):
        """Registra advertencia."""
        self.logger.warning(mensaje)
    
    def error(self, mensaje: str, exc_info: bool = False):
        """Registra error, opcionalmente con traceback."""
        self.logger.error(mensaje, exc_info=exc_info)
    
    def debug(self, mensaje: str):
        """Registra mensaje de debug."""
        self.logger.debug(mensaje)
    
    def critical(self, mensaje: str, exc_info: bool = False):
        """Registra error crítico."""
        self.logger.critical(mensaje, exc_info=exc_info)


# Instancia global del logger
logger = VigiaLogger()
