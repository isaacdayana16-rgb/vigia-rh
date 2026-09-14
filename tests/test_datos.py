"""Tests unitarios para src/datos.py"""
import pytest
import pandas as pd
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.datos import (
    cargar_datos,
    validar_columnas,
    agregar_indice_compuesto_jdr,
    renombrar_columnas_es,
    MAPEO_ES,
)


# Fixtures
@pytest.fixture
def df_completo():
    """DataFrame con todas las columnas requeridas del esquema IBM HR."""
    return pd.DataFrame({
        "Attrition": ["Yes", "No", "Yes"],
        "OverTime": ["Yes", "No", "Yes"],
        "JobSatisfaction": [2, 4, 3],
        "MonthlyIncome": [3000, 5000, 4000],
        "Department": ["Sales", "HR", "R&D"],
        "DistanceFromHome": [5, 10, 20],
        "WorkLifeBalance": [3, 4, 2],
        "RelationshipSatisfaction": [2, 4, 3],
    })


@pytest.fixture
def df_columnas_faltantes():
    """DataFrame sin la columna Attrition."""
    return pd.DataFrame({
        "OverTime": ["Yes", "No"],
        "JobSatisfaction": [2, 4],
    })


@pytest.fixture
def df_atrition_invalido():
    """DataFrame con valores incorrectos en Attrition."""
    return pd.DataFrame({
        "Attrition": ["Maybe", "No", "Yes"],
        "OverTime": ["Yes", "No", "Yes"],
        "JobSatisfaction": [2, 4, 3],
        "MonthlyIncome": [3000, 5000, 4000],
        "Department": ["Sales", "HR", "R&D"],
        "DistanceFromHome": [5, 10, 20],
        "WorkLifeBalance": [3, 4, 2],
        "RelationshipSatisfaction": [2, 4, 3],
    })


@pytest.fixture
def df_overtime_invalido():
    """DataFrame con valor inválido en OverTime."""
    return pd.DataFrame({
        "Attrition": ["Yes", "No"],
        "OverTime": ["Sometimes", "No"],
        "JobSatisfaction": [2, 4],
        "MonthlyIncome": [3000, 5000],
        "Department": ["Sales", "HR"],
        "DistanceFromHome": [5, 10],
        "WorkLifeBalance": [3, 4],
        "RelationshipSatisfaction": [2, 4],
    })


# --- Tests para validar_columnas ---

class TestValidarColumnas:
    def test_pasa_con_columnas_completas(self, df_completo):
        """validar_columnas no lanza excepcion con todas las columnas."""
        validar_columnas(df_completo)

    def test_falla_con_columnas_faltantes(self, df_columnas_faltantes):
        """validar_columnas lanza ValueError cuando faltan columnas."""
        with pytest.raises(ValueError, match="El archivo no tiene las columnas necesarias"):
            validar_columnas(df_columnas_faltantes)

    def test_falla_con_atrition_invalido(self, df_atrition_invalido):
        """validar_columnas lanza ValueError cuando Attrition tiene valores no Yes/No."""
        with pytest.raises(ValueError, match="La columna Attrition debe usar los valores"):
            validar_columnas(df_atrition_invalido)

    def test_pasa_con_atrition_correcto(self, df_completo):
        """validar_columnas no lanza excepcion con Attrition Yes/No."""
        df = df_completo.copy()
        validar_columnas(df)

    def test_pasa_con_espacios_en_columnas(self):
        """validar_columnas strip() los nombres de columnas y pasa con espacios extra."""
        df = pd.DataFrame({
            "Attrition ": ["Yes", "No"],
            "OverTime ": ["Yes", "No"],
            "JobSatisfaction ": [2, 4],
            "MonthlyIncome ": [3000, 5000],
            "Department ": ["Sales", "HR"],
            "DistanceFromHome ": [5, 10],
            "WorkLifeBalance ": [3, 4],
            "RelationshipSatisfaction ": [2, 4],
        })
        validar_columnas(df)


# --- Tests para agregar_indice_compuesto_jdr ---

