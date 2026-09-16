"""Tests para el validador de calidad de datos de encuesta (src/psicometria/calidad_datos.py)."""
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.psicometria import (
    ITEMS,
    items_de_dimension,
    generar_datos_ejemplo,
)
from src.psicometria.calidad_datos import (
    validar_rango_items,
    detectar_filas_incompletas,
    detectar_columnas_problema,
    detectar_duplicados,
    detectar_items_varianza_cero,
    validar_outcome,
    reporte_calidad_datos,
)

IDS_ITEMS = list(ITEMS.keys())


def _df_limpio(n=100):
    """DataFrame sintético sin problemas de calidad."""
    return generar_datos_ejemplo(n=n, semilla=1)


class TestValidarRangoItems:
    def test_datos_limpios(self):
        """Datos bien codificados no reportan valores fuera de rango."""
        df = _df_limpio()
        r = validar_rango_items(df)
        assert r["items_afectados"] == []
        assert r["valores_fuera"] == {}

    def test_detecta_valores_fuera_de_rango(self):
        """Detecta valores fuera del rango 1-5."""
        df = _df_limpio()
        df.loc[0, "d_cant_1"] = 7
        df.loc[1, "d_cant_1"] = 0
        r = validar_rango_items(df)
        assert "d_cant_1" in r["items_afectados"]
        assert 7 in r["valores_fuera"]["d_cant_1"]

    def test_limites_son_validos(self):
        """1 y 5 son valores válidos; no se marcan como fuera de rango."""
        df = _df_limpio()
        df.loc[0, "d_cant_1"] = 1
        df.loc[1, "d_cant_1"] = 5
        r = validar_rango_items(df)
        assert "d_cant_1" not in r["items_afectados"]


class TestDetectarFilasIncompletas:
    def test_datos_limpios(self):
        """Datos completos no reportan filas incompletas."""
        df = _df_limpio()
        assert detectar_filas_incompletas(df).empty

    def test_detecta_nan(self):
        """Detecta filas con valores faltantes en ítems."""
        df = _df_limpio()
        df.loc[3, "d_cant_1"] = None
        df.loc[4, "r_apoy_1"] = None
        incompletas = detectar_filas_incompletas(df)
        assert len(incompletas) == 2
        assert 3 in incompletas["indice"].tolist()
        assert 4 in incompletas["indice"].tolist()


class TestDetectarColumnasProblema:
    def test_datos_completos(self):
        """Con todos los ítems y el outcome, no hay columnas problema."""
        df = _df_limpio()
        r = detectar_columnas_problema(df)
        assert r["items_faltantes"] == []
        assert r["columnas_desconocidas"] == []

    def test_detecta_items_faltantes(self):
        """Reporta ítems ausentes si se quitan columnas."""
        df = _df_limpio().drop(columns=["d_cant_1", "d_emoc_3"])
        r = detectar_columnas_problema(df)
        assert "d_cant_1" in r["items_faltantes"]
        assert "d_emoc_3" in r["items_faltantes"]

    def test_detecta_columnas_desconocidas(self):
        """Reporta columnas que no pertenecen al instrumento."""
        df = _df_limpio()
        df["edad_extra"] = 30
        r = detectar_columnas_problema(df)
        assert "edad_extra" in r["columnas_desconocidas"]


class TestDetectarDuplicados:
    def test_datos_limpios(self):
        """Datos sin duplicados no reportan nada."""
        df = _df_limpio(n=100)
        assert detectar_duplicados(df).empty

    def test_detecta_duplicados_exactos(self):
        """Detecta filas idénticas en todos los ítems."""
        df = _df_limpio(n=50)
        df = pd.concat([df, df.iloc[[10]]], ignore_index=True)
        dup = detectar_duplicados(df)
        assert not dup.empty


class TestDetectarItemsVarianzaCero:
    def test_datos_limpios(self):
        """Datos con varianza no reportan ítems con varianza cero."""
        df = _df_limpio()
        assert detectar_items_varianza_cero(df) == []

    def test_detecta_varianza_cero(self):
        """Detecta ítems constantes (no discriminan)."""
        df = _df_limpio()
        df["d_cant_1"] = 3.0
        assert "d_cant_1" in detectar_items_varianza_cero(df)


class TestValidarOutcome:
    def test_outcome_ausente(self):
        """Reporta presente=False si falta la columna."""
        df = _df_limpio().drop(columns=["intencion_rotacion"])
        r = validar_outcome(df)
        assert r["presente"] is False

    def test_outcome_binario(self):
        """Outcome binario correcto (0/1)."""
        df = _df_limpio()
        r = validar_outcome(df)
        assert r["presente"] is True
        assert r["es_binario"] is True

    def test_outcome_no_binario(self):
        """Outcome no binario se detecta."""
        df = _df_limpio()
        df["intencion_rotacion"] = 5  # rango 3-15, no binario
        r = validar_outcome(df)
        assert r["es_binario"] is False


class TestReporteCalidadDatos:
    def test_datos_limpios_sin_advertencias(self):
        """Datos limpios no generan advertencias."""
        df = _df_limpio()
        reporte = reporte_calidad_datos(df)
        assert reporte["advertencias"] == []
        assert reporte["n_filas"] == len(df)

    def test_datos_sucios_generan_advertencias(self):
        """Múltiples problemas generan advertencias."""
        df = _df_limpio()
        df.loc[0, "d_cant_1"] = 9  # fuera de rango
        df.loc[1, "r_apoy_1"] = None  # incompleta
        df = pd.concat([df, df.iloc[[2]]], ignore_index=True)  # duplicado
        reporte = reporte_calidad_datos(df)
        assert len(reporte["advertencias"]) >= 2

    def test_integracion_con_validacion(self):
        """Datos sucios pueden arreglarse y luego validarse correctamente."""
        from src.psicometria import analisis_factorial, cronbach_alpha
        df = _df_limpio()
        # Varianza cero rompería el AFE -> debe detectarse
        df["d_cant_1"] = 3.0
        reporte = reporte_calidad_datos(df)
        assert "d_cant_1" in reporte["items_varianza_cero"]
        assert reporte["advertencias"]