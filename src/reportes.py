import os
import sys
from pathlib import Path
from fpdf import FPDF

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datos import cargar_datos, agregar_indice_compuesto_jdr

# Rutas seguras - funciona desde cualquier lugar
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "output")
SHAP_PATH = os.path.join(OUTPUT_DIR, "shap_resumen.png")
PDF_PATH = os.path.join(OUTPUT_DIR, "reporte_vigia_rh.pdf")

os.makedirs(OUTPUT_DIR, exist_ok=True)

df = cargar_datos()
df = agregar_indice_compuesto_jdr(df)

total_empleados = len(df)
total_renuncias = len(df[df["Attrition"] == "Yes"])
tasa_rotacion = (total_renuncias / total_empleados) * 100

# Indice compuesto JD-R (calculado en src.datos, formula unica)
indice_jdr_por_grupo = df.groupby("Attrition")["indice_compuesto_jdr"].mean()

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", "B", 18)
pdf.cell(0, 12, "Vigia RH - Reporte de Analitica Predictiva", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 11)
pdf.cell(0, 8, "Sistema de analisis de riesgo de rotacion de personal", new_x="LMARGIN", new_y="NEXT")
pdf.ln(8)

pdf.set_font("Helvetica", "B", 13)
pdf.cell(0, 10, "Resumen general", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 11)
pdf.cell(0, 8, f"Total de empleados: {total_empleados}", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, f"Renuncias registradas: {total_renuncias}", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, f"Tasa de rotacion: {tasa_rotacion:.1f}%", new_x="LMARGIN", new_y="NEXT")
pdf.ln(6)

pdf.set_font("Helvetica", "B", 13)
pdf.cell(0, 10, "Indice compuesto inspirado conceptualmente en el modelo JD-R", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 11)
pdf.cell(0, 8, f"Promedio en empleados que se quedaron: {indice_jdr_por_grupo['No']:.2f}", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, f"Promedio en empleados que renunciaron: {indice_jdr_por_grupo['Yes']:.2f}", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "I", 9)
pdf.cell(0, 6, "Indicador exploratorio; no constituye diagnostico clinico ni reemplaza instrumentos psicologicos validados.", new_x="LMARGIN", new_y="NEXT")
pdf.ln(6)

pdf.set_font("Helvetica", "B", 13)
pdf.cell(0, 10, "Explicabilidad del modelo (SHAP)", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 11)
pdf.cell(0, 8, "Variables que mas influyen en la rotacion:", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)

if os.path.exists(SHAP_PATH):
    pdf.image(SHAP_PATH, w=170)
else:
    pdf.cell(0, 8, f"No se encontro imagen en {SHAP_PATH}", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "I", 9)
pdf.cell(0, 6, "Indicador exploratorio; no constituye diagnostico clinico ni reemplaza instrumentos psicologicos validados.", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)

pdf.output(PDF_PATH)
print(f"Reporte generado en {PDF_PATH}")
