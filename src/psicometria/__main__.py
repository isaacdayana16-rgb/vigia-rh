"""Entry point del paquete psicometría.

Permite ejecutar la validación psicométrica con:
    python -m src.psicometria [archivo.csv] [--pdf RUTA]
"""
import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())