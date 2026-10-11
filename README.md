# 🔎 Vigía RH — People Analytics Ético & Rotación Predictiva

> Intersección entre **Psicología Organizacional** (marco conceptual Job Demands-Resources) y **Ciencia de Datos** (Streamlit + pandas + Plotly + scikit-learn + SHAP).

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.63+-red?logo=streamlit)
![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas)
![Plotly](https://img.shields.io/badge/Plotly-Express-3F4F75?logo=plotly)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.9.0-FFCB2E?logo=scikit-learn)
![joblib](https://img.shields.io/badge/joblib-serialized_model-00B04A?logo=joblib)
![FPDF](https://img.shields.io/badge/FPDF2-reportes-EC1C24)
![License](https://img.shields.io/badge/Licencia-MIT-green)
![Status](https://img.shields.io/badge/Estado-Modelo%20predictivo%20funcional-green)

---

## ⚠️ Compromiso ético (léeme antes de usar)

Este proyecto es **estrictamente exploratorio** y no reemplaza la práctica profesional:

- ✅ La vía psicosocial usa el **instrumento oficial del Ministerio del Trabajo del Ecuador** (Cuestionario de Evaluación de Riesgo Psicosocial, 58 ítems, escala Likert 1-4, puntos de corte oficiales), transcrito de la fuente primaria (`docs/fuentes/`).
- ❌ **NO** es diagnóstico clínico, **NO** evalúa síndrome de burnout, MBI, UWES-9 ni ningún test sancionado.
- 🚫 El código **no debe usarse** para tomar decisiones individuales sobre contratación, despido, ascenso o sanción de personas.
- 🏥 Los resultados se **asocian con indicadores de salud laboral**; la relación con **accidentabilidad específica es débil** según la evidencia disponible (SUSESO/ISTAS21, Chile: rho -0.29 a -0.34). **No se afirma que el modelo "prevenga accidentes".**
- 🧪 El dataset de demostración psicosocial es **sintético** (estructura conocida, sin datos reales). El dataset predictivo es IBM HR Analytics (público de Kaggle).

---

## 📸 Preview del dashboard

<!-- TODO: agregar screenshot real 1200x700 del dashboard (métricas + histograma JD-R + disclaimer + imagen SHAP) -->

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
    - Carga de CSV/Excel con ruta configurable.
    - Mapeo dinámico español-inglés para columnas en ambos idiomas.
    - `validar_columnas()`: validación estricta del esquema mínimo IBM HR (8 columnas).
    - `agregar_indice_compuesto_jdr(df)`: cálculo único del indicador (fuente de verdad).
2. **📊 Dashboard interactivo Streamlit** (`dashboard/app.py`):
    - 3 métricas de rotación globales.
    - Filtro dinámico por **Departamento**.
    - 2 histogramas Plotly (horas extra / satisfacción laboral) segmentados por Attrition.
    - **Sección Índice JD-R**: métrica promedio + histograma 0..14 + disclaimer ético `st.warning()`.
    - **Sección Modelo Predictivo**: métricas de performance (accuracy, precision, recall, F1), predicción por empleado seleccionable, y explicación SHAP dinámica por predicción individual.
    - **Sección Perfiles Psicosociales**: vía psicométrica basada en el Cuestionario de Evaluación de Riesgo Psicosocial del Ministerio del Trabajo del Ecuador (58 ítems), con fiabilidad (α/ω), validez de constructo (AFE) y validez de criterio.
3. **🤖 Modelo predictivo** (`src/modelo.py`):
     - RandomForestClassifier (scikit-learn) entrenado y serializado con joblib.
     - 5 funciones modulares: `entrenar_modelo()`, `evaluar_modelo()`, `guardar_modelo()`, `cargar_modelo()`, `obtener_importancias()`.
     - Accuracy: ~87.4% en dataset de prueba. Feature más importante: `MonthlyIncome`.
     - Documentación completa: [`docs/API_MODELO.md`](docs/API_MODELO.md).
4. **📄 Reporte PDF automatizado** (`src/reportes.py`):
    - Encabezado, resumen general, sección JD-R (con disclaimer), sección SHAP (con disclaimer).
5. **📘 Script de lectura conceptual** (`src/marco_psicologico.py`):
    - Compara promedio del índice JD-R entre empleados que renunciaron vs los que se quedaron (validación exploratoria del dataset demo).
6. **🧬 Vía psicométrica con instrumento oficial MDT** (`src/psicometria/`):
    - **Instrumento oficial del MDT-Ecuador**: 58 ítems, escala Likert 1-4, sumatoria simple con puntos de corte oficiales (Tablas 3-4). Fuente primaria transcrita: `docs/fuentes/guia_aplicacion_cuestionario_mdt_ecuador.pdf`.
    - **Clasificación oficial de riesgo**: distribución Bajo/Medio/Alto por dimensión, subescala y global.
    - Fiabilidad: Cronbach α y McDonald ω (dimensiones de 3+ ítems); **Spearman-Brown y marca "descriptiva, no psicométrica" para las subescalas de 2 ítems** (acoso sexual, acoso laboral, doble presencia, condiciones del trabajo, salud auto percibida) — nunca se reporta α como válido ahí.
    - Validez de constructo: análisis factorial **exploratorio** (el MDT no postula estructura bidimensional).
    - Validez de criterio: dirección univariada (estable frente a multicolinealidad) + regresión logística multivariada con nota de cautela.
    - **Validación cruzada k-fold ESTRATIFICADA (k=5)** con **F1 macro y accuracy balanceada** (no accuracy simple); con N < 100 el modelo se declara "exploratorio, no generalizable".
    - **Campo demográfico tipo_jornada** (turno fijo/rotativo; Aguilar Ortega & Vega Cauich, 2024, n=597).
    - CLI: `python -m src.psicometria <respuestas.csv> --pdf`.
    - Documentos: [`docs/CUESTIONARIO.md`](docs/CUESTIONARIO.md), [`docs/CONSENTIMIENTO.md`](docs/CONSENTIMIENTO.md), [`docs/PROTOCOLO_SITUACIONES_DETECTADAS.md`](docs/PROTOCOLO_SITUACIONES_DETECTADAS.md), [`docs/GUIA_RECOLECCION.md`](docs/GUIA_RECOLECCION.md).
7. **🧪 Simulador de N vs α/ω** (`src/psicometria/simulador_muestra.py`): fija el N objetivo de campo con las dimensiones reales del instrumento (no con reglas genéricas).
8. **🛠️ Simulador de intervención informado por evidencia externa** (`src/simulador_intervencion.py`): combina la prioridad local (correlaciones dimensión-rotación) con tamaños de efecto de meta-análisis publicados (Richardson & Rothstein, 2008: d=0.526, IC 95% 0.364-0.687) y el menú de intervenciones HSE/OMS de la guía oficial. CLI: `python -m src.simulador_intervencion`.

---

## 🔄 Pipeline ETL y flujo de datos

### Flujo de datos

```
[Dataset IBM HR (CSV/Excel)]
         │
         ▼
┌─────────────────────────────┐
│  src/datos.py               │
│  1. cargar_datos()          │  ← Lee CSV/Excel, maneja encoding
│  2. validar_columnas()      │  ← Valida esquema mínimo (8 col)
│  3. renombrar_columnas_es() │  ← Mapeo ES→EN si aplica
│  4. agregar_indice_jdr()    │  ← Calcula índice compuesto JD-R
└─────────────────────────────┘
         │
         ├──► [dashboard/app.py]  ← Consume DataFrame, renderiza UI
         │
         ├──► [src/modelo.py]    ← Entrena RandomForestClassifier
         │                         → output/modelo_vigia.joblib
         │
         └──► [src/reportes.py]  ← Genera PDF con fpdf2
```

### Escalabilidad con datos reales

El pipeline está diseñado para escalar con datos reales de RRHH. Para ello:

1. **Carga**: `cargar_datos(ruta="...")` acepta cualquier ruta. Con datos reales, el archivo se coloca en `data/` o se pasa la ruta completa.
2. **Validación**: `validar_columnas()` garantiza que el esquema sea consistente antes de cualquier procesamiento. Si el schema cambia, el error es inmediato y explícito.
3. **Mapeo**: `renombrar_columnas_es()` detecta automáticamente columnas en español y las traduce al esquema interno en inglés. Con datos de diferentes fuentes, basta con actualizar `MAPEO_ES` en `src/datos.py`.
4. **Índice JD-R**: `agregar_indice_compuesto_jdr()` es la única fuente de verdad del cálculo del índice. Cualquier cambio en la fórmula se hace en un solo lugar.
5. **Modelo**: `entrenar_modelo()` recibe cualquier DataFrame con el esquema correcto. Para datos reales con más features, el modelo los incorpora automáticamente.

### Limitaciones actuales (honestidad técnica)

- **No hay data drift detection**: el modelo no detecta cambios en la distribución de datos a lo largo de tiempo.
- **No hay monitoreo de calidad de datos**: no hay alertas automáticas si los datos entrantes tienen anomalías.
- **No hay pipeline automatizado**: el entrenamiento se ejecuta manualmente con `python src/modelo.py`. Para automatizar, se necesita un orquestador (Airflow, Prefect, etc.) que no está implementado.
- **El dataset predictivo es de demo**: los resultados provienen del dataset público IBM HR Analytics de Kaggle, no de datos reales de empleados.
- **Limitación de N con el instrumento MDT (documentada, no forzada):** con 58 ítems, la regla clásica de 10 sujetos por ítem (Nunnally & Bernstein, 1994) exigiría **N ≈ 580** para un AFE estable — **inviable de recolectar en este proyecto**. La meta original de 150 NO se fuerza como requisito de AFE:
    - La simulación (`src/psicometria/simulador_muestra.py`) muestra que la fiabilidad α/ω de las dimensiones principales (4-6 ítems) es estable (≥ 0.85) a cualquier N de 30-400; N=150 da α/ω ≈ 0.90-0.95.
    - **N objetivo: ≥ 100 (mínimo indicativo, alineado con el umbral de la validación cruzada); 150-300 recomendado.** Por debajo de 100, los resultados se declaran "exploratorios, no generalizables".
    - A N alcanzable, el AFE se declara **exploratorio** y las subescalas de 2 ítems **descriptivas**.
    - La dimensión "Otros puntos importantes" (24 ítems de 8 subconstructos) converge a α ≈ 0.68 a **cualquier N**: límite **estructural**, no de muestra (la guía oficial, pág. 17, la define como "punto de partida para evaluaciones más específicas").

---

## 🌾 Cómo recolectar tus datos reales (paso a paso)

> Esta es la guía práctica para el trabajo de campo (Fase 10). El detalle completo está
> en [`docs/GUIA_RECOLECCION.md`](docs/GUIA_RECOLECCION.md).

### Paso 1 — Preparar los documentos

1. **Consentimiento informado:** usa [`docs/CONSENTIMIENTO.md`](docs/CONSENTIMIENTO.md) tal cual (ya incluye temas de acoso, anonimato reforzado y LOPDP).
2. **Protocolo de situaciones detectadas:** lee [`docs/PROTOCOLO_SITUACIONES_DETECTADAS.md`](docs/PROTOCOLO_SITUACIONES_DETECTADAS.md) ANTES de recolectar — define qué hacer si una respuesta revela una situación real.
3. **Cuestionario:** usa [`docs/CUESTIONARIO.md`](docs/CUESTIONARIO.md) (58 ítems oficiales del MDT, escala 1-4, sin cambiar texto ni orden).

### Paso 2 — Configurar el formulario (Google Forms)

1. Crea un formulario anónimo: **NO recopilar correos**, NO limitar a 1 respuesta por persona (eso obligaría a iniciar sesión).
2. Primera página: el consentimiento completo, con una pregunta obligatoria "¿Acepto participar?" (Sí/No).
3. Página de datos generales: los 10 campos del Anexo 11.1 + `tipo_jornada` (ver CUESTIONARIO.md, con las opciones exactas como lista desplegable).
4. Página(s) de ítems: los 58 ítems en el orden oficial, cada uno como opción múltiple con las 4 opciones de la escala (Completamente de acuerdo=4, Parcialmente de acuerdo=3, Poco de acuerdo=2, En desacuerdo=1) + opción "NR".
5. Última página: observaciones y comentarios (texto libre, opcional) + `intencion_rotacion` (1 ítem binario: 1 = piensa buscar otro trabajo).

### Paso 3 — Recolectar

- Pide autorización formal a RRHH/dirección y socializa la aplicación con todo el personal.
- Objetivo: **≥ 100 respondientes** (mínimo indicativo); 150-300 recomendado. Si no llegas a 100, los resultados se declaran "exploratorios, no generalizables" — no fuerces la meta.
- Duración por persona: 15-20 minutos. Colecta en 2-4 semanas.

### Paso 4 — Exportar los datos

1. En Google Forms: Respuestas → icono de Google Sheets → archivo → Descargar → CSV.
2. **Renombra las columnas** para que coincidan EXACTAMENTE con `data/encuestas/plantilla_respuestas.csv`: `fecha, provincia, ciudad, area_trabajo, nivel_instruccion, antiguedad, edad, autoidentificacion_etnica, genero, tipo_jornada, item_01 ... item_58, intencion_rotacion`.
3. Los valores de los ítems deben ser enteros **1-4** (recodifica el texto de las opciones a números: Completamente de acuerdo=4, Parcialmente de acuerdo=3, Poco de acuerdo=2, En desacuerdo=1, NR=vacío).
4. `intencion_rotacion`: 0/1. Guarda en UTF-8 como `data/encuestas/respuestas.csv` (la plantilla solo tiene encabezados: no la cargues como datos).

### Paso 5 — Validar y clasificar

```bash
# Validación psicométrica completa + clasificación oficial + reporte PDF
python -m src.psicometria data/encuestas/respuestas.csv --pdf

# Simulador de intervención (prioriza y dimensiona intervenciones)
python -m src.simulador_intervencion data/encuestas/respuestas.csv

# Dashboard (detecta automáticamente data/encuestas/respuestas.csv)
streamlit run dashboard/app.py
```

- El reporte incluye: clasificación de riesgo con los **puntos de corte oficiales** (Tablas 3-4), fiabilidad (α/ω; **Spearman-Brown para subescalas de 2 ítems**), AFE exploratorio, dirección univariada, regresión multivariada con cautela y **validación cruzada estratificada (F1 macro / accuracy balanceada)**.
- Si faltan ítems, hay valores fuera de rango o la muestra es < 100, el CLI lo avisa automáticamente.

---

## 🧱 Stack tecnológico (al día con el código actual)

| Capa | Librería | Propósito |
|---|---|---|
| Lenguaje | Python 3.11+ | Runtime. |
| Dashboard | Streamlit | Interfaz web interactiva. |
| Datos | pandas | DataFrames y validación. |
| ML | scikit-learn | RandomForestClassifier, métricas. |
| Explicabilidad | SHAP | Explicación dinámica por predicción. |
| Serialización | joblib | Guardar/cargar modelo entrenado. |
| Viz | Plotly Express | Gráficas interactivas. |
| Reportes | fpdf2 | Exportación PDF. |
| Robustez imports | `pathlib` + `sys.path` idempotente | Funciona desde cualquier cwd. |

> Todas las dependencias están declaradas en `requirements.txt`. El modelo serializado (`output/modelo_vigia.joblib`) se genera ejecutando `python src/modelo.py`.

---

## 🏗️ Arquitectura modular

```mermaid
flowchart LR
    A[data/WA_Fn-UseC_-HR-Employee-Attrition.csv] --> B
    B[src/datos.py\n(carga + validacion + indice JD-R)]
    B --> C[dashboard/app.py\nUI interactiva Streamlit]
    B --> D[src/reportes.py\nreporte PDF]
    B --> E[src/marco_psicologico.py\nanalisis conceptual]
    B --> F[src/modelo.py\nentrenamiento + evaluacion]
    F --> G[output/modelo_vigia.joblib\nmodelo serializado]
    C --> H[src/modelo\ncargar_modelo + evaluar_modelo]
    H --> I[Explicacion SHAP dinamica\npor empleado]

    F --> I
    I --> C
    D --> J[output/reporte_vigia_rh.pdf]
```

**Diseño clave**: la fórmula del índice JD-R vive **en un solo lugar** (`src/datos.py`), y el modelo predictivo vive **en un solo módulo** (`src/modelo.py`). No existe duplicación en el repositorio.

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

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```
Incluye: streamlit, pandas, plotly, fpdf2, openpyxl, scikit-learn, shap, matplotlib, psutil.

### 3. Generar el modelo predictivo (primera vez)
```bash
python src/modelo.py
# Genera output/modelo_vigia.joblib y muestra métricas.
# Solo necesario una vez; el dashboard usa el modelo serializado.
```

### 4. Ejecutar el dashboard
```bash
streamlit run dashboard/app.py
```
Abre `http://localhost:8501` en tu navegador.

### 5. (Opcional) Generar reporte PDF
```bash
python src/reportes.py
# Salida: output/reporte_vigia_rh.pdf
```

### 6. (Opcional) Análisis conceptual JD-R
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
│   ├── WA_Fn-UseC_-HR-Employee-Attrition.csv   # Dataset demo IBM
│   └── encuestas/
│       └── plantilla_respuestas.csv  # Plantilla de respuestas psicométricas
├── src/
│   ├── __init__.py               # Paquete Python
│   ├── datos.py                  # Núcleo: carga + validación + índice JD-R + mapeo ES-EN
│   ├── modelo.py                 # Modelo predictivo: entrenamiento, evaluación, serialización
│   ├── explicabilidad.py         # Explicabilidad SHAP por predicción
│   ├── reportes.py               # Generación PDF (FPDF2)
│   ├── marco_psicologico.py      # Lectura conceptual del índice
│   ├── psicometria/              # Vía psicométrica con instrumento oficial MDT
│   │   ├── __init__.py
│   │   ├── instrumento.py        # Definición del cuestionario oficial (58 ítems, Tablas 3-4)
│   │   ├── puntuaciones.py       # Sumatoria simple + clasificación oficial de riesgo
│   │   ├── fiabilidad.py         # Cronbach α + McDonald ω + Spearman-Brown (2 ítems)
│   │   ├── validacion.py         # AFE + regresión logística + validación cruzada estratificada
│   │   ├── simulador_muestra.py  # Simulador N vs α/ω (fija el N objetivo)
│   │   ├── ejemplos_datos.py     # Datos sintéticos de demostración (+tipo_jornada)
│   │   ├── reporte.py            # Reporte de validación (consola + PDF)
│   │   ├── cli.py                # CLI: python -m src.psicometria
│   │   ├── __main__.py           # Entry point del paquete
│   │   └── vista_dashboard.py    # Sección "Perfiles psicosociales"
│   ├── simulador_intervencion.py # Simulador de intervención (evidencia externa)
│   ├── utils/
│   │   ├── logger.py             # VigiaLogger: logging estructurado
│   │   └── __init__.py
│   └── dashboard/
│       ├── __init__.py
│       ├── error_handler.py      # VigiaError, ErrorDatos, ErrorMapeo, ErrorCalculo
│       └── ui_components.py      # Componentes UI reutilizables + modelo predictivo
├── docs/
│   ├── API_MODELO.md             # Documentación de la API del modelo
│   ├── CUESTIONARIO.md           # Instrumento oficial MDT (58 ítems, escala 1-4)
│   ├── CONSENTIMIENTO.md         # Consentimiento informado (acoso, LOPDP)
│   ├── PROTOCOLO_SITUACIONES_DETECTADAS.md  # Protocolo de situaciones detectadas
│   ├── GUIA_RECOLECCION.md       # Guía de recolección de datos de campo
│   └── fuentes/                  # Fuente primaria: PDF oficial del MDT + extracto
├── output/
│   ├── modelo_vigia.joblib       # Modelo predictivo serializado
│   ├── shap_resumen.png          # Plot SHAP precomputado
│   └── reporte_vigia_rh.pdf      # Último reporte generado
├── notebooks/                    # Análisis exploratorios (WIP)
├── requirements.txt
├── start_dashboard_safe.py       # Inicio seguro con monitoreo de procesos
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

| Fase | Descripción | Estado |
|---|---|---|
| ✅ Fase 1 | Pipeline de datos, mapeo ES-EN, validación, dashboard descriptivo | **Completada** |
| ✅ Fase 2 | Modelo predictivo scikit-learn, serialización joblib, explicabilidad SHAP dinámica | **Completada** |
| ✅ Fase 3 | Tests unitarios (`pytest`) sobre validación, índice JD-R y componentes de dashboard. | **Completada** |
| ✅ Fase 4 | Dockerfile para despliegue reproducible. | **Completada** |
| ✅ Fase 5 | GitHub Actions CI/CD pipeline. | **Completada** |
| ✅ Fase 6 | Documentación de la API del modelo (`docs/API_MODELO.md`). | **Completada** |
| ✅ Fase 7 | Documentación del pipeline ETL y escalabilidad. | **Completada** |
| ✅ Fase 8 | Vía psicométrica (`src/psicometria`): instrumento MDT-Ecuador (58 ítems), fiabilidad, AFE, validez de criterio. Validación con datos de campo pendiente. | **Completada** |
| ✅ Fase 9 | Herramientas de campo: CLI de validación, plantilla, cuestionario, consentimiento, guía. | **Completada** |
| ✅ Fase 10 (preparación) | Pivote al instrumento oficial MDT (58 ítems), protocolo ético LOPDP, validación cruzada estratificada, simuladores de N e intervención. Trabajo de campo pendiente. | **Preparada — recolección con el usuario** |
| 🔜 Fase 11 | Recolección de datos reales de campo y validación empírica (≥100 respondientes; meta deseada 150-300). | **Pendiente (trabajo de campo)** |
| 🔜 Fase 12 | Tests de integración para el dashboard completo. | **Pendiente** |
| 🔜 Fase 13 | Despliegue en Docker + Streamlit Cloud con CI/CD. | **Pendiente** |

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
