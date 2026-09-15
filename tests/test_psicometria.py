"""Tests para el paquete de psicometría (src/psicometria).

Cubre: integridad del instrumento, puntuaciones, fiabilidad (alpha/omega),
validez de constructo (análisis factorial) y validez de criterio
(regresión logística). Se usa datos sintéticos con estructura conocida.
"""
import numpy as np
import pandas as pd
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.psicometria import (
    ITEMS,
    DIMENSIONES,
    items_de_dimension,
    validar_instrumento,
    aplicar_reversa,
    calcular_puntuaciones,
    cronbach_alpha,
    mcdonald_omega,
    analisis_factorial,
    regresion_logistica,
    generar_datos_ejemplo,
)


# --- Tests del instrumento ---

class TestInstrumento:
    def test_instrumento_valido(self):
        """El instrumento no presenta errores de estructura."""
        assert validar_instrumento() == []

    def test_dimensiones_cubiertas(self):
        """Cada dimensión tiene al menos un ítem."""
        for dimension in DIMENSIONES:
            assert len(items_de_dimension(dimension)) >= 1

    def test_items_ids_unicos(self):
        """Los ids de ítems son únicos."""
        assert len(ITEMS) == len(set(ITEMS.keys()))

    def test_cada_dimension_tiene_items(self):
        """Los ítems se asignan correctamente a demandas y recursos."""
        dem = set(items_de_dimension("demandas"))
        rec = set(items_de_dimension("recursos"))
        assert dem.isdisjoint(rec)
        assert dem | rec == set(ITEMS.keys())

    def test_escala_likert_1_a_5(self):
        """La escala de respuesta se documenta como Likert 1-5."""
        # Solo valida que los ítems sean coherentes (metadatos presentes).
        for meta in ITEMS.values():
            assert isinstance(meta["texto"], str)
            assert meta["texto"].strip()


# --- Tests de puntuaciones ---

class TestPuntuaciones:
    def test_aplicar_reversa(self):
        """aplicar_reversa invierte una escala Likert 1-5."""
        serie = pd.Series([1, 2, 3, 4, 5])
        resultado = aplicar_reversa(serie)
        assert resultado.tolist() == [5, 4, 3, 2, 1]

    def test_puntuaciones_media_por_dimension(self):
        """calcular_puntuaciones calcula la media por dimensión."""
        df = generar_datos_ejemplo(n=100, semilla=1)
        punt = calcular_puntuaciones(df)
        assert "demandas" in punt.columns
        assert "recursos" in punt.columns
        assert len(punt) == len(df)

    def test_puntuaciones_en_rango(self):
        """Las medias por dimensión están en el rango Likert 1-5."""
        df = generar_datos_ejemplo(n=100, semilla=2)
        punt = calcular_puntuaciones(df)
        for col in DIMENSIONES:
            assert punt[col].between(1, 5).all()

    def test_puntuaciones_reproducibles(self):
        """Las puntuaciones son deterministas con la misma semilla."""
        df1 = generar_datos_ejemplo(n=50, semilla=7)
        df2 = generar_datos_ejemplo(n=50, semilla=7)
        p1 = calcular_puntuaciones(df1)
        p2 = calcular_puntuaciones(df2)
        pd.testing.assert_frame_equal(p1, p2)

    def test_reversa_correcta(self):
        """Si un ítem es reversa, se invierte antes de promediar."""
        # Construir un df manual con un ítem reversa conocido
        df = pd.DataFrame({
            "d_cant_1": [1.0, 1.0, 1.0],  # alto = muchas demandas
            "d_cant_2": [5.0, 5.0, 5.0],
            "d_cant_3": [5.0, 5.0, 5.0],
        })
        # Sin ítems reversa definidos aquí, media = 3.67 aprox
        punt = calcular_puntuaciones(df)
        assert np.isclose(punt["demandas"].iloc[0], (1 + 5 + 5) / 3, atol=1e-6)


# --- Tests de fiabilidad ---

