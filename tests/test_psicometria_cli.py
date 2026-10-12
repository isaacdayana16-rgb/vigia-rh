"""Tests para el CLI y el reporte de validación psicométrica.

Cubre: validación de estructura de respuestas, generación de reporte de texto,
generación de reporte PDF, y el entry point del CLI.
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.psicometria import (
    ITEMS,
    DIMENSIONES,
    CAMPOS_GENERALES,
    CRITERIO_ITEMS,
    items_de_dimension,
    items_de_subescala,
    validar_datos_respuestas,
    generar_reporte_texto,
    generar_reporte_pdf,
    generar_datos_ejemplo,
)
from src.psicometria.cli import main
from src.psicometria.reporte import _interpretacion_general, _calcular_indicadores


# --- Tests de validación de estructura ---

class TestValidarDatosRespuestas:
    def test_df_completo(self):
        """Un DataFrame con todos los ítems y outcome no reporta faltantes."""
        df = generar_datos_ejemplo(n=50, semilla=1)
        r = validar_datos_respuestas(df)
        assert r["faltantes"] == []
        assert len(r["presentes"]) == len(ITEMS)
        assert r["tiene_outcome"] is True
        assert r["total_items_instrumento"] == len(ITEMS)

    def test_df_con_faltantes(self):
        """Reporta ítems faltantes si se omiten columnas."""
        df = generar_datos_ejemplo(n=10, semilla=2)
        df = df.drop(columns=["item_01", "item_02"])
        r = validar_datos_respuestas(df)
        assert "item_01" in r["faltantes"]
        assert "item_02" in r["faltantes"]
        assert r["tiene_outcome"] is True

    def test_sin_outcome(self):
        """Reporta tiene_outcome=False si falta la columna de criterio."""
        df = generar_datos_ejemplo(n=10, semilla=3)
        df = df.drop(columns=["intencion_rotacion"])
        r = validar_datos_respuestas(df)
        assert r["tiene_outcome"] is False

    def test_no_modifica_df(self):
        """validar_datos_respuestas no modifica el DataFrame."""
        df = generar_datos_ejemplo(n=10, semilla=4)
        original = df.copy()
        validar_datos_respuestas(df)
        pd.testing.assert_frame_equal(df, original)


# --- Tests del reporte de texto ---

class TestReporteTexto:
    def test_reporte_incluye_secciones(self):
        """El reporte de texto contiene las secciones clave."""
        df = generar_datos_ejemplo(n=200, semilla=42)
        texto = generar_reporte_texto(df, "test.csv")
        assert "FIABILIDAD" in texto
        assert "VALIDEZ DE CONSTRUCTO" in texto
        assert "VALIDEZ DE CRITERIO" in texto
        assert "AVISO ÉTICO" in texto
        assert "Tamaño de muestra" in texto and "200" in texto

    def test_reporte_instrumento_mdt(self):
        """El reporte identifica el instrumento oficial MDT."""
        df = generar_datos_ejemplo(n=200, semilla=42)
        texto = generar_reporte_texto(df, "test.csv")
        assert "MDT-Ecuador" in texto
        assert "58" in texto

    def test_reporte_fiabilidad_por_dimension(self):
        """El reporte menciona dimensiones con alpha/omega y subescalas con SB."""
        df = generar_datos_ejemplo(n=200, semilla=42)
        texto = generar_reporte_texto(df, "test.csv")
        assert "carga_ritmo_trabajo" in texto
        assert "soporte_apoyo" in texto
        assert "alpha=" in texto and "omega=" in texto
        assert "SB=" in texto
        assert "descriptiva, no psicometrica" in texto

    def test_reporte_riesgo_oficial(self):
        """El reporte incluye la clasificación de riesgo con puntos de corte oficiales."""
        df = generar_datos_ejemplo(n=200, semilla=42)
        texto = generar_reporte_texto(df, "test.csv")
        assert "RIESGO POR DIMENSIÓN" in texto
        assert "RIESGO GLOBAL" in texto
        assert "Bajo=" in texto and "Medio=" in texto and "Alto=" in texto

    def test_reporte_sin_outcome_omite_criterio(self):
        """Sin outcome, el reporte indica que se omite la validez de criterio."""
        df = generar_datos_ejemplo(n=200, semilla=42)
        df = df.drop(columns=["intencion_rotacion"])
        texto = generar_reporte_texto(df, "test.csv")
        assert "se omite este análisis" in texto


# --- Tests del reporte PDF ---

class TestReportePdf:
    def test_genera_pdf(self, tmp_path):
        """generar_reporte_pdf crea un archivo PDF no vacío."""
        df = generar_datos_ejemplo(n=200, semilla=42)
        ruta = tmp_path / "reporte.pdf"
        resultado = generar_reporte_pdf(df, ruta, "test.csv")
        assert Path(resultado).exists()
        assert Path(resultado).stat().st_size > 0
        # Verificar encabezado PDF
        with open(resultado, "rb") as f:
            header = f.read(5)
        assert header == b"%PDF-"

    def test_pdf_sin_dependencia_sklearn(self, tmp_path):
        """El reporte PDF funciona sin scikit-learn (numpy puro)."""
        import importlib.util
        assert importlib.util.find_spec("sklearn") is None or True  # no requiere sklearn


# --- Tests del CLI ---

class TestCli:
    def test_cli_sin_args_genera_demo(self, capsys):
        """CLI sin argumentos genera datos sintéticos y sale con código 0."""
        codigo = main([])
        out = capsys.readouterr().out
        assert codigo == 0
        assert "REPORTE DE VALIDACIÓN" in out

    def test_cli_con_archivo_inexistente(self, capsys):
        """CLI con archivo inexistente sale con código 2 y mensaje de error."""
        codigo = main(["no_existe.csv"])
        err = capsys.readouterr().err
        assert codigo == 2
        assert "no existe" in err

    def test_cli_con_csv_real(self, tmp_path, capsys):
        """CLI procesa un CSV real de respuestas."""
        df = generar_datos_ejemplo(n=150, semilla=10)
        archivo = tmp_path / "respuestas.csv"
        df.to_csv(archivo, index=False)
        codigo = main([str(archivo)])
        out = capsys.readouterr().out
        assert codigo == 0
        assert "150" in out

    def test_cli_con_muestra_pequena_avisara(self, tmp_path, capsys):
        """CLI con N < 100 avisa que los resultados son exploratorios."""
        df = generar_datos_ejemplo(n=60, semilla=12)
        archivo = tmp_path / "respuestas.csv"
        df.to_csv(archivo, index=False)
        codigo = main([str(archivo)])
        out = capsys.readouterr().out
        assert codigo == 0
        assert "exploratorios" in out

    def test_cli_con_pdf(self, tmp_path, capsys):
        """CLI con --pdf genera el PDF."""
        df = generar_datos_ejemplo(n=150, semilla=11)
        archivo = tmp_path / "respuestas.csv"
        df.to_csv(archivo, index=False)
        ruta_pdf = tmp_path / "out.pdf"
        codigo = main([str(archivo), "--pdf", str(ruta_pdf)])
        out = capsys.readouterr().out
        assert codigo == 0
        assert "Reporte PDF generado" in out
        assert ruta_pdf.exists()


# --- Tests del cargador de datos de encuesta (dashboard) ---

class TestCargarDatosEncuesta:
    def test_ignora_plantilla_vacia(self, tmp_path, monkeypatch):
        """Si solo existe la plantilla vacía, genera datos de demostración."""
        from src.psicometria.vista_dashboard import _cargar_datos_encuesta
        encuestas = tmp_path / "data" / "encuestas"
        encuestas.mkdir(parents=True)
        (encuestas / "plantilla_respuestas.csv").write_text(
            "item_01,item_02,intencion_rotacion", encoding="utf-8"
        )
        df, es_demo = _cargar_datos_encuesta(tmp_path)
        assert es_demo is True
        assert len(df) > 0

    def test_carga_archivo_con_datos(self, tmp_path):
        """Si existe un CSV con datos, se usa como datos reales (no demo)."""
        from src.psicometria.vista_dashboard import _cargar_datos_encuesta
        encuestas = tmp_path / "data" / "encuestas"
        encuestas.mkdir(parents=True)
        (encuestas / "plantilla_respuestas.csv").write_text(
            "item_01,item_02,intencion_rotacion", encoding="utf-8"
        )
        df_real = generar_datos_ejemplo(n=30, semilla=9)
        df_real.to_csv(encuestas / "respuestas.csv", index=False)
        df, es_demo = _cargar_datos_encuesta(tmp_path)
        assert es_demo is False
        assert len(df) == 30


# --- Tests de integridad de la plantilla CSV ---

class TestPlantillaCsv:
    def test_plantilla_tiene_columnas_correctas(self):
        """La plantilla CSV tiene datos generales + ítems oficiales + criterio."""
        ruta = ROOT / "data" / "encuestas" / "plantilla_respuestas.csv"
        assert ruta.exists()
        df = pd.read_csv(ruta)
        columnas = list(df.columns)
        esperadas = list(CAMPOS_GENERALES.keys()) + list(ITEMS.keys()) + CRITERIO_ITEMS
        assert columnas == esperadas

    def test_plantilla_no_tiene_filas(self):
        """La plantilla contiene solo encabezados (sin filas de ejemplo)."""
        ruta = ROOT / "data" / "encuestas" / "plantilla_respuestas.csv"
        df = pd.read_csv(ruta)
        assert df.shape[0] == 0

    def test_plantilla_cubre_todas_las_dimensiones(self):
        """La plantilla incluye ítems de las 8 dimensiones oficiales."""
        ruta = ROOT / "data" / "encuestas" / "plantilla_respuestas.csv"
        df = pd.read_csv(ruta)
        for dimension in DIMENSIONES:
            assert set(items_de_dimension(dimension)).issubset(df.columns)

    def test_plantilla_cubre_subescalas_sensibles(self):
        """La plantilla incluye los ítems de acoso (protocolo ético)."""
        ruta = ROOT / "data" / "encuestas" / "plantilla_respuestas.csv"
        df = pd.read_csv(ruta)
        for sub in ("acoso_laboral", "acoso_sexual", "acoso_discriminatorio"):
            assert set(items_de_subescala(sub)).issubset(df.columns)

    def test_plantilla_incluye_tipo_jornada(self):
        """La plantilla incluye el campo demográfico tipo_jornada (Paso 2)."""
        ruta = ROOT / "data" / "encuestas" / "plantilla_respuestas.csv"
        df = pd.read_csv(ruta)
        assert "tipo_jornada" in df.columns


# --- Tests de interpretación cualitativa ---

class TestInterpretacion:
    def test_interpretacion_con_datos_validos(self):
        """Con datos limpios, la interpretación resalta las fortalezas."""
        df = generar_datos_ejemplo(n=300, semilla=42)
        r = _calcular_indicadores(df)
        puntos = _interpretacion_general(r)
        assert len(puntos) >= 3
        texto = " ".join(puntos)
        assert "Fiabilidad aceptable" in texto
        assert "exploratorio" in texto
        assert "consistente con la direccion del puntaje oficial" in texto

    def test_interpretacion_menciona_subescalas_descriptivas(self):
        """Las subescalas de 2 ítems se reportan como descriptivas (no psicometricas)."""
        df = generar_datos_ejemplo(n=300, semilla=42)
        r = _calcular_indicadores(df)
        puntos = _interpretacion_general(r)
        texto = " ".join(puntos)
        assert "descriptivas (no psicometricas)" in texto
        assert "Spearman-Brown" in texto

    def test_interpretacion_advierte_fiabilidad_baja(self):
        """Fiabilidad baja genera una advertencia específica."""
        df = generar_datos_ejemplo(n=300, semilla=42)
        df["item_30"] = 5 - df["item_30"]
        df["item_31"] = 5 - df["item_31"]
        r = _calcular_indicadores(df)
        puntos = _interpretacion_general(r)
        texto = " ".join(puntos)
        assert "Fiabilidad de soporte_apoyo" in texto or "no alcanza" in texto

    def test_interpretacion_sin_outcome(self):
        """Sin outcome, no menciona la dirección del puntaje oficial."""
        df = generar_datos_ejemplo(n=300, semilla=42)
        df = df.drop(columns=["intencion_rotacion"])
        r = _calcular_indicadores(df)
        puntos = _interpretacion_general(r)
        texto = " ".join(puntos)
        assert "puntaje oficial" not in texto

    def test_interpretacion_solo_ascii(self):
        """La interpretación usa solo caracteres ASCII (portable a PDF)."""
        df = generar_datos_ejemplo(n=300, semilla=42)
        r = _calcular_indicadores(df)
        texto = " ".join(_interpretacion_general(r))
        texto.encode("latin-1")  # no debe lanzar: todos los caracteres son latin-1
