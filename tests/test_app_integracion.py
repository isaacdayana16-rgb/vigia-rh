"""Test de integración del dashboard completo (dashboard/app.py) vía AppTest.

Ejecuta la app real en un runtime de Streamlit simulado y verifica que renderiza
sin excepciones, con sus 4 pestañas y los avisos éticos de la pestaña Inicio.
La ruta al script se ancla a la ubicación del test para que el resultado no
dependa del directorio desde el que se lance pytest.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parent.parent / "dashboard" / "app.py"


@pytest.fixture(scope="module")
def app_ejecutada():
    """Ejecuta la app una sola vez para todos los asserts del módulo."""
    at = AppTest.from_file(str(APP_PATH), default_timeout=90)
    at.run()
    return at


class TestAppIntegracion:
    def test_sin_excepciones(self, app_ejecutada):
        """La app corre sin excepciones no manejadas en el árbol de ejecución."""
        at = app_ejecutada
        assert len(at.exception) == 0, f"Excepciones: {[str(e.value) for e in at.exception]}"

    def test_sin_error_critico_global(self, app_ejecutada):
        """El guard global de app.py no se activó (no hay st.error 'Error crítico')."""
        at = app_ejecutada
        errores_criticos = [
            e for e in at.error if "Error crítico" in str(e.value)
        ]
        assert errores_criticos == []

    def test_cuatro_pestanas(self, app_ejecutada):
        """La app define exactamente 4 pestañas con etiquetas no vacías."""
        at = app_ejecutada
        assert len(at.tabs) == 4
        for tab in at.tabs:
            assert tab.label

    def test_avisos_warning_en_inicio(self, app_ejecutada):
        """La pestaña Inicio muestra el aviso ético (st.warning) esperado."""
        at = app_ejecutada
        avisos = [str(w.value) for w in at.warning]
        assert any("no certificada" in aviso for aviso in avisos), (
            f"No se encontró el aviso ético de Inicio. Avisos: {avisos}"
        )
