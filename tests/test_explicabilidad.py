"""Pruebas de src/explicabilidad.py (SHAP sobre modelo pequeño, PNG en tmp_path)."""
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.explicabilidad import (
    generar_explicacion_empleado,
    generar_grafica_shap,
    obtener_top_variables,
    preparar_datos,
)
from src.modelo import entrenar_modelo


def _df_sintetico(n: int = 60) -> pd.DataFrame:
    """DataFrame pequeño y determinista con esquema mínimo tipo IBM HR."""
    filas = []
    for i in range(n):
        filas.append(
            {
                "Attrition": "Yes" if i % 5 == 0 else "No",
                "Department": "Sales" if i % 2 == 0 else "Research",
                "OverTime": "Yes" if i % 3 == 0 else "No",
                "Age": 25 + (i % 30),
                "MonthlyIncome": 2000 + (i % 50) * 100,
                "JobSatisfaction": 1 + (i % 4),
            }
        )
    return pd.DataFrame(filas)


@pytest.fixture(scope="module")
def contexto_shap():
    """Modelo pequeño entrenado una vez + sus datos de prueba."""
    modelo, X_test, _ = entrenar_modelo(_df_sintetico())
    return modelo, X_test


class TestPrepararDatos:
    def test_split_consistente(self):
        """preparar_datos separa Attrition y conserva las mismas columnas."""
        df, X_test, y_test = preparar_datos()
        assert "Attrition" not in X_test.columns
        assert set(X_test.columns) == set(df.columns) - {"Attrition"}
        assert len(X_test) == len(y_test)
        assert 0 < len(X_test) < len(df)

    def test_determinista(self):
        """El split con random_state=42 es reproducible."""
        _, X_test_1, y_test_1 = preparar_datos()
        _, X_test_2, y_test_2 = preparar_datos()
        pd.testing.assert_frame_equal(X_test_1, X_test_2)
        pd.testing.assert_series_equal(y_test_1, y_test_2)


class TestGenerarExplicacionEmpleado:
    def test_serie_ordenada_por_impacto(self, contexto_shap):
        """Devuelve una Serie SHAP por feature, ordenada por valor absoluto."""
        modelo, X_test = contexto_shap
        shap_empleado = generar_explicacion_empleado(modelo, X_test, empleado_index=0)
        assert isinstance(shap_empleado, pd.Series)
        assert len(shap_empleado) == X_test.shape[1]
        assert set(shap_empleado.index) == set(X_test.columns)
        valores_abs = shap_empleado.abs().to_numpy()
        assert (valores_abs[:-1] >= valores_abs[1:]).all()

    def test_cada_empleado_tiene_explicacion(self, contexto_shap):
        """Todos los índices válidos devuelven una Serie finita."""
        modelo, X_test = contexto_shap
        for i in (0, 1, len(X_test) - 1):
            shap_empleado = generar_explicacion_empleado(modelo, X_test, empleado_index=i)
            assert shap_empleado.notna().all()


class TestObtenerTopVariables:
    def test_top_n(self, contexto_shap):
        """obtener_top_variables retorna exactamente las primeras n entradas."""
        modelo, X_test = contexto_shap
        shap_empleado = generar_explicacion_empleado(modelo, X_test)
        top = obtener_top_variables(shap_empleado, top_n=3)
        assert len(top) == 3
        assert list(top.index) == list(shap_empleado.index[:3])


class TestGenerarGraficaShap:
    def test_png_en_tmp(self, contexto_shap, tmp_path):
        """La gráfica SHAP se guarda en tmp_path como PNG no vacío."""
        modelo, X_test = contexto_shap
        ruta = tmp_path / "shap_test.png"
        generar_grafica_shap(modelo, X_test, str(ruta))
        assert ruta.exists()
        assert ruta.stat().st_size > 0
        assert ruta.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
