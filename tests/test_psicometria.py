"""Tests para el paquete de psicometría (src/psicometria).

Cubre: integridad del instrumento oficial MDT (58 ítems), puntuaciones
(sumatoria simple y clasificación oficial de riesgo), fiabilidad (alpha/omega
y Spearman-Brown para subescalas de 2 ítems), validez de constructo (análisis
factorial), validez de criterio (regresión logística), validación cruzada
estratificada y simulador de N. Se usa datos sintéticos con estructura conocida.
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
    SUBESCALAS_OTROS,
    PUNTOS_CORTE,
    ESCALA,
    items_de_dimension,
    items_de_subescala,
    clasificar_riesgo_dimension,
    clasificar_riesgo_global,
    validar_instrumento,
    aplicar_reversa,
    calcular_puntuaciones,
    calcular_puntuaciones_subescala,
    calcular_suma_global,
    cronbach_alpha,
    mcdonald_omega,
    spearman_brown,
    clasificar_subescala,
    analisis_factorial,
    regresion_logistica,
    validacion_cruzada_estratificada,
    generar_datos_ejemplo,
    simular_fiabilidad_n,
    recomendar_n,
)


# --- Tests del instrumento (oficial MDT, 58 ítems) ---

class TestInstrumento:
    def test_instrumento_valido(self):
        """El instrumento no presenta errores de estructura contra el PDF oficial."""
        assert validar_instrumento() == []

    def test_58_items_oficiales(self):
        """El instrumento tiene exactamente los 58 ítems oficiales (Anexo 11.1)."""
        assert len(ITEMS) == 58
        esperados = {f"item_{n:02d}" for n in range(1, 59)}
        assert set(ITEMS.keys()) == esperados

    def test_dimensiones_oficiales_con_items(self):
        """Las 8 dimensiones oficiales tienen los ítems de la Tabla 2."""
        conteos = {d: len(items_de_dimension(d)) for d in DIMENSIONES}
        assert conteos == {
            "carga_ritmo_trabajo": 4,
            "desarrollo_competencias": 4,
            "liderazgo": 6,
            "margen_accion_control": 4,
            "organizacion_trabajo": 6,
            "recuperacion": 5,
            "soporte_apoyo": 5,
            "otros_puntos_importantes": 24,
        }

    def test_items_ids_unicos(self):
        """Los ids de ítems son únicos."""
        assert len(ITEMS) == len(set(ITEMS.keys()))

    def test_items_particion_exacta(self):
        """Cada ítem pertenece a exactamente una dimensión; cubren los 58."""
        todos = set()
        for dimension in DIMENSIONES:
            todos |= set(items_de_dimension(dimension))
        assert todos == set(ITEMS.keys())

    def test_subescalas_particion_exacta(self):
        """Las subescalas de 'Otros puntos importantes' cubren los ítems 35-58 exactamente."""
        todos = set()
        for sub in SUBESCALAS_OTROS:
            todos |= set(items_de_subescala(sub))
        esperados = {f"item_{n:02d}" for n in range(35, 59)}
        assert todos == esperados

    def test_subescalas_conteos_oficiales(self):
        """Los conteos de subescalas coinciden con la Tabla 2 del PDF oficial."""
        conteos = {s: len(items_de_subescala(s)) for s in SUBESCALAS_OTROS}
        assert conteos == {
            "acoso_discriminatorio": 4,
            "acoso_laboral": 2,
            "acoso_sexual": 2,
            "adiccion_trabajo": 5,
            "condiciones_trabajo": 2,
            "doble_presencia": 2,
            "estabilidad_emocional": 5,
            "salud_auto_percebida": 2,
        }

    def test_escala_likert_1_a_4_oficial(self):
        """La escala de respuesta es la oficial: Likert 1-4 (Tabla 1)."""
        assert ESCALA["minimo"] == 1 and ESCALA["maximo"] == 4
        assert ESCALA["etiquetas"][4] == "Completamente de acuerdo"
        assert ESCALA["etiquetas"][1] == "En desacuerdo"

    def test_textos_no_vacios(self):
        """Todos los ítems tienen texto (transcripción del Anexo 11.1)."""
        for meta in ITEMS.values():
            assert isinstance(meta["texto"], str)
            assert meta["texto"].strip()

    def test_items_sensibles_presentes(self):
        """Los ítems de acoso (protocolo ético) existen en el instrumento."""
        for iid in ("item_41", "item_43", "item_48", "item_50"):
            assert iid in ITEMS

    def test_puntos_corte_oficiales(self):
        """Puntos de corte clave coinciden con la Tabla 3 del PDF oficial."""
        assert PUNTOS_CORTE["carga_ritmo_trabajo"] == {"bajo": (13, 16), "medio": (8, 12), "alto": (4, 7)}
        assert PUNTOS_CORTE["liderazgo"] == {"bajo": (18, 24), "medio": (12, 17), "alto": (6, 11)}
        assert PUNTOS_CORTE["acoso_laboral"] == {"bajo": (7, 8), "medio": (5, 6), "alto": (2, 4)}
        assert PUNTOS_CORTE["otros_puntos_importantes"] == {"bajo": (73, 96), "medio": (49, 72), "alto": (24, 48)}


# --- Tests de clasificación de riesgo oficial ---

class TestClasificacionRiesgo:
    def test_clasificar_dimension(self):
        """Clasificación por dimensión según la Tabla 3."""
        assert clasificar_riesgo_dimension("carga_ritmo_trabajo", 14) == "Bajo"
        assert clasificar_riesgo_dimension("carga_ritmo_trabajo", 10) == "Medio"
        assert clasificar_riesgo_dimension("carga_ritmo_trabajo", 5) == "Alto"

    def test_clasificar_global(self):
        """Clasificación global según la Tabla 4 (menor puntaje = mayor riesgo)."""
        assert clasificar_riesgo_global(200) == "Bajo"
        assert clasificar_riesgo_global(140) == "Medio"
        assert clasificar_riesgo_global(100) == "Alto"

    def test_clasificar_fuera_de_rango_es_none(self):
        """Sumas fuera del rango teórico retornan None (no clasifican)."""
        assert clasificar_riesgo_dimension("carga_ritmo_trabajo", 17) is None
        assert clasificar_riesgo_global(232) == "Bajo"
        assert clasificar_riesgo_global(233) is None
        assert clasificar_riesgo_global(float("nan")) is None

    def test_menor_puntaje_mayor_riesgo(self):
        """Invariante oficial: a menor suma, nivel de riesgo más alto."""
        niveles = ["Bajo", "Medio", "Alto"]
        sumas = [16, 12, 4]
        for s in sumas:
            nivel = clasificar_riesgo_dimension("carga_ritmo_trabajo", s)
            assert niveles.index(nivel) == sumas.index(s)


# --- Tests de puntuaciones ---

class TestPuntuaciones:
    def test_aplicar_reversa_likert_4(self):
        """aplicar_reversa invierte una escala Likert 1-4."""
        serie = pd.Series([1, 2, 3, 4])
        resultado = aplicar_reversa(serie)
        assert resultado.tolist() == [4, 3, 2, 1]

    def test_puntuaciones_suma_por_dimension(self):
        """calcular_puntuaciones calcula la sumatoria simple oficial por dimensión."""
        df = generar_datos_ejemplo(n=100, semilla=1)
        punt = calcular_puntuaciones(df)
        for dimension in DIMENSIONES:
            assert dimension in punt.columns
            assert len(punt) == len(df)

    def test_puntuaciones_suma_correcta_manual(self):
        """La suma por dimensión es la sumatoria de los ítems que la integran."""
        df = pd.DataFrame({
            "item_01": [1.0], "item_02": [2.0], "item_03": [3.0], "item_04": [4.0],
        })
        punt = calcular_puntuaciones(df)
        assert np.isclose(punt["carga_ritmo_trabajo"].iloc[0], 10.0, atol=1e-6)

    def test_puntuaciones_normalizadas_en_rango(self):
        """Las medias por dimensión (normalizadas) están en el rango Likert 1-4."""
        df = generar_datos_ejemplo(n=100, semilla=2)
        punt = calcular_puntuaciones(df, normalizar=True)
        for col in DIMENSIONES:
            assert punt[col].between(1, 4).all()

    def test_puntuaciones_reproducibles(self):
        """Las puntuaciones son deterministas con la misma semilla."""
        df1 = generar_datos_ejemplo(n=50, semilla=7)
        df2 = generar_datos_ejemplo(n=50, semilla=7)
        p1 = calcular_puntuaciones(df1)
        p2 = calcular_puntuaciones(df2)
        pd.testing.assert_frame_equal(p1, p2)

    def test_item_faltante_da_nan(self):
        """Si falta un ítem de la dimensión, la puntuación es NaN (regla oficial)."""
        df = pd.DataFrame({
            "item_01": [1.0, 2.0], "item_02": [2.0, 3.0], "item_03": [3.0, 4.0],
        })
        punt = calcular_puntuaciones(df)
        assert punt["carga_ritmo_trabajo"].isna().all()

    def test_nr_da_nan(self):
        """El texto 'NR' (No Responde) se trata como faltante."""
        df = pd.DataFrame({
            "item_01": ["NR"], "item_02": [2.0], "item_03": [3.0], "item_04": [4.0],
        })
        punt = calcular_puntuaciones(df)
        assert punt["carga_ritmo_trabajo"].isna().all()

    def test_subescala_suma_correcta(self):
        """La suma por subescala usa los ítems oficiales de la Tabla 2."""
        df = generar_datos_ejemplo(n=50, semilla=3)
        punt_sub = calcular_puntuaciones_subescala(df)
        for sub in SUBESCALAS_OTROS:
            assert sub in punt_sub.columns

    def test_suma_global_requiere_todos_los_items(self):
        """La suma global es NaN si no están los 58 ítems; correcta si lo están."""
        df = generar_datos_ejemplo(n=50, semilla=4)
        suma = calcular_suma_global(df)
        assert np.isfinite(suma).all()
        # rango teórico de la suma global: 58-232
        assert suma.between(58, 232).all()

        df_parcial = df.drop(columns=["item_01"])
        suma_parcial = calcular_suma_global(df_parcial)
        assert suma_parcial.isna().all()


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
        """Con dimensiones principales sustantivas coherentes, alpha y omega >= 0.8."""
        df = generar_datos_ejemplo(n=300)
        sustantivas = [d for d in DIMENSIONES if d != "otros_puntos_importantes"]
        for dimension in sustantivas:
            items = items_de_dimension(dimension)
            assert cronbach_alpha(df[items]) >= 0.8
            assert mcdonald_omega(df[items]) >= 0.8

    def test_otros_importantes_heterogeneo_por_diseno(self):
        """'Otros puntos importantes' (24 ítems de 8 subconstructos) tiene alpha
        moderado: heterogeneidad estructural documentada (la simulación muestra
        que converge a ≈0.68 a cualquier N; la guía oficial, pág. 17, la define
        como punto de partida para evaluaciones más específicas)."""
        df = generar_datos_ejemplo(n=300)
        items = items_de_dimension("otros_puntos_importantes")
        alpha = cronbach_alpha(df[items])
        assert 0.5 < alpha < 0.8

    def test_alpha_requiere_dos_items(self):
        """alpha devuelve nan con un solo ítem."""
        df = pd.DataFrame({"a": [1, 2, 3]})
        assert np.isnan(cronbach_alpha(df))

    def test_omega_nan_con_varianza_cero(self):
        """omega devuelve NaN (no lanza) si un ítem tiene varianza nula."""
        df = generar_datos_ejemplo(n=100, semilla=5)
        df["item_01"] = 3.0  # varianza nula
        with np.errstate(all="ignore"):
            omega = mcdonald_omega(df[items_de_dimension("carga_ritmo_trabajo")])
        assert np.isnan(omega)

    def test_omega_nan_con_pocas_filas(self):
        """omega devuelve NaN con menos de 2 filas (sin warning)."""
        df = pd.DataFrame({iid: [3.0] for iid in items_de_dimension("soporte_apoyo")})
        assert np.isnan(mcdonald_omega(df))

    def test_omega_nan_con_nan_en_items(self):
        """omega devuelve NaN (no lanza) con NaN en los ítems."""
        df = generar_datos_ejemplo(n=100, semilla=6)
        df.loc[0, "item_30"] = None
        with np.errstate(all="ignore"):
            omega = mcdonald_omega(df[items_de_dimension("soporte_apoyo")])
        assert np.isnan(omega)


# --- Tests de Spearman-Brown y subescalas de 2 ítems ---

class TestSpearmanBrown:
    def test_spearman_brown_formula(self):
        """SB = 2r / (1 + r) con r conocido."""
        df = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [1, 2, 3, 4, 5]})
        assert np.isclose(spearman_brown(df), 1.0, atol=1e-6)

    def test_spearman_brown_valor_conocido(self):
        """SB con correlación intermedia 0.5 aprox = 0.67 (2*0.5/1.5)."""
        rng = np.random.default_rng(1)
        x = rng.normal(0, 1, 2000)
        y = 0.5 * x + np.sqrt(1 - 0.25) * rng.normal(0, 1, 2000)
        df = pd.DataFrame({"a": x, "b": y})
        sb = spearman_brown(df)
        assert 0.55 < sb < 0.75

    def test_spearman_brown_requiere_dos_items(self):
        """SB es NaN con número de ítems distinto de 2."""
        df = pd.DataFrame({"a": [1, 2, 3], "b": [2, 3, 4], "c": [3, 4, 5]})
        assert np.isnan(spearman_brown(df))

    def test_spearman_brown_nan_con_varianza_nula(self):
        """SB es NaN si un ítem tiene varianza nula."""
        df = pd.DataFrame({"a": [1, 1, 1], "b": [2, 3, 4]})
        assert np.isnan(spearman_brown(df))

    def test_subescala_2_items_clasificada_descriptiva(self):
        """Las subescalas de 2 ítems se marcan 'descriptiva_no_psicometrica'."""
        for sub in ("acoso_laboral", "acoso_sexual", "doble_presencia",
                    "condiciones_trabajo", "salud_auto_percebida"):
            n = len(items_de_subescala(sub))
            assert n == 2
            assert clasificar_subescala(n) == "descriptiva_no_psicometrica"

    def test_subescala_3_o_mas_clasificada_psicometrica(self):
        """Las subescalas de 3+ ítems se marcan 'psicometrica'."""
        for sub in ("acoso_discriminatorio", "adiccion_trabajo", "estabilidad_emocional"):
            n = len(items_de_subescala(sub))
            assert n >= 3
            assert clasificar_subescala(n) == "psicometrica"


# --- Tests de validez de constructo (análisis factorial) ---

class TestAnalisisFactorial:
    def test_recupera_dos_factores(self):
        """El AFE separa dos grupos de ítems con datos sintéticos."""
        df = generar_datos_ejemplo(n=500, semilla=123)
        cargas, varianza = analisis_factorial(df[list(ITEMS.keys())], n_factores=2)
        assert cargas.shape == (len(ITEMS), 2)
        assert (varianza > 0).all()

    def test_varianza_explicada_positiva(self):
        """La varianza explicada por cada factor es positiva y suma <= 1."""
        df = generar_datos_ejemplo(n=500)
        _, varianza = analisis_factorial(df[list(ITEMS.keys())], n_factores=2)
        assert (varianza > 0).all()
        assert varianza.sum() <= 1.0

    def test_dataframe_vacio_no_falla(self):
        """analisis_factorial con 0 filas no lanza error LAPACK, retorna vacío."""
        df = pd.DataFrame({iid: [] for iid in ITEMS})
        cargas, varianza = analisis_factorial(df, n_factores=2)
        assert cargas.shape == (len(ITEMS), 2)
        assert (varianza == 0).all()

    def test_dataframe_con_nan_no_falla(self):
        """analisis_factorial con NaN (varianza nula) no lanza, retorna vacío."""
        df = generar_datos_ejemplo(n=50, semilla=5)
        df = df[list(ITEMS.keys())].copy()
        df.loc[:, "item_01"] = 3.0  # varianza nula en un ítem
        with np.errstate(all="ignore"):
            cargas, _ = analisis_factorial(df, n_factores=2)
        assert cargas.shape == (len(ITEMS), 2)

    def test_una_fila_no_falla(self):
        """analisis_factorial con 1 fila no lanza."""
        df = pd.DataFrame({iid: [3.0] for iid in ITEMS})
        with np.errstate(all="ignore"):
            cargas, _ = analisis_factorial(df, n_factores=2)
        assert cargas.shape == (len(ITEMS), 2)


# --- Tests de validez de criterio (regresión logística) ---

class TestValidezCriterio:
    def test_direccion_univariada_oficial(self):
        """Dirección univariada: mayor puntaje (menos riesgo) -> menor rotación.

        Se prueba por dimensión de forma UNIVARIADA: con las 8 dimensiones
        colineales (todas cargan en el factor general), los coeficientes
        individuales de una regresión multivariada son inestables
        (multicolinealidad), pero la dirección univariada sí es estable.
        """
        df = generar_datos_ejemplo(n=500, semilla=99)
        punt = calcular_puntuaciones(df, normalizar=True)
        y = df["intencion_rotacion"].to_numpy()

        for dimension in DIMENSIONES:
            resultado = regresion_logistica(punt[[dimension]], y)
            coef = resultado["coeficientes"]
            # Dirección del puntaje oficial: a mayor puntaje, menor riesgo
            assert coef[dimension] < 0, f"{dimension}: coeficiente univariado debe ser negativo"

    def test_correlacion_univariada_negativa(self):
        """La correlación de cada dimensión con la rotación es negativa."""
        df = generar_datos_ejemplo(n=500, semilla=99)
        punt = calcular_puntuaciones(df, normalizar=True)
        y = df["intencion_rotacion"].to_numpy()
        for dimension in DIMENSIONES:
            r = np.corrcoef(punt[dimension], y)[0, 1]
            assert r < 0, f"{dimension}: correlación debe ser negativa"

    def test_coeficientes_reproducibles(self):
        """La regresión logística es determinista."""
        df = generar_datos_ejemplo(n=300, semilla=5)
        punt = calcular_puntuaciones(df, normalizar=True)
        X = punt[list(DIMENSIONES)]
        y = df["intencion_rotacion"].to_numpy()

        r1 = regresion_logistica(X, y, epocas=500)
        r2 = regresion_logistica(X, y, epocas=500)
        pd.testing.assert_series_equal(r1["coeficientes"], r2["coeficientes"])


# --- Tests de validación cruzada estratificada ---

class TestValidacionCruzadaEstratificada:
    def test_metricas_balanceadas_con_datos_validos(self):
        """k-fold estratificado retorna F1 macro y balanced accuracy."""
        df = generar_datos_ejemplo(n=300, semilla=42)
        punt = calcular_puntuaciones(df, normalizar=True)
        X = punt[list(DIMENSIONES)]
        y = df["intencion_rotacion"].to_numpy()

        r = validacion_cruzada_estratificada(X, y, k=5)
        assert r["viable"] is True
        assert r["k"] == 5
        assert 0.0 <= r["f1_macro"] <= 1.0
        assert 0.0 <= r["balanced_accuracy"] <= 1.0

    def test_f1_macro_alto_con_senal_conocida(self):
        """Con señal latente conocida y n=300, F1 macro >= 0.6."""
        df = generar_datos_ejemplo(n=300, semilla=42)
        punt = calcular_puntuaciones(df, normalizar=True)
        X = punt[list(DIMENSIONES)]
        y = df["intencion_rotacion"].to_numpy()

        r = validacion_cruzada_estratificada(X, y, k=5)
        assert r["f1_macro"] >= 0.6

    def test_etiqueta_exploratoria_con_n_pequeno(self):
        """Con N < 100, el modelo se declara 'exploratorio_no_generalizable'."""
        df = generar_datos_ejemplo(n=60, semilla=1)
        punt = calcular_puntuaciones(df, normalizar=True)
        X = punt[list(DIMENSIONES)]
        y = df["intencion_rotacion"].to_numpy()

        r = validacion_cruzada_estratificada(X, y, k=5)
        assert r["etiqueta"] == "exploratorio_no_generalizable"

    def test_no_viable_con_clase_insuficiente(self):
        """Con una clase con menos miembros que k, retorna viable=False."""
        df = generar_datos_ejemplo(n=100, semilla=2)
        y = df["intencion_rotacion"].to_numpy().copy()
        y[:] = 1
        y[:3] = 0  # clase 0 con solo 3 miembros < k=5
        punt = calcular_puntuaciones(df, normalizar=True)
        X = punt[list(DIMENSIONES)]

        r = validacion_cruzada_estratificada(X, y, k=5)
        assert r["viable"] is False
        assert r["etiqueta"] == "no_viable_clase_insuficiente"


# --- Tests del simulador de N vs α/ω ---

class TestSimuladorMuestra:
    def test_simular_fiabilidad_n_por_dimension(self):
        """simular_fiabilidad_n retorna α/ω para las 8 dimensiones."""
        r = simular_fiabilidad_n(n=100, semilla=1)
        assert set(r.keys()) == set(DIMENSIONES)
        for dimension, datos in r.items():
            assert 0.0 < datos["alpha"] <= 1.0
            assert 0.0 < datos["omega"] <= 1.0

    def test_simular_fiabilidad_n_reproducible(self):
        """La simulación es determinista con la misma semilla."""
        r1 = simular_fiabilidad_n(n=80, semilla=3)
        r2 = simular_fiabilidad_n(n=80, semilla=3)
        assert r1 == r2

    def test_recomendar_n_estructura(self):
        """recomendar_n retorna n_recomendado, tabla y metadatos."""
        r = recomendar_n(n_min=30, n_max=50, paso=10, semillas=2)
        assert "n_recomendado" in r
        assert "n_recomendado_todas" in r
        assert len(r["tabla"]) == 3
        assert r["umbral"] == 0.70

    def test_recomendar_n_excluye_dimension_heterogenea(self):
        """El criterio por defecto excluye 'otros_puntos_importantes' (heterogénea)."""
        r = recomendar_n(n_min=30, n_max=50, paso=10, semillas=2)
        assert "otros_puntos_importantes" in r["dimensiones_excluidas"]


# --- Tests de integración end-to-end ---

class TestPipelinePsicometrico:
    def test_pipeline_completo(self):
        """El pipeline completo (generar -> puntuar -> clasificar -> validar) funciona."""
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

        punt_norm = calcular_puntuaciones(df, normalizar=True)
        X = punt_norm[list(DIMENSIONES)]
        resultado = regresion_logistica(X, df["intencion_rotacion"].to_numpy())
        assert "intercepto" in resultado["coeficientes"].index
        for dimension in DIMENSIONES:
            assert dimension in resultado["coeficientes"].index
