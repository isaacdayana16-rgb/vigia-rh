"""Tests de integración para la vista psicométrica del dashboard.

Cubre: métricas de fiabilidad (función pura), simulador interactivo, control
de calidad en la sección, y renderizado completo de la sección (con mocks de
Streamlit y Plotly).
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.psicometria.vista_dashboard import (
    _metricas_fiabilidad,
    _cargar_datos_encuesta,
    componente_simulador_psicometria,
    componente_perfiles_psicosociales,
)
from src.psicometria import generar_datos_ejemplo


def _mock_st():
    """Construye un mock de streamlit con los métodos usados por la vista."""
    st = MagicMock()
    col = MagicMock()
    col.metric = MagicMock()
    st.columns.return_value = [col, col]
    return st


def _mock_px():
    px = MagicMock()
    px.bar.return_value = MagicMock()
    return px


class TestMetricasFiabilidad:
    def test_metricas_con_datos_validos(self):
        """Calcula alpha y omega por dimensión con datos sintéticos."""
        df = generar_datos_ejemplo(n=200, semilla=1)
        m = _metricas_fiabilidad(df)
        assert "demandas" in m and "recursos" in m
        assert m["demandas"]["alpha"] is not None
        assert m["demandas"]["omega"] is not None
        assert 0.0 < m["demandas"]["alpha"] <= 1.0

    def test_metricas_none_con_datos_degenerados(self):
        """Devuelve None si la fiabilidad no es calculable (varianza nula)."""
        df = generar_datos_ejemplo(n=100, semilla=2)
        df["d_cant_1"] = 3.0  # varianza nula en demandas
        with np.errstate(all="ignore"):
            m = _metricas_fiabilidad(df)
        # omega de demandas no calculable -> None (no lanza)
        assert m["demandas"]["omega"] is None


class TestComponenteSimulador:
    @patch("src.psicometria.vista_dashboard.st")
    @patch("src.psicometria.vista_dashboard.generar_datos_ejemplo")
    def test_simulador_genera_metricas(self, mock_gen, mock_st):
        """El simulador genera datos y muestra métricas α/ω."""
        mock_st.slider.return_value = 150
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_gen.return_value = generar_datos_ejemplo(n=150, semilla=42)
        componente_simulador_psicometria()
        assert mock_st.slider.called
        assert mock_st.columns.called
        assert mock_st.metric.called

    @patch("src.psicometria.vista_dashboard.st")
    def test_simulador_marca_demo(self, mock_st):
        """El simulador se presenta como demo pedagógica."""
        mock_st.slider.return_value = 150
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        with patch("src.psicometria.vista_dashboard.generar_datos_ejemplo") as mock_gen:
            mock_gen.return_value = generar_datos_ejemplo(n=150, semilla=42)
            componente_simulador_psicometria()
        captions = [str(c) for c in mock_st.caption.call_args_list]
        assert any("Demo pedagógica" in c for c in captions)


class TestCargarDatosEncuesta:
    def test_ignora_plantilla_y_genera_demo(self, tmp_path):
        """Sin datos reales, genera demo (no usa la plantilla vacía)."""
        encuestas = tmp_path / "data" / "encuestas"
        encuestas.mkdir(parents=True)
        (encuestas / "plantilla_respuestas.csv").write_text(
            "d_cant_1,d_cant_2,intencion_rotacion", encoding="utf-8"
        )
        df, es_demo = _cargar_datos_encuesta(tmp_path)
        assert es_demo is True
        assert len(df) > 0

    def test_usa_datos_reales(self, tmp_path):
        """Con un CSV real (no plantilla), usa esos datos."""
        encuestas = tmp_path / "data" / "encuestas"
        encuestas.mkdir(parents=True)
        (encuestas / "plantilla_respuestas.csv").write_text(
            "d_cant_1,d_cant_2,intencion_rotacion", encoding="utf-8"
        )
        df_real = generar_datos_ejemplo(n=50, semilla=3)
        df_real.to_csv(encuestas / "respuestas.csv", index=False)
        df, es_demo = _cargar_datos_encuesta(tmp_path)
        assert es_demo is False
        assert len(df) == 50


class TestComponentePerfiles:
    @patch("src.psicometria.vista_dashboard.px")
    @patch("src.psicometria.vista_dashboard.st")
    def test_renderiza_con_demo(self, mock_st, mock_px):
        """Con demo, la sección renderiza y llama al simulador."""
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.slider.return_value = 150
        mock_px.bar.return_value = MagicMock()
        componente_perfiles_psicosociales(ROOT)
        assert mock_st.subheader.called
        assert mock_st.warning.called  # aviso ético

    @patch("src.psicometria.vista_dashboard.px")
    @patch("src.psicometria.vista_dashboard.st")
    def test_no_rompe_sin_datos(self, mock_st, mock_px):
        """La sección nunca lanza (try/except interno), aún sin datos."""
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.slider.return_value = 150
        mock_st.subheader.side_effect = Exception("mock error")
        mock_px.bar.return_value = MagicMock()
        # No debe propagar excepción
        componente_perfiles_psicosociales(ROOT)