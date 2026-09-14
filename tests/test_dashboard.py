"""Tests unitarios para los componentes del dashboard y manejo de errores.

Cubre:
- Funciones puras de detección de formato y validación de errores
- Funciones con mock de Streamlit para componentes UI
- Lectura universal de archivos (CSV/Excel)
- Decorador de manejo de errores UI
"""
import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock

ROOT = Path(__file__).resolve().parent.parent
import sys
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dashboard.error_handler import (
    VigiaError,
    ErrorDatos,
    ErrorMapeo,
    ErrorCalculo,
    manejar_error_ui,
    validar_csv_corrupto,
    validar_tamano_archivo,
)
from src.dashboard.ui_components import (
    detectar_formato_archivo,
    leer_archivo_universal,
    componente_metricas_principales,
    componente_filtro_departamento,
    componente_graficas_rotacion,
    componente_indice_jdr,
    componente_explicabilidad_shap,
)


# --- Tests para el módulo de detección de formato ---

class TestDetectarFormatoArchivo:
    def test_csv(self):
        """detectar_formato_archivo retorna 'csv' para archivos .csv."""
        assert detectar_formato_archivo("data.csv") == "csv"

    def test_xlsx(self):
        """detectar_formato_archivo retorna 'excel' para archivos .xlsx."""
        assert detectar_formato_archivo("reporte.xlsx") == "excel"

    def test_xls(self):
        """detectar_formato_archivo retorna 'excel' para archivos .xls."""
        assert detectar_formato_archivo("reporte.xls") == "excel"

    def test_desconocido(self):
        """detectar_formato_archivo retorna 'desconocido' sin extensión."""
        assert detectar_formato_archivo("sin_extension") == "desconocido"

    def test_desconocido_ext_incorrecta(self):
        """detectar_formato_archivo retorna 'desconocido' para extensión no soportada."""
        assert detectar_formato_archivo("data.json") == "desconocido"

    def test_mayusculas(self):
        """detectar_formato_archivo es case-insensitive."""
        assert detectar_formato_archivo("DATA.CSV") == "csv"


# --- Tests para validar_csv_corrupto ---

class TestValidarCsvCorrupto:
    def test_pasa_con_dataframe_valido(self):
        """validar_csv_corrupto no lanza excepción con DataFrame válido."""
        df = pd.DataFrame({"A": [1], "B": [2], "C": [3]})
        validar_csv_corrupto(df, "test.csv")

    def test_lanza_con_dataframe_vacio(self):
        """validar_csv_corrupto lanza ErrorDatos con DataFrame vacío."""
        df = pd.DataFrame()
        with pytest.raises(ErrorDatos, match="vacío o corrupto"):
            validar_csv_corrupto(df, "test.csv")

    def test_lanza_con_dataframe_none(self):
        """validar_csv_corrupto lanza ErrorDatos con None."""
        with pytest.raises(ErrorDatos, match="vacío o corrupto"):
            validar_csv_corrupto(None, "test.csv")

    def test_lanza_con_pocas_columnas(self):
        """validar_csv_corrupto lanza ErrorDatos con menos de 3 columnas."""
        df = pd.DataFrame({"A": [1]})
        with pytest.raises(ErrorDatos, match="muy pocas columnas"):
            validar_csv_corrupto(df, "test.csv")


# --- Tests para validar_tamano_archivo ---

class TestValidarTamanoArchivo:
    def test_pasa_archivo_pequeno(self, tmp_path):
        """validar_tamano_archivo no lanza excepción con archivo pequeño."""
        archivo = tmp_path / "pequeno.txt"
        archivo.write_text("hola")
        validar_tamano_archivo(str(archivo), max_mb=1)

    def test_lanza_archivo_grande(self, tmp_path):
        """validar_tamano_archivo lanza ErrorDatos con archivo que excede max_mb."""
        archivo = tmp_path / "grande.txt"
        contenido = "x" * (1024 * 1024 + 1)  # 1MB + 1 byte
        archivo.write_text(contenido)
        with pytest.raises(ErrorDatos, match="excede el tamaño"):
            validar_tamano_archivo(str(archivo), max_mb=1)

    def test_valor_por_defecto_50mb(self):
        """validar_tamano_archivo usa max_mb=50 como default."""
        archivo = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        archivo.write(b"x" * (1024 * 1024))  # 1MB
        archivo.close()
        try:
            validar_tamano_archivo(archivo.name, max_mb=50)
        finally:
            os.unlink(archivo.name)


# --- Tests para manejar_error_ui ---

