# 🔎 Vigía RH — Análisis agregado de riesgo psicosocial laboral y rotación

Herramienta de People Analytics para el **análisis agregado** de riesgo psicosocial laboral y
rotación de personal, construida con Streamlit, pandas, Plotly y scikit-learn.
La vía psicosocial utiliza el **Cuestionario de Evaluación de Riesgo Psicosocial del Ministerio
del Trabajo del Ecuador** (58 ítems, escala Likert 1-4, con sus puntos de corte oficiales),
transcrito de la fuente primaria en [`docs/fuentes/`](docs/fuentes/).

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-red?logo=streamlit)
![scikit-learn](https://img.shields.io/badge/scikit--learn-clasificaci%C3%B3n-FFCB2E?logo=scikit-learn)
![Tests](https://img.shields.io/badge/tests-224%20passing-brightgreen)
![License](https://img.shields.io/badge/Licencia-MIT-green)

---

## ⚠️ Aviso ético — léeme antes de usar

- **Herramienta de apoyo, NO certificada.** No sustituye la práctica profesional de psicología
  organizacional ni ningún proceso oficial de evaluación.
- **No evalúa personas individuales.** Los resultados se presentan **a nivel agregado (grupal)**
  y los grupos con **menos de 5 respondientes (n < 5) se ocultan** para proteger la anonimidad.
- **No debe usarse para decisiones sobre personas concretas** (contratación, despido, ascenso,
  sanción u otras medidas individuales).
- **La validación psicométrica con datos reales está en construcción.** Los datos psicosociales
  que incluye hoy son **sintéticos, solo de demostración**; el trabajo de campo con el
  instrumento oficial está pendiente.
- **Privacidad:** la aplicación de la encuesta prevista es anónima, con consentimiento informado
  y bajo la Ley Orgánica de Protección de Datos Personales (**LOPDP**, Ecuador). Ver
  [`docs/CONSENTIMIENTO.md`](docs/CONSENTIMIENTO.md).

---

## 🌐 Dashboard público

**👉 [Abrir el dashboard](https://vigia-rh-iomyd5oyurcsmkmfssdkzs.streamlit.app)**

> Si la app estaba inactiva, la primera carga puede tardar 1-2 minutos.

---

## 📸 Capturas

<!-- Capturas pendientes de agregar en docs/img/:
![Pestaña Inicio del dashboard](docs/img/01_inicio.png)
![Pestaña Riesgo psicosocial](docs/img/02_riesgo_psicosocial.png)
![Pestaña Rotación](docs/img/03_rotacion.png)
![Pestaña Simulador de escenario hipotético](docs/img/04_simulador.png)
-->

---

## 🧭 Qué hace

El dashboard (`dashboard/app.py`) tiene **4 pestañas**, con el riesgo psicosocial como vista principal:

1. **🏠 Inicio** — qué es Vigía RH, aviso ético y limitaciones.
2. **🧠 Riesgo psicosocial** — evaluación psicométrica **grupal** con el Cuestionario de
   Evaluación de Riesgo Psicosocial del MDT-Ecuador (58 ítems, escala 1-4): clasificación de
   riesgo con los **puntos de corte oficiales** del instrumento, fiabilidad (α de Cronbach y ω
   de McDonald; **Spearman-Brown marcado como descriptivo** para las subescalas de 2 ítems),
   análisis factorial **exploratorio**, validez de criterio y validación cruzada estratificada.
   Todo se reporta a nivel agregado; los grupos con **n < 5 se ocultan**.
3. **🛠️ Simulador (escenario hipotético)** — dimensiona intervenciones organizacionales
   combinando la prioridad local con tamaños de efecto publicados en la literatura
   (Richardson & Rothstein, 2008: **d = 0.526**). Es un **escenario hipotético de
   demostración**: no garantiza resultados ni establece relaciones causales.
4. **🧪 Módulo demostrativo (rotación — IBM HR)** — métricas agregadas de rotación sobre el
   dataset público IBM HR Analytics: filtros por departamento, histogramas segmentados,
   índice compuesto JD-R (fórmula pública y transparente en [`src/datos.py`](src/datos.py))
   y un **modelo de clasificación demostrativo** (RandomForest) con evaluación agregada por
   grupo (protección **n < 5**) y explicabilidad SHAP global.

Referencia numérica del demo (dataset IBM HR, no interpretable como validación): el promedio
del índice JD-R es **7.18** entre quienes permanecen y **8.35** entre quienes renuncian
(verificable con `python src/marco_psicologico.py`).

Además del dashboard, el repo incluye herramientas de línea de comandos y de campo:

```bash
# Validación psicométrica + clasificación + reporte PDF
python -m src.psicometria data/encuestas/respuestas.csv --pdf

# Simulador de intervención (escenario hipotético)
python -m src.simulador_intervencion data/encuestas/respuestas.csv
```

---

## 🚀 Ejecución en local

Requisitos: Python 3.11+ y Git. Todas las dependencias están en [`requirements.txt`](requirements.txt).

```bash
# 1. Clonar
git clone https://github.com/isaacdayana16-rgb/vigia-rh.git
cd vigia-rh

# 2. Entorno virtual
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# 3. Dependencias
pip install -r requirements.txt

# 4. Generar el modelo demostrativo (solo la primera vez)
python src/modelo.py
# Genera output/modelo_vigia.joblib y muestra sus métricas en consola.

# 5. Levantar el dashboard
streamlit run dashboard/app.py
# Abre http://localhost:8501 en tu navegador.
```

Opcionales: `python src/reportes.py` (reporte PDF en `output/`) y
`python src/marco_psicologico.py` (promedios del índice JD-R por grupo de rotación).

---

## 🧪 Tests

La suite tiene **224 tests** (pytest), todos en verde en el último commit:

```bash
.\venv\Scripts\pytest -q        # Windows (PowerShell)
pytest -q                        # con el entorno virtual activado
```

---

## 📂 Estructura del proyecto

```
vigia-rh/
├── dashboard/
│   └── app.py                    # Dashboard Streamlit (4 pestañas)
├── data/
│   ├── WA_Fn-UseC_-HR-Employee-Attrition.csv   # Dataset demo IBM HR (público)
│   ├── RH_Empresa_Ejemplo_Ecuador.xlsx         # Dataset demo en español
│   └── encuestas/
│       └── plantilla_respuestas.csv            # Plantilla de respuestas (solo encabezados)
├── docs/
│   ├── API_MODELO.md             # Documentación de la API del modelo
│   ├── CONSENTIMIENTO.md         # Consentimiento informado (LOPDP)
│   ├── CUESTIONARIO.md           # Instrumento oficial MDT (58 ítems, escala 1-4)
│   ├── GUIA_RECOLECCION.md       # Guía de recolección de datos de campo
│   ├── PROTOCOLO_SITUACIONES_DETECTADAS.md     # Protocolo ante situaciones detectadas
│   └── fuentes/                  # PDF oficial del MDT-Ecuador + extracto de texto
├── src/
│   ├── datos.py                  # Carga, validación, mapeo ES-EN e índice JD-R
│   ├── modelo.py                 # RandomForest: entrenamiento, evaluación, serialización
│   ├── explicabilidad.py         # Explicabilidad SHAP
│   ├── reportes.py               # Reporte PDF (fpdf2)
│   ├── marco_psicologico.py      # Lectura conceptual del índice JD-R
│   ├── simulador_intervencion.py # Simulador de intervención (escenario hipotético)
│   ├── psicometria/              # Vía psicométrica MDT: instrumento, puntuaciones,
│   │                             #   fiabilidad, validación, calidad de datos, CLI, reporte
│   ├── dashboard/                # Componentes UI reutilizables + manejo de errores
│   └── utils/                    # Logger estructurado
├── tests/                        # Suite pytest (224 tests)
├── output/                       # Modelo serializado, reportes y gráficas generadas
├── notebooks/                    # Análisis exploratorios
├── .github/workflows/test.yml    # CI (GitHub Actions)
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
└── start_dashboard_safe.py       # Inicio del dashboard con monitoreo de procesos
```

---

## ⚠️ Limitaciones y alcance

- **Dataset de rotación:** IBM HR Analytics Employee Attrition & Performance es un dataset
  **público y sintético** (Kaggle), igual que el archivo demo en español
  (`data/RH_Empresa_Ejemplo_Ecuador.xlsx`). Ninguna cifra de esta vía proviene de empleados reales.
- **Vía psicosocial:** espera **datos reales de campo**. La validación psicométrica con datos
  reales está **en construcción**; la recolección prevista requiere consentimiento informado,
  anonimato y un mínimo indicativo de **100 respondientes** (objetivo 150-300). Con la muestra
  alcanzable, los análisis se declaran exploratorios y las subescalas de 2 ítems, descriptivas.
- **Simulador:** es un **escenario hipotético** basado en literatura (tamaño de efecto
  d = 0.526, Richardson & Rothstein, 2008). No garantiza resultados ni permite afirmar
  relaciones de causa-efecto.
- **Desbalance de clases en el demo:** el modelo demostrativo alcanza accuracy **87.1 %** en el
  split de prueba del dataset IBM HR, con **recall bajo en la clase minoritaria (7.7 %)**:
  las métricas son demostrativas y no trasladables a otra población.
- **Relación con accidentabilidad:** la evidencia disponible (SUSESO/ISTAS21, Chile,
  rho -0.29 a -0.34) indica una asociación débil; esta herramienta **no afirma prevenir accidentes**.
- **Privacidad:** aplicación anónima, consentimiento informado y cumplimiento de la LOPDP
  (Ecuador). Los resultados se presentan solo de forma agregada con **n mínimo de 5**.

---

## 📜 Licencia y autor

- **Código:** licencia [MIT](LICENSE) © 2026.
- **Instrumento psicosocial:** Cuestionario de Evaluación de Riesgo Psicosocial del
  **Ministerio del Trabajo del Ecuador** (fuente oficial en [`docs/fuentes/`](docs/fuentes/)).
- **Dataset de rotación:** IBM HR Analytics Employee Attrition & Performance (público, Kaggle).
- **Referencia conceptual:** modelo Job Demands-Resources — Bakker & Demerouti (2007).

**Isaac Romeo Reyes Moreira**
Psicología Organizacional · People Analytics · Data Science
