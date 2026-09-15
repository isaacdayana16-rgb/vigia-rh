# Guía de Recolección de Datos (Trabajo de Campo)

> Documento operativo para recolectar respuestas reales de la encuesta psicosocial y
> validar el instrumento COPSOQ-ISTAS21. Léelo completo antes de comenzar.

---

## 1. Resumen del objetivo

Recolectar respuestas anónimas de una muestra de empleados para ejecutar la validación
psicométrica del instrumento y así dar **validez empírica** a la vía psicosocial de Vigía RH.

## 2. Requisitos previos (autorización)

- **Autorización institucional:** si el trabajo de campo se realiza dentro de una empresa,
  obtener autorización formal de RRHH/dirección.
- **Consentimiento informado:** cada participante debe leer `docs/CONSENTIMIENTO.md` y aceptar.
- **Revisión ética:** si lo exige tu institución académica, solicitar la aprobación del comité
  de ética. Para un portafolio, el consentimiento informado anónimo suele ser suficiente.

## 3. Tamaño de muestra (crítico)

Regla empírica: **10 sujetos por ítem** (Nunnally & Bernstein, 1994). El instrumento tiene
**13 ítems** + 3 de criterio = **16 variables**.

| Nivel | Respondientes | Uso |
|---|---|---|
| Mínimo | **150** | Análisis factorial estable (borde) |
| Recomendado | **200-300** | Resultados confiables |
| Óptimo | **300+** | Máxima estabilidad factorial |

> **Nunca valides con menos de 150.** Por debajo de eso, el análisis factorial es inestable.

## 4. Muestreo

- **Aleatorio/representativo** si es posible (cada empleado con igual probabilidad).
- Si es por conveniencia (voluntarios), decláralo como limitación. La generalización será limitada.
- **Heterogeneidad deseada:** incluir distintos departamentos, edades, géneros y antigüedad.
- Evita muestrear solo un equipo o un departamento.

## 5. Instrumento

- Usa el cuestionario de `docs/CUESTIONARIO.md`.
- **Formato recomendado:** Google Forms (anónimo, sin recopilar correos) para digitalizar
  respuestas automáticamente. Alternativa: Excel/CSV.
- Incluye la página de consentimiento al inicio del formulario.
- Escala Likert 1-5. No cambiar la escala ni el orden de los ítems.

## 6. Administración

- Entrega el enlace del formulario y explica brevemente el propósito y la anonimidad.
- Da tiempo suficiente (10-15 min). No presiones.
- Aclara que no hay respuestas correctas ni incorrectas.
- Colecta respuestas en un periodo definido (ej. 2-4 semanas).

## 7. Formato del archivo de datos (CRÍTICO)

El archivo debe seguir **exactamente** la plantilla `data/encuestas/plantilla_respuestas.csv`.

**Columnas obligatorias (en este orden):**
```
d_cant_1,d_cant_2,d_cant_3,d_emoc_1,d_emoc_2,d_emoc_3,
r_apoy_1,r_apoy_2,r_apoy_3,r_auto_1,r_auto_2,r_clar_1,r_clar_2,
intencion_rotacion
```

- Cada **columna** es un ítem; cada **fila** es un respondiente.
- Los valores de los ítems son **enteros 1-5**.
- `intencion_rotacion` es la **suma** de los 3 ítems de criterio (rango 3-15), o se puede
  dicotomizar (ej. ≥10 = 1, <10 = 0). El pipeline la trata como binaria si está en 0/1.
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

- La consola imprime el reporte de validación.
- `--pdf` genera `output/reporte_validacion_psicometria.pdf`.

**Advertencias automáticas:** el CLI avisa si faltan ítems, si la muestra es < 150, o si falta
la columna de outcome.

## 9. Interpretación de los resultados

| Indicador | Qué evalúa | Buen resultado |
|---|---|---|
| **Cronbach α / McDonald ω** | Fiabilidad (consistencia interna) por dimensión | ≥ 0.70 |
| **Análisis factorial** | Validez de constructo (demandas vs. recursos separados) | 2 factores separados |
| **Regresión logística** | Validez de criterio (relación con rotación) | demandas +, recursos − |

- Si la fiabilidad es < 0.70, revisar la redacción de ítems problemáticos.
- Si el AFE no separa en 2 factores, revisar el instrumento o la calidad de datos.
- Si los coeficientes no tienen la dirección JD-R esperada, sospechar datos ruidosos o muestra sesgada.

## 10. Ética (no negociable)

- Datos **anónimos** y **grupales**.
- **Nunca** usar para decisiones individuales de contratación, despido, ascenso o sanción.
- Reportar solo agregados. No mostrar filas individuales.
- Ser honesto sobre el tamaño de muestra y el tipo de muestreo en el reporte.

## 11. Lista de verificación previa al campo

- [ ] Autorización institucional obtenida.
- [ ] Consentimiento informado redactado y aprobado.
- [ ] Cuestionario revisado (13 ítems + 3 criterio).
- [ ] Formulario anónimo configurado (sin recopilar correos).
- [ ] Plantilla CSV verificada.
- [ ] CLI probado con datos sintéticos (`python -m src.psicometria`).
- [ ] Objetivo de muestra definido (≥150).