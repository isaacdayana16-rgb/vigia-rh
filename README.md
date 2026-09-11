# 🔎 Vigía RH — People Analytics Ético & Rotación Predictiva (exploratorio)

> Intersección entre **Psicología Organizacional** (marco conceptual Job Demands-Resources) y **Ciencia de Datos** (Streamlit + pandas + Plotly + SHAP).

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.63+-red?logo=streamlit)
![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas)
![Plotly](https://img.shields.io/badge/Plotly-Express-3F4F75?logo=plotly)
![FPDF](https://img.shields.io/badge/FPDF2-reportes-EC1C24)
![License](https://img.shields.io/badge/Licencia-MIT-green)
![Status](https://img.shields.io/badge/Estado-Prototipo%20funcional-yellow)

---

## ⚠️ Compromiso ético (léeme antes de usar)

Este proyecto es **estrictamente exploratorio** y no reemplaza la práctica profesional:

- ✅ El indicador principal se denomina **Índice compuesto JD-R (exploratorio)**, "inspirado conceptualmente" en el modelo Job Demands-Resources.
- ❌ **NO** es un instrumento psicométrico validado, **NO** es diagnóstico clínico, y **NO** evalúa síndrome de burnout, MBI, UWES-9 ni ningún test sancionado.
- 🧪 El dataset de demostración es **IBM HR Analytics Employee Attrition (dataset público de Kaggle)**: no contiene datos reales de empleados.
- 🚫 El código **no debe usarse** para tomar decisiones individuales sobre contratación, despido, ascenso o sanción de personas.

---

## 📸 Preview del dashboard

> *(Reemplazar esta línea por una screenshot real 1200x700 del dashboard corriendo localmente: métricas + histograma JD-R + disclaimer st.warning() + imagen SHAP)*

---

## 🎯 Contexto: el problema de la rotación

Reemplazar a un empleado cuesta, en promedio, entre 6 y 9 meses de su salario (estudios de SHRM y Gallup).
La mayoría de reportes de RRHH describen **qué** está pasando (kpis de rotación), pero no aportan un **marco conceptual** para entender **por qué** ni para priorizar acciones de mitigación.

Vigía RH cierra esa brecha traduciendo variables operativas de RRHH a la lente del **modelo Job Demands-Resources (JD-R, Bakker & Demerouti, 2007)**.

---

## 🧠 Marco conceptual JD-R (trasfondo del índice)

El modelo JD-R diferencia dos ejes que afectan el bienestar y la permanencia:

| Eje | Descripción | Representación en el índice |
|---|---|---|
| **Demandas** | Factores del trabajo que agotan energía (horas extra, carga mental) | Peso positivo: **Horas extra × 2** |
| **Recursos** | Factores que protegen y motivan (satisfacción, balance vida-trabajo, relación con el jefe) | Peso inverso: `(5 − Satisfacción) + (5 − Balance) + (5 − Relación)` |

**Fórmula publicada, 100% transparente** ([src/datos.py](file:///c:/Users/User/vigia-rh/src/datos.py#L77-L82)):
```
indice_compuesto_jdr =
    OverTime × 2
    + (5 − JobSatisfaction)
    + (5 − WorkLifeBalance)
    + (5 − RelationshipSatisfaction)
```

Rango teórico: **0 (menor desgaste)** → **14 (mayor desgaste)**. A mayor valor, perfil asociado estadísticamente a mayor rotación en el dataset demo.

---

## ✅ Qué hace HOY el producto (features reales, committeadas)

1. **🔌 Pipeline de datos centralizado** (`src/datos.py`):
   - Carga de CSV con ruta configurable.
   - `validar_columnas()`: validación estricta del esquema mínimo IBM HR (8 columnas).
   - `agregar_indice_compuesto_jdr(df)`: cálculo único del indicador (fuente de verdad).
2. **📊 Dashboard interactivo Streamlit** (`dashboard/app.py`):
   - 3 métricas de rotación globales.
   - Filtro dinámico por **Departamento**.
   - 2 histogramas Plotly (horas extra / satisfacción laboral) segmentados por Attrition.
   - **Sección Índice JD-R**: métrica promedio + histograma 0..14 + disclaimer ético `st.warning()`.
   - Sección **SHAP** con imagen de resumen precomputada.
3. **📄 Reporte PDF automatizado** (`src/reportes.py`):
   - Encabezado, resumen general, sección JD-R (con disclaimer), sección SHAP (con disclaimer).
4. **📘 Script de lectura conceptual** (`src/marco_psicologico.py`):
   - Compara promedio del índice JD-R entre empleados que renunciaron vs los que se quedaron (validación exploratoria del dataset demo).

---

## 🧱 Stack tecnológico (al día con el código actual)

| Capa | Librería | Propósito |
|---|---|---|
| Lenguaje | Python 3.11+ | Runtime. |
| Dashboard | Streamlit | Interfaz web interactiva. |
| Datos | pandas | DataFrames y validación. |
| Viz | Plotly Express | Gráficas interactivas. |
| Explicabilidad (outputs) | SHAP | Gráfica de resumen precomputada. |
| Reportes | fpdf2 | Exportación PDF. |
| Robustez imports | `pathlib` + `sys.path` idempotente | Funciona desde cualquier cwd. |

> Nota: scikit-learn, pysentimiento y otros módulos del árbol `src/` sin commitear no forman parte del prototipo mínimamente reproducible en este momento; se listarán cuando se integren al pipeline estable.

---

## 🏗️ Arquitectura modular

```mermaid
flowchart LR
    A[data/WA_Fn-UseC_-HR-Employee-Attrition.csv] --> B
    B[src/datos.py\n(carga + validacion + indice JD-R)]
    B --> C[dashboard/app.py\nUI interactiva Streamlit]
    B --> D[src/reportes.py\nreporte PDF]
    B --> E[src/marco_psicologico.py\nanalisis conceptual]

    F[output/shap_resumen.png] --> C
    F --> D
    D --> G[output/reporte_vigia_rh.pdf]
```

**Diseño clave**: la fórmula del índice JD-R vive **en un solo lugar** — no existe duplicación en el repositorio.

---

## 🚀 Instalación y ejecución (100% reproducible)

### 1. Clonar y preparar entorno
```bash
git clone <URL_DE_TU_REPO>
cd vigia-rh

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependencias mínimas
```bash
pip install -r requirements.txt
# adicionalmente, para generar PDFs:
pip install fpdf2
```

### 3. Ejecutar el dashboard
```bash
streamlit run dashboard/app.py
```
Abre `http://localhost:8501` en tu navegador.

### 4. (Opcional) Generar reporte PDF
```bash
python src/reportes.py
# Salida: output/reporte_vigia_rh.pdf
```

### 5. (Opcional) Análisis conceptual JD-R
```bash
python src/marco_psicologico.py
# Imprime en consola el promedio del índice por grupo de rotación.
```

---

## 📂 Estructura del proyecto

```
vigia-rh/
├── dashboard/
│   └── app.py                    # Entry point: UI Streamlit
├── data/
│   └── WA_Fn-UseC_-HR-Employee-Attrition.csv   # Dataset demo IBM
├── src/
│   ├── __init__.py               # Paquete Python
│   ├── datos.py                  # Núcleo: carga + validación + índice JD-R
│   ├── reportes.py               # Generación PDF (FPDF2)
│   └── marco_psicologico.py      # Lectura conceptual del índice
├── output/
│   ├── shap_resumen.png          # Plot SHAP precomputado
│   └── reporte_vigia_rh.pdf      # Último reporte generado
├── notebooks/                    # Análisis exploratorios (WIP)
├── requirements.txt
└── README.md
```

---

## 📊 Hallazgos demo (del dataset IBM, no interpretables como "validación")

Al ejecutar `python src/marco_psicologico.py` se obtienen valores de promedio del **índice compuesto JD-R**:

| Grupo | Promedio JD-R (demo) |
|---|---|
| Empleados que **se quedaron** (Attrition = No) | `~7.18` |
| Empleados que **renunciaron** (Attrition = Yes) | `~8.35` |

> Aclaración: esta diferencia se observa **en este dataset demo puntual**. No constituye validación del modelo JD-R ni garantiza el mismo comportamiento en otra población.

---

## 🗺️ Roadmap (próximos pasos intencionales)

| Fase | Descripción |
|---|---|
| 🔜 Fase 1 | Despliegue público en **Streamlit Community Cloud**. |
| 🔜 Fase 2 | Soporte para **cargar CSV propio** desde la UI (drag & drop). |
| 🔜 Fase 3 | Tests unitarios (`pytest`) sobre `validar_columnas()` y `agregar_indice_compuesto_jdr()` con fixtures. |
| 🔜 Fase 4 | Integrar **modelo predictivo scikit-learn** committeable al pipeline estable + joblib serializado. |
| 🔜 Fase 5 | Filtros adicionales en dashboard (rango salarial, distancia, antigüedad). |

---

## 📜 Licencia y créditos

- **Código**: Licencia MIT (ver archivo `LICENSE`).
- **Dataset demo**: IBM HR Analytics Employee Attrition & Performance, disponible públicamente en Kaggle.
- **Referencia conceptual**: modelo **JD-R** — *Bakker, A. B., & Demerouti, E. (2007). The job demands-resources model: State of the art.* Journal of Managerial Psychology.

---

## 👋 Autor / Contacto

**Isaac Reyes**
Psicología Organizacional · People Analytics · Data Science

- 🔗 LinkedIn: *(agrega tu link)*
- 🐙 GitHub: *(agrega tu link)*
- ✉️ Email: *(agrega tu correo profesional)*
