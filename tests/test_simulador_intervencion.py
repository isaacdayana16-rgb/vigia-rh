"""Tests para el simulador de intervención (src/simulador_intervencion.py)."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.psicometria import generar_datos_ejemplo
from src.simulador_intervencion import (
    D_CONSERVADOR,
    D_OPTIMISTA,
    INTERVENCIONES,
    priorizar_dimensiones,
    simular_intervencion,
    generar_reporte_texto,
    main,
)


class TestCatalogoIntervenciones:
    def test_catalogo_no_vacio(self):
        """El catálogo de intervenciones no está vacío."""
        assert len(INTERVENCIONES) >= 3

    def test_dimensiones_afectadas_validas(self):
        """Las dimensiones afectadas existen en el instrumento."""
        from src.psicometria.instrumento import DIMENSIONES
        for conf in INTERVENCIONES.values():
            for dim in conf["dimensiones"]:
                assert dim in DIMENSIONES

    def test_tamanos_de_efecto_del_metaanalisis(self):
        """Los d provienen del meta-análisis verificado (Richardson & Rothstein, 2008)."""
        assert D_CONSERVADOR == 0.526
        assert D_OPTIMISTA == 0.687
        assert D_CONSERVADOR < D_OPTIMISTA


class TestPriorizarDimensiones:
    def test_prioridad_con_outcome(self):
        """Con outcome, la prioridad retorna correlaciones negativas."""
        df = generar_datos_ejemplo(n=200, semilla=1)
        prioridad = priorizar_dimensiones(df)
        for dim, valor in prioridad.items():
            assert np.isfinite(valor)
            assert valor < 0

    def test_prioridad_sin_outcome_es_nan(self):
        """Sin outcome, la prioridad es NaN (no se puede priorizar)."""
        df = generar_datos_ejemplo(n=50, semilla=2)
        df = df.drop(columns=["intencion_rotacion"])
        prioridad = priorizar_dimensiones(df)
        assert all(valor != valor for valor in prioridad.values())


class TestSimularIntervencion:
    def test_simulacion_completa(self):
        """La simulación retorna resultados viables con la estructura esperada."""
        df = generar_datos_ejemplo(n=200, semilla=42)
        r = simular_intervencion(df)
        assert "intervenciones" in r
        assert "prioridad" in r
        assert "caveats" in r
        assert len(r["caveats"]) >= 3

    def test_caveats_incluyen_cautela_causal(self):
        """Los caveats documentan que NO es predicción causal verificada."""
        df = generar_datos_ejemplo(n=200, semilla=42)
        r = simular_intervencion(df)
        texto = " ".join(r["caveats"])
        assert "NO predicción causal verificada" in texto
        assert "Richardson & Rothstein (2008" in texto
        assert "previene accidentes" in texto

    def test_delta_suma_positivo(self):
        """El delta de suma es positivo (la intervención mejora el puntaje)."""
        df = generar_datos_ejemplo(n=200, semilla=42)
        r = simular_intervencion(df, ["rediseño_carga_laboral"])
        detalle = r["intervenciones"]["rediseño_carga_laboral"]["dimensiones"]
        for dim, d in detalle.items():
            assert d["delta_suma"]["conservador"] > 0
            assert d["delta_suma"]["optimista"] > d["delta_suma"]["conservador"]

    def test_movimientos_riesgo_no_negativos(self):
        """Ningún nivel de riesgo aumenta tras la intervención simulada."""
        df = generar_datos_ejemplo(n=200, semilla=42)
        r = simular_intervencion(df)
        for nombre, res in r["intervenciones"].items():
            if not res.get("viable"):
                continue
            for dim, d in res["dimensiones"].items():
                for escenario in ("conservador", "optimista"):
                    antes = d["riesgo_antes"]
                    despues = d["riesgo_despues"][escenario]
                    assert despues["Bajo"] >= antes["Bajo"]
                    assert despues["Alto"] <= antes["Alto"]

    def test_intervencion_desconocida_lanza(self):
        """Una intervención desconocida lanza ValueError."""
        df = generar_datos_ejemplo(n=50, semilla=3)
        with pytest.raises(ValueError):
            simular_intervencion(df, ["no_existe"])

    def test_salen_de_alto_consistente_con_distribucion(self):
        """'salen_de_alto' coincide con el cambio en la distribución."""
        df = generar_datos_ejemplo(n=200, semilla=42)
        r = simular_intervencion(df, ["capacitacion_desarrollo"])
        d = r["intervenciones"]["capacitacion_desarrollo"]["dimensiones"]["desarrollo_competencias"]
        esperado = d["riesgo_antes"]["Alto"] - d["riesgo_despues"]["conservador"]["Alto"]
        assert d["salen_de_alto"]["conservador"] == esperado


class TestReporteIntervencion:
    def test_reporte_incluye_secciones(self):
        """El reporte del simulador incluye las secciones y cautelas."""
        df = generar_datos_ejemplo(n=200, semilla=42)
        texto = generar_reporte_texto(df)
        assert "SIMULADOR DE INTERVENCIÓN" in texto
        assert "PRIORIDAD LOCAL" in texto
        assert "CAUTELAS" in texto
        assert "AVISO ÉTICO" in texto
        assert "Richardson & Rothstein (2008)" in texto

    def test_reporte_sin_afirmar_prevencion_accidentes(self):
        """El reporte NO afirma que el modelo previene accidentes (solo la negación explícita)."""
        df = generar_datos_ejemplo(n=200, semilla=42)
        texto = generar_reporte_texto(df)
        lineas_con_frase = [l for l in texto.splitlines() if "previene accidentes" in l]
        # La única mención permitida es la negación explícita (cautela del PASO 11)
        assert len(lineas_con_frase) == 1
        assert "afirma" in lineas_con_frase[0]

    def test_cli_demo(self, capsys):
        """El CLI con datos de demostración sale con código 0."""
        codigo = main([])
        out = capsys.readouterr().out
        assert codigo == 0
        assert "SIMULADOR DE INTERVENCIÓN" in out

    def test_cli_archivo_inexistente(self, capsys):
        """El CLI con archivo inexistente sale con código 2."""
        codigo = main(["no_existe.csv"])
        err = capsys.readouterr().err
        assert codigo == 2

    def test_cli_con_csv(self, tmp_path, capsys):
        """El CLI procesa un CSV real de respuestas."""
        df = generar_datos_ejemplo(n=150, semilla=10)
        archivo = tmp_path / "respuestas.csv"
        df.to_csv(archivo, index=False)
        codigo = main([str(archivo)])
        out = capsys.readouterr().out
        assert codigo == 0