class TestAgregarIndiceCompuestoJdr:
    def test_anade_columna_jdr(self, df_completo):
        """agregar_indice_compuesto_jdr retorna DataFrame con columna indice_compuesto_jdr."""
        result = agregar_indice_compuesto_jdr(df_completo)
        assert "indice_compuesto_jdr" in result.columns

    def test_calculo_correcto(self, df_completo):
        """Verifica que el índice se calcula correctamente para un caso conocido."""
        result = agregar_indice_compuesto_jdr(df_completo)
        # Para OverTime=Yes (1), JobSatisfaction=2, WorkLifeBalance=3, RelationshipSatisfaction=2:
        # indice = 1*2 + (5-2) + (5-3) + (5-2) = 2 + 3 + 2 + 3 = 10
        row = result.iloc[0]
        assert row["indice_compuesto_jdr"] == 10

    def test_para_overtime_no(self, df_completo):
        """Para OverTime=No, el indice NO incluye el peso de horas extra."""
        result = agregar_indice_compuesto_jdr(df_completo)
        row = result.iloc[1]  # OverTime=No
        # indice = 0*2 + (5-4) + (5-4) + (5-4) = 0 + 1 + 1 + 1 = 3
        assert row["indice_compuesto_jdr"] == 3

    def test_falla_con_overtime_invalido(self, df_overtime_invalido):
        """agregar_indice_compuesto_jdr lanza ValueError cuando OverTime no es Yes/No."""
        with pytest.raises(ValueError, match="OverTime debe ser 'Yes' o 'No'"):
            agregar_indice_compuesto_jdr(df_overtime_invalido)

    def test_no_modifica_original(self, df_completo):
        """agregar_indice_compuesto_jdr retorna un DataFrame nuevo, no modifica el original."""
        original_cols = set(df_completo.columns)
        result = agregar_indice_compuesto_jdr(df_completo)
        assert set(result.columns) != original_cols  # Agrega una columna
        assert set(df_completo.columns) == original_cols  # Original sin cambios


# --- Tests para renombrar_columnas_es ---

class TestRenombrarColumnasEs:
    def test_renombra_columnas_español_a_ingles(self):
        """renombrar_columnas_es convierte nombres de columnas en español a inglés."""
        df_es = pd.DataFrame({
            "Rotación": ["Yes", "No"],
            "Horas Extra": ["Si", "No"],
            "Satisfacción Laboral": [3, 4],
            "Departamento": ["Sales", "HR"],
            "Distancia al Trabajo": [5, 10],
            "Balance Vida-Trabajo": [3, 4],
            "Satisfacción con el Jefe": [2, 4],
        })
        result = renombrar_columnas_es(df_es)
        assert "Attrition" in result.columns
        assert "OverTime" in result.columns
        assert "JobSatisfaction" in result.columns
        assert "Department" in result.columns
        assert "DistanceFromHome" in result.columns
        assert "WorkLifeBalance" in result.columns
        assert "RelationshipSatisfaction" in result.columns

    def test_no_modifica_columnas_ingles(self):
        """Si el DataFrame ya tiene columnas en inglés, no hace nada."""
        df_en = pd.DataFrame({
            "Attrition": ["Yes", "No"],
            "OverTime": ["Yes", "No"],
        })
        original = df_en.copy()
        result = renombrar_columnas_es(df_en)
        assert list(result.columns) == list(original.columns)

    def test_mapeo_tiene_todas_las_claves(self):
        """MAPEO_ES contiene entradas para todas las columnas requeridas."""
        required = {"Attrition", "OverTime", "JobSatisfaction", "MonthlyIncome",
                     "Department", "DistanceFromHome", "WorkLifeBalance",
                     "RelationshipSatisfaction"}
        mapeo_claves = set(MAPEO_ES.keys())
        assert required.issubset(mapeo_claves), f"Faltan claves en MAPEO_ES: {required - mapeo_claves}"


# --- Tests para cargar_datos ---

class TestCargarDatos:
    def test_falla_con_ruta_inexistente(self):
        """cargar_datos lanza FileNotFoundError para ruta que no existe."""
        with pytest.raises(FileNotFoundError):
            cargar_datos(ruta="datos/inexistente.csv")

    def test_carga_dataset_real(self):
        """cargar_datos() carga el dataset default sin error."""
        df = cargar_datos()
        assert len(df) > 0
        assert "Attrition" in df.columns
