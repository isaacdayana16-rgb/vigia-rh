"""Pruebas de src/modelo.py sobre datos sintéticos pequeños (sin tocar output/)."""
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.modelo import (
    cargar_modelo,
    entrenar_modelo,
    evaluar_modelo,
    guardar_modelo,
    obtener_importancias,
)


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
def modelo_entrenado():
    """Entrena una vez por módulo sobre datos sintéticos (determinista)."""
    df = _df_sintetico()
    return entrenar_modelo(df)


class TestEntrenarModelo:
    def test_retorna_modelo_y_split(self, modelo_entrenado):
        """Devuelve (modelo, X_test, y_test) con el 20% de las filas."""
        modelo, X_test, y_test = modelo_entrenado
        assert hasattr(modelo, "predict")
        assert hasattr(modelo, "predict_proba")
        df = _df_sintetico()
        assert len(X_test) == int(len(df) * 0.2)
        assert len(X_test) == len(y_test)
        assert "Attrition" not in X_test.columns

    def test_categorias_codificadas(self, modelo_entrenado):
        """Las columnas object quedan codificadas como enteros."""
        _, X_test, _ = modelo_entrenado
        for columna in ("Department", "OverTime"):
            assert pd.api.types.is_integer_dtype(X_test[columna])

    def test_determinista(self):
        """Con la misma semilla, el split es idéntico entre ejecuciones."""
        _, X_test_1, y_test_1 = entrenar_modelo(_df_sintetico())
        _, X_test_2, y_test_2 = entrenar_modelo(_df_sintetico())
        pd.testing.assert_frame_equal(X_test_1, X_test_2)
        pd.testing.assert_series_equal(y_test_1, y_test_2)


class TestEvaluarModelo:
    def test_claves_y_rangos(self, modelo_entrenado):
        """Las métricas existen y están en [0, 1]."""
        modelo, X_test, y_test = modelo_entrenado
        metricas = evaluar_modelo(modelo, X_test, y_test)
        assert set(metricas.keys()) == {"accuracy", "precision", "recall", "f1"}
        for valor in metricas.values():
            assert isinstance(valor, float)
            assert 0.0 <= valor <= 1.0


class TestGuardarCargarModelo:
    def test_roundtrip_en_tmp(self, modelo_entrenado, tmp_path):
        """Serializa y deserializa el modelo sin pérdida de predicciones."""
        modelo, X_test, _ = modelo_entrenado
        ruta = tmp_path / "modelo_test.joblib"
        guardar_modelo(modelo, ruta)
        assert ruta.exists()
        modelo_cargado = cargar_modelo(ruta)
        pd.testing.assert_series_equal(
            pd.Series(modelo.predict(X_test)),
            pd.Series(modelo_cargado.predict(X_test)),
        )


class TestObtenerImportancias:
    def test_forma_y_orden(self, modelo_entrenado):
        """Una importancia por feature, no negativas y orden descendente."""
        modelo, X_test, _ = modelo_entrenado
        importancias = obtener_importancias(modelo, X_test)
        assert isinstance(importancias, pd.Series)
        assert len(importancias) == X_test.shape[1]
        assert set(importancias.index) == set(X_test.columns)
        assert (importancias >= 0).all()
        assert importancias.is_monotonic_decreasing