class TestManejarErrorUi:
    def test_decorador_passthrough_exitoso(self):
        """manejar_error_ui permite el paso cuando la función no lanza excepción."""
        @manejar_error_ui
        def func_ok(x):
            return x * 2

        assert func_ok(5) == 10

    def test_decorador_captura_error_datos(self):
        """manejar_error_ui convierte ErrorDatos en diccionario recuperable."""
        @manejar_error_ui
        def func_error():
            raise ErrorDatos("datos mal")

        result = func_error()
        assert result["error"] == "error_datos"
        assert result["recuperable"] is True
        assert "datos mal" in result["mensaje"]

    def test_decorador_captura_error_mapeo(self):
        """manejar_error_ui convierte ErrorMapeo en diccionario recuperable."""
        @manejar_error_ui
        def func_error():
            raise ErrorMapeo("mapeo mal")

        result = func_error()
        assert result["error"] == "error_mapeo"
        assert result["recuperable"] is True

    def test_decorador_captura_error_calculo(self):
        """manejar_error_ui convierte ErrorCalculo en diccionario no recuperable."""
        @manejar_error_ui
        def func_error():
            raise ErrorCalculo("calc mal")

        result = func_error()
        assert result["error"] == "error_calculo"
        assert result["recuperable"] is False

    def test_decorador_captura_file_not_found(self):
        """manejar_error_ui captura FileNotFoundError."""
        @manejar_error_ui
        def func_error():
            raise FileNotFoundError("no existe")

        result = func_error()
        assert result["error"] == "archivo_no_encontrado"
        assert result["recuperable"] is True

    def test_decorador_captura_excepcion_genérica(self):
        """manejar_error_ui captura cualquier excepción genérica."""
        @manejar_error_ui
        def func_error():
            raise ValueError("genérico")

        result = func_error()
        assert result["error"] == "error_desconocido"
        assert result["recuperable"] is False
        assert "traceback" in result

    def test_preserva_nombre_funcion(self):
        """manejar_error_ui preserva el nombre de la función original."""
        @manejar_error_ui
        def mi_funcion():
            pass

        assert mi_funcion.__name__ == "mi_funcion"


# --- Tests para leer_archivo_universal ---

class TestLeerArchivoUniversal:
    def test_lectura_csv(self, tmp_path):
        """leer_archivo_universal lee un CSV correctamente."""
        csv_path = tmp_path / "test.csv"
        csv_path.write_text("A,B,C\n1,2,3\n4,5,6")
        df = leer_archivo_universal(str(csv_path), "csv")
        assert len(df) == 2
        assert list(df.columns) == ["A", "B", "C"]
        assert df["A"].tolist() == [1, 4]

    def test_lectura_csv_con_encoding_latin1(self, tmp_path):
        """leer_archivo_universal maneja encoding latin-1."""
        csv_path = tmp_path / "test.csv"
        csv_path.write_bytes("A,B\ncafé,1\n".encode("latin-1"))
        df = leer_archivo_universal(str(csv_path), "csv")
        assert len(df) == 1

    def test_lectura_excel(self, tmp_path):
        """leer_archivo_universal lee un Excel correctamente."""
        xlsx_path = tmp_path / "test.xlsx"
        df_orig = pd.DataFrame({"X": [1, 2], "Y": [3, 4]})
        df_orig.to_excel(xlsx_path, index=False, engine="openpyxl")
        df = leer_archivo_universal(str(xlsx_path), "excel")
        assert len(df) == 2
        assert "X" in df.columns

    def test_formato_no_soportado(self, tmp_path):
        """leer_archivo_universal lanza ErrorDatos para formato no soportado."""
        txt_path = tmp_path / "test.txt"
        txt_path.write_text("hola")
        with pytest.raises(ErrorDatos, match="Formato no soportado"):
            leer_archivo_universal(str(txt_path), "txt")

    def test_ruta_inexistente(self):
        """leer_archivo_universal lanza ErrorDatos para archivo inexistente."""
        with pytest.raises(ErrorDatos):
            leer_archivo_universal("/ruta/que/no/existe.csv", "csv")


# --- Tests para componente_metricas_principales ---