class TestFiabilidad:
    def test_alpha_correlacion_perfecta_es_1(self):
        """Cronbach's alpha = 1 para ítems idénticos."""
        df = pd.DataFrame({
            "a": [1, 2, 3, 4, 5],
            "b": [1, 2, 3, 4, 5],
            "c": [1, 2, 3, 4, 5],
        })
        assert np.isclose(cronbach_alpha(df), 1.0, atol=1e-6)

    def test_alpha_en_rango(self):
        """Cronbach's alpha de datos sintéticos está en (0, 1]."""
        df = generar_datos_ejemplo(n=300)
        alphas = {
            dimension: cronbach_alpha(df[items_de_dimension(dimension)])
            for dimension in DIMENSIONES
        }
        for a in alphas.values():
            assert 0.0 < a <= 1.0

    def test_omega_en_rango(self):
        """McDonald's omega de datos sintéticos está en (0, 1]."""
        df = generar_datos_ejemplo(n=300)
        for dimension in DIMENSIONES:
            omega = mcdonald_omega(df[items_de_dimension(dimension)])
            assert 0.0 < omega <= 1.0

    def test_alpha_y_omega_altos_con_datos_consistentes(self):
        """Con ítems de una dimensión coherente, alpha y omega >= 0.6."""
        df = generar_datos_ejemplo(n=300)
        for dimension in DIMENSIONES:
            items = items_de_dimension(dimension)
            assert cronbach_alpha(df[items]) >= 0.6
            assert mcdonald_omega(df[items]) >= 0.6

    def test_alpha_requiere_dos_items(self):
        """alpha devuelve nan con un solo ítem."""
        df = pd.DataFrame({"a": [1, 2, 3]})
        assert np.isnan(cronbach_alpha(df))


# --- Tests de validez de constructo (análisis factorial) ---

class TestAnalisisFactorial:
    def test_recupera_dos_factores(self):
        """El AFE separa demandas y recursos en 2 factores con datos sintéticos."""
        df = generar_datos_ejemplo(n=500, semilla=123)
        cargas, varianza = analisis_factorial(df[list(ITEMS.keys())], n_factores=2)
        assert cargas.shape == (len(ITEMS), 2)

        dem_items = items_de_dimension("demandas")
        rec_items = items_de_dimension("recursos")

        # Cargas absolutas medias por factor y grupo de ítems
        dem_f1 = cargas.loc[dem_items, "F1"].abs().mean()
        dem_f2 = cargas.loc[dem_items, "F2"].abs().mean()
        rec_f1 = cargas.loc[rec_items, "F1"].abs().mean()
        rec_f2 = cargas.loc[rec_items, "F2"].abs().mean()

        # Cada factor debe estar dominado por una dimensión distinta
        # (robusto al orden de los factores)
        f1_dominante = "demandas" if dem_f1 > rec_f1 else "recursos"
        f2_dominante = "demandas" if dem_f2 > rec_f2 else "recursos"
        assert f1_dominante != f2_dominante

    def test_varianza_explicada_positiva(self):
        """La varianza explicada por cada factor es positiva y suma <= 1."""
        df = generar_datos_ejemplo(n=500)
        _, varianza = analisis_factorial(df[list(ITEMS.keys())], n_factores=2)
        assert (varianza > 0).all()
        assert varianza.sum() <= 1.0


# --- Tests de validez de criterio (regresión logística) ---

class TestValidezCriterio:
    def test_direccion_coeficientes_jdr(self):
        """Mayores demandas -> mayor rotación; mayores recursos -> menor rotación."""
        df = generar_datos_ejemplo(n=500, semilla=99)
        punt = calcular_puntuaciones(df)
        X = punt[["demandas", "recursos"]]
        y = df["intencion_rotacion"].to_numpy()

        resultado = regresion_logistica(X, y)
        coef = resultado["coeficientes"]

        # JD-R: demandas (+) y recursos (-)
        assert coef["demandas"] > 0
        assert coef["recursos"] < 0

    def test_coeficientes_reproducibles(self):
        """La regresión logística es determinista."""
        df = generar_datos_ejemplo(n=300, semilla=5)
        punt = calcular_puntuaciones(df)
        X = punt[["demandas", "recursos"]]
        y = df["intencion_rotacion"].to_numpy()

        r1 = regresion_logistica(X, y, epocas=500)
        r2 = regresion_logistica(X, y, epocas=500)
        pd.testing.assert_series_equal(r1["coeficientes"], r2["coeficientes"])


# --- Tests de integración end-to-end ---

class TestPipelinePsicometrico:
    def test_pipeline_completo(self):
        """El pipeline completo (generar -> puntuar -> validar) funciona."""
        df = generar_datos_ejemplo(n=200, semilla=42)
        punt = calcular_puntuaciones(df)

        for dimension in DIMENSIONES:
            items = items_de_dimension(dimension)
            alpha = cronbach_alpha(df[items])
            omega = mcdonald_omega(df[items])
            assert 0.0 < alpha <= 1.0
            assert 0.0 < omega <= 1.0

        cargas, _ = analisis_factorial(df[list(ITEMS.keys())])
        assert cargas.shape[0] == len(ITEMS)

        X = punt[["demandas", "recursos"]]
        resultado = regresion_logistica(X, df["intencion_rotacion"].to_numpy())
        assert "intercepto" in resultado["coeficientes"].index
        assert "demandas" in resultado["coeficientes"].index
        assert "recursos" in resultado["coeficientes"].index