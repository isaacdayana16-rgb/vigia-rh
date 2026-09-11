import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datos import cargar_datos, agregar_indice_compuesto_jdr

# Lectura conceptual del modelo JD-R: las "demandas" desgastan,
# los "recursos" protegen. El calculo del indicador se centralizo en
# src.datos: no duplicamos la formula aqui.

df = cargar_datos()
df = agregar_indice_compuesto_jdr(df)

# ¿El índice compuesto JD-R se relaciona con la rotación real?
print("Índice compuesto JD-R promedio, según si la persona renunció o no:")
print(df.groupby("Attrition")["indice_compuesto_jdr"].mean())

print("\nEsto muestra si nuestra lectura conceptual del JD-R")
print("coincide con lo que el modelo predictivo encontró por su cuenta.")
