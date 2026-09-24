# Guía de Recolección de Datos (Trabajo de Campo — Fase 10)

> Documento operativo para recolectar respuestas reales con el **instrumento oficial del
> MDT-Ecuador** (Cuestionario de Evaluación de Riesgo Psicosocial, 58 ítems) y validar
> empíricamente la vía psicosocial de Vigía RH. Léelo completo antes de comenzar.

---

## 1. Resumen del objetivo

Recolectar respuestas anónimas de una muestra de trabajadores/servidores para ejecutar la
validación psicométrica del instrumento oficial MDT y clasificar el riesgo con los
puntos de corte oficiales, dando **validez empírica** a la vía psicosocial de Vigía RH.

## 2. Requisitos previos (autorización y ética — no negociable)

- **Autorización institucional:** si el trabajo de campo se realiza dentro de una empresa,
  obtener autorización formal de RRHH/dirección.
- **Consentimiento informado:** cada participante debe leer `docs/CONSENTIMIENTO.md` y
  aceptar. Incluye menciones explícitas de **acoso** y el reforzamiento del anonimato.
- **Protocolo de situaciones detectadas:** leer `docs/PROTOCOLO_SITUACIONES_DETECTADAS.md`
  ANTES de recolectar (qué hacer si una respuesta revela una situación real).
- **Revisión ética:** si lo exige tu institución académica, solicitar la aprobación del
  comité de ética. Para un portafolio, el consentimiento + protocolo suelen ser suficientes.

## 3. Tamaño de muestra (crítico — fijado por simulación)

> **⚠️ Limitación explícita y honesta:** con el instrumento MDT de **58 ítems**, la regla
> clásica de **10 sujetos por ítem** (Nunnally & Bernstein, 1994) exigiría **N ≈ 580**
> para un análisis factorial (AFE) estable. Esa meta es **inviable de recolectar** en el
> alcance de este proyecto (portafolio). Por eso:

- El **N objetivo se fija por simulación** con las dimensiones reales del instrumento
  (`src/psicometria/simulador_muestra.py`): la fiabilidad (α/ω) de las **dimensiones
  principales (4-6 ítems)** es estable (≥ 0.85) a cualquier N simulado de 30 a 400, con
  N=150 dando α/ω ≈ 0.90-0.95 en datos sintéticos.
- **La meta original de 150 NO se fuerza como requisito de AFE**; a N alcanzable, el AFE
  se declara **exploratorio** y las subescalas de 2 ítems **descriptivas**.

| Nivel | Respondientes | Uso |
|---|---|---|
| Mínimo indicativo | **100** | Resultados exploratorios/no generalizables (umbral de validación cruzada) |
| Recomendado | **150-300** | Fiabilidad α/ω estable por dimensión; AFE exploratorio |
| Ideal (10:1 con 58 ítems) | **~580** | AFE estable — **inviable en este proyecto (documentado)** |

> **Nunca valides con menos de 100.** Por debajo, los resultados se declaran
> "exploratorios, no generalizables". Si N final < 100, el README/reporte lo deben decir
> explícitamente.

## 4. Muestreo

- **Aleatorio/representativo** si es posible (cada trabajador con igual probabilidad).
- Si es por conveniencia (voluntarios), decláralo como limitación.
- **Heterogeneidad deseada:** incluir distintas áreas (Administrativa/Operativa), edades,
  géneros, antigüedad y **tipo de jornada (turno fijo/rotativo)**.
- Evita muestrear solo un equipo o un departamento.

## 5. Instrumento

- Usa el cuestionario oficial de `docs/CUESTIONARIO.md` (texto literal del Anexo 11.1 del
  PDF del MDT). **No cambiar la escala (Likert 1-4), el texto ni el orden de los ítems.**
- **Formato recomendado:** Google Forms (anónimo, sin recopilar correos) para digitalizar
  respuestas automáticamente. Alternativa: Excel/CSV con la plantilla.
- Incluye la página de consentimiento al inicio del formulario.
- Duración esperada: 15-20 minutos (según la guía oficial).

## 6. Administración

- Entrega el enlace del formulario y explica brevemente el propósito y la anonimidad.
- Aclara que los ítems de **acoso** son de percepción y que pueden marcar "NR" si no
  quieren responder.
- Aclara que no hay respuestas correctas ni incorrectas y que los resultados se
  socializarán a los participantes.
- Colecta respuestas en un periodo definido (ej. 2-4 semanas).

## 7. Formato del archivo de datos (CRÍTICO)

El archivo debe seguir **exactamente** la plantilla `data/encuestas/plantilla_respuestas.csv`
(69 columnas: 10 de datos generales + 58 ítems + 1 criterio).