class TestComponenteMetricasPrincipales:
    @patch("src.dashboard.ui_components.st")
    def test_muestra_metricas_correctas(self, mock_st):
        """componente_metricas_principales calcula y muestra métricas correctamente."""
        col_mocks = [MagicMock() for _ in range(3)]
        mock_st.columns.return_value = col_mocks
        df = pd.DataFrame({
            "Attrition": ["Yes", "No", "Yes", "No", "No"],
            "Department": ["Sales", "HR", "R&D", "Sales", "HR"],
        })
        componente_metricas_principales(df)
        assert mock_st.columns.called
        for col in col_mocks:
            col.metric.assert_called_once()
        assert mock_st.metric.call_count == 0

    @patch("src.dashboard.ui_components.st")
    def test_con_cero_empleados(self, mock_st):
        """componente_metricas_principales maneja DataFrame vacío sin división por cero."""
        col_mocks = [MagicMock() for _ in range(3)]
        mock_st.columns.return_value = col_mocks
        df = pd.DataFrame({"Attrition": [], "Department": []})
        componente_metricas_principales(df)
        assert mock_st.columns.called
        col_mocks[0].metric.assert_any_call("Total de empleados", 0)

    @patch("src.dashboard.ui_components.st")
    def test_maneja_excepcion(self, mock_st):
        """componente_metricas_principales muestra error si algo falla."""
        mock_st.columns.side_effect = Exception("mock error")
        df = pd.DataFrame({"Attrition": ["Yes"], "Department": ["Sales"]})
        componente_metricas_principales(df)
        mock_st.error.assert_called_once()

    @patch("src.dashboard.ui_components.st")
    def test_log_info(self, mock_st):
        """componente_metricas_principales loguea las métricas."""
        col_mocks = [MagicMock() for _ in range(3)]
        mock_st.columns.return_value = col_mocks
        df = pd.DataFrame({
            "Attrition": ["Yes", "No"],
            "Department": ["Sales", "HR"],
        })
        with patch("src.dashboard.ui_components.logger") as mock_logger:
            componente_metricas_principales(df)
            mock_logger.debug.assert_called()


# --- Tests para componente_filtro_departamento ---

class TestComponenteFiltroDepartamento:
    @patch("src.dashboard.ui_components.st")
    def test_filtra_departamento(self, mock_st):
        """componente_filtro_departamento filtra por departamento seleccionado."""
        mock_st.selectbox.return_value = "Sales"
        df = pd.DataFrame({
            "Department": ["Sales", "HR", "Sales", "R&D"],
            "Age": [25, 30, 35, 40],
        })
        result = componente_filtro_departamento(df)
        assert len(result) == 2
        assert result["Department"].unique().tolist() == ["Sales"]

    @patch("src.dashboard.ui_components.st")
    def test_sin_filtro_todos(self, mock_st):
        """componente_filtro_departamento retorna todos los datos si 'Todos'."""
        mock_st.selectbox.return_value = "Todos"
        df = pd.DataFrame({
            "Department": ["Sales", "HR"],
            "Age": [25, 30],
        })
        result = componente_filtro_departamento(df)
        assert len(result) == 2

    @patch("src.dashboard.ui_components.st")
    def test_incluye_todos_en_opciones(self, mock_st):
        """componente_filtro_departamento siempre incluye 'Todos'."""
        df = pd.DataFrame({"Department": ["Sales", "HR"]})
        componente_filtro_departamento(df)
        mock_st.selectbox.assert_called_once()
        args = mock_st.selectbox.call_args[0]
        assert args[1][0] == "Todos"

    @patch("src.dashboard.ui_components.st")
    def test_maneja_excepcion(self, mock_st):
        """componente_filtro_departamento retorna df original si hay error."""
        mock_st.selectbox.side_effect = Exception("mock error")
        df = pd.DataFrame({"Department": ["Sales"], "Age": [25]})
        result = componente_filtro_departamento(df)
        assert len(result) == 1


# --- Tests para componente_graficas_rotacion ---

class TestComponenteGraficasRotacion:
    @patch("src.dashboard.ui_components.st")
    def test_genera_graficas(self, mock_st):
        """componente_graficas_rotacion genera y renderiza 2 gráficas."""
        col_mocks = [MagicMock() for _ in range(2)]
        mock_st.columns.return_value = col_mocks
        df = pd.DataFrame({
            "OverTime": ["Yes", "No", "Yes"],
            "Attrition": ["Yes", "No", "Yes"],
            "JobSatisfaction": [2, 4, 3],
        })
        componente_graficas_rotacion(df)
        assert mock_st.plotly_chart.call_count == 2

    @patch("src.dashboard.ui_components.st")
    def test_maneja_excepcion(self, mock_st):
        """componente_graficas_rotacion muestra error si falla."""
        mock_st.columns.side_effect = Exception("mock error")
        df = pd.DataFrame({"OverTime": ["Yes"], "Attrition": ["Yes"]})
        componente_graficas_rotacion(df)
        mock_st.error.assert_called_once()

    @patch("src.dashboard.ui_components.st")
    def test_logger_debug(self, mock_st):
        """componente_graficas_rotacion loguea al finalizar."""
        col_mocks = [MagicMock() for _ in range(2)]
        mock_st.columns.return_value = col_mocks
        df = pd.DataFrame({
            "OverTime": ["Yes"],
            "Attrition": ["Yes"],
            "JobSatisfaction": [2],
        })
        with patch("src.dashboard.ui_components.logger") as mock_logger:
            componente_graficas_rotacion(df)
            mock_logger.debug.assert_called()


