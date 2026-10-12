"""Pruebas de src/marco_psicologico.py (análisis conceptual, salida por consola)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.marco_psicologico import _analisis_conceptual


class TestAnalisisConceptual:
    def test_imprime_promedios_por_grupo(self, capsys):
        """El análisis imprime los promedios del índice JD-R por Attrition."""
        _analisis_conceptual()
        out = capsys.readouterr().out
        assert "Índice compuesto JD-R promedio" in out
        assert "Yes" in out
        assert "No" in out

    def test_salida_determinista(self, capsys):
        """Dos ejecuciones consecutivas producen la misma salida."""
        _analisis_conceptual()
        out_1 = capsys.readouterr().out
        _analisis_conceptual()
        out_2 = capsys.readouterr().out
        assert out_1 == out_2
        assert out_1.strip() != ""