**Columnas obligatorias (en este orden):**
```
fecha,provincia,ciudad,area_trabajo,nivel_instruccion,antiguedad,edad,
autoidentificacion_etnica,genero,tipo_jornada,
item_01,item_02,...,item_58,
intencion_rotacion
```

- Cada **columna de ítem** es un ítem oficial; cada **fila** es un respondiente.
- Los valores de los ítems son **enteros 1-4** (escala oficial: 4 = Completamente de
  acuerdo, 1 = En desacuerdo). "NR" o celda vacía se tratan como faltante.
- Los campos generales usan las opciones del Anexo 11.1 (ver CUESTIONARIO.md);
  `tipo_jornada`: `turno_fijo` / `turno_rotativo` / `otro`.
- `intencion_rotacion` es el **criterio externo** (el cuestionario oficial no lo incluye):
  binario 0/1 (ej. 1 = piensa buscar otro trabajo). El pipeline la trata como binaria.
- **No** cambiar los nombres de columna. Si un ítem no fue respondido, dejar la celda vacía.
- Guardar en **UTF-8** con extensión `.csv`.

> ⚠️ **Advertencia:** la plantilla `plantilla_respuestas.csv` contiene solo encabezados.
> No la cargues como datos. Rellena debajo de los encabezados.

## 8. Ejecutar la validación

Ubicado en la raíz del proyecto:

```bash
# Con un archivo de datos real
python -m src.psicometria data/encuestas/respuestas.csv --pdf

# Solo consola
python -m src.psicometria data/encuestas/respuestas.csv

# Ver ayuda
python -m src.psicometria --help
```

- La consola imprime el reporte: clasificación de riesgo con puntos de corte oficiales,
  fiabilidad (α/ω; Spearman-Brown para subescalas de 2 ítems), AFE exploratorio y
  validez de criterio.
- `--pdf` genera `output/reporte_validacion_psicometria.pdf`.

**Advertencias automáticas:** el CLI avisa si faltan ítems, si la muestra es < 100
(N objetivo por simulación), o si falta la columna de outcome.

## 9. Interpretación de los resultados

| Indicador | Qué evalúa | Buen resultado |
|---|---|---|
| **Riesgo por dimensión** (Tablas 3-4 oficiales) | Clasificación Bajo/Medio/Alto | Distribución informada por los puntos de corte oficiales |
| **Cronbach α / McDonald ω** (3+ ítems) | Fiabilidad por dimensión principal | ≥ 0.70 |
| **Spearman-Brown** (2 ítems) | Subescalas de 2 ítems — **descriptivas, no psicométricas** | Informativo, no inferencial |
| **Análisis factorial** | Validez de constructo — **exploratorio** (el MDT no postula 2 factores) | Exploratorio |
| **Regresión logística / validación cruzada** | Validez de criterio (relación con rotación) | F1 macro y balanced accuracy (no accuracy simple) |

- **Cautela (no negociable):** los resultados se **asocian con indicadores de salud
  laboral**; la relación con **accidentabilidad específica es débil** según la evidencia
  disponible (SUSESO/ISTAS21, Chile: rho -0.29 a -0.34). **No afirmar que el modelo
  "previene accidentes".**
- Si la fiabilidad es < 0.70 en una dimensión principal, revisar la redacción de ítems
  problemáticos y la calidad de datos.
- La dimensión "Otros puntos importantes" es heterogénea por diseño (24 ítems de 8
  subconstructos); la simulación muestra que su α converge a ≈0.68 a cualquier N. Analizar
  sus subescalas por separado (la propia guía la define como "punto de partida para
  evaluaciones más específicas", pág. 17).

## 10. Ética (no negociable)

- Datos **anónimos** y **grupales**.
- **Nunca** usar para decisiones individuales de contratación, despido, ascenso o sanción.
- Reportar solo agregados. No mostrar filas individuales.
- Ser honesto sobre el tamaño de muestra y el tipo de muestreo en el reporte.
- Seguir el protocolo de situaciones detectadas (sección 2).

## 11. Lista de verificación previa al campo

- [ ] Autorización institucional obtenida.
- [ ] Consentimiento informado redactado (con temas de acoso y LOPDP) y aprobado.
- [ ] Protocolo de situaciones detectadas leído y comprometido.
- [ ] Cuestionario revisado (58 ítems oficiales, escala 1-4, sin cambios de texto/orden).
- [ ] Formulario anónimo configurado (sin recopilar correos).
- [ ] Plantilla CSV verificada (69 columnas).
- [ ] CLI probado con datos sintéticos (`python -m src.psicometria`).
- [ ] Objetivo de muestra definido (≥ 100; limitación de AFE documentada).