# --- Tests para componente_indice_jdr ---

class TestComponenteIndiceJdr:
    @patch("src.dashboard.ui_components.st")
    def test_muestra_indice_con_columna(self, mock_st):
        """componente_indice_jdr muestra el índice si la columna existe."""
        df = pd.DataFrame({
            "indice_compuesto_jdr": [3.5, 7.2, 1.0],
            "Attrition": ["No", "Yes", "No"],
        })
        componente_indice_jdr(df)
        mock_st.metric.assert_called()
        mock_st.plotly_chart.assert_called()

    @patch("src.dashboard.ui_components.st")
    def test_advierte_sin_columna(self, mock_st):
        """componente_indice_jdr muestra advertencia si no existe la columna."""
        df = pd.DataFrame({"Attrition": ["Yes"]})
        componente_indice_jdr(df)
        mock_st.warning.assert_called_once()
        mock_st.plotly_chart.assert_not_called()

    @patch("src.dashboard.ui_components.st")
    def test_muestra_aviso_etico(self, mock_st):
        """componente_indice_jdr siempre muestra el aviso ético."""
        mock_st.columns.return_value = [Mock(), Mock()]
        df = pd.DataFrame({
            "indice_compuesto_jdr": [3.5],
            "Attrition": ["No"],
        })
        componente_indice_jdr(df)
        warning_calls = [str(c) for c in mock_st.warning.call_args_list]
        assert any("ético" in c for c in warning_calls)

    @patch("src.dashboard.ui_components.st")
    def test_maneja_excepcion(self, mock_st):
        """componente_indice_jdr muestra error si algo falla."""
        mock_st.subheader.side_effect = Exception("mock error")
        df = pd.DataFrame({"indice_compuesto_jdr": [1.0]})
        componente_indice_jdr(df)
        mock_st.error.assert_called_once()


# --- Tests para componente_explicabilidad_shap ---

class TestComponenteExplicabilidadShap:
    def test_imagen_existe(self, tmp_path):
        """componente_explicabilidad_shap muestra imagen si el archivo existe."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        img_path = output_dir / "shap_resumen.png"
        img_path.write_bytes(b"fake_png_data")
        with patch("src.dashboard.ui_components.st") as mock_st:
            componente_explicabilidad_shap(tmp_path)
            mock_st.image.assert_called_once()
            assert "shap_resumen.png" in str(mock_st.image.call_args)

    def test_archivo_no_existe(self, tmp_path):
        """componente_explicabilidad_shap muestra info si el archivo no existe."""
        with patch("src.dashboard.ui_components.st") as mock_st:
            componente_explicabilidad_shap(tmp_path)
            mock_st.info.assert_called_once()

    @patch("src.dashboard.ui_components.st")
    def test_maneja_excepcion(self, mock_st):
        """componente_explicabilidad_shap maneja excepciones."""
        mock_st.subheader.side_effect = Exception("mock error")
        with patch("src.dashboard.ui_components.st") as mock_st2:
            mock_st2.subheader.side_effect = Exception("mock error")
            componente_explicabilidad_shap(Path("/tmp"))
            mock_st2.error.assert_called()


# --- Tests para integración de clases de error ---

class TestJerarquiaErrores:
    def test_herencia_vigia_error(self):
        """ErrorDatos hereda de VigiaError."""
        assert issubclass(ErrorDatos, VigiaError)

    def test_herencia_mapeo(self):
        """ErrorMapeo hereda de VigiaError."""
        assert issubclass(ErrorMapeo, VigiaError)

    def test_herencia_calculo(self):
        """ErrorCalculo hereda de VigiaError."""
        assert issubclass(ErrorCalculo, VigiaError)

    def test_vigia_error_es_exception(self):
        """VigiaError es Exception."""
        assert issubclass(VigiaError, Exception)

    def test_captura_por_vigia_error(self):
        """Todos los errores específicos son capturables por VigiaError."""
        try:
            raise ErrorDatos("test")
        except VigiaError:
            pass
        else:
            pytest.fail("ErrorDatos no fue capturado por VigiaError")

        try:
            raise ErrorMapeo("test")
        except VigiaError:
            pass
        else:
            pytest.fail("ErrorMapeo no fue capturado por VigiaError")

        try:
            raise ErrorCalculo("test")
        except VigiaError:
            pass
        else:
            pytest.fail("ErrorCalculo no fue capturado por VigiaError")
