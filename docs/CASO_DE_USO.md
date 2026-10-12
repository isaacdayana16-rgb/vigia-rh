# Caso de uso FICTICIO — datos sintéticos

> **Este documento describe un caso completamente FICTICIO.** La empresa, las personas y todas
> las cifras marcadas como "ilustrativas" son inventadas con fines demostrativos. Las únicas
> cifras reales son las que provienen del dataset de demostración del repositorio (IBM HR
> Analytics y datos sintéticos incluidos en el código), y se identifican como tales.

---

## La empresa (inventada)

**Textitla Andina S.A.S.** es una empresa manufacturera ficticia de mediano tamaño, con sede en
una ciudad intermedia del Ecuador. Tiene 240 personas en planilla (cifra ilustrativa),
distribuidas en tres áreas: Producción, Ventas y Administración.

## El problema (ficticio)

En los últimos dos trimestres (escenario ilustrativo), Textitla Andina observa:

- Una **rotación anualizada del 22 %** (cifra ilustrativa), concentrada en Producción.
- Costos crecientes de reclutamiento e inducción, y pérdida de conocimiento operativo.
- Comentarios informales sobre **jornadas rotativas exhaustivas**, presión de plazos y poca
  claridad en los roles, aunque sin mediciones formales.

Gerencia pide a RRHH entender **qué está pasando a nivel agregado** y priorizar acciones, sin
incurrir en evaluaciones individuales.

## Cómo se usaría Vigía RH (flujo agregado, nunca individual)

1. **Preparación ética:** RRHH obtiene autorización de dirección, aplica el consentimiento
   informado de [`docs/CONSENTIMIENTO.md`](CONSENTIMIENTO.md) y lee el
   [protocolo de situaciones detectadas](PROTOCOLO_SITUACIONES_DETECTADAS.md). La encuesta es
   anónima y voluntaria, conforme a la LOPDP.
2. **Recolección:** aplica el Cuestionario de Evaluación de Riesgo Psicosocial del MDT-Ecuador
   (58 ítems, escala 1-4) vía formulario anónimo, con el objetivo de **al menos 100
   respondientes** (meta recomendada 150-300). Duración estimada por persona: 15-20 minutos.
3. **Carga y validación:** exporta a CSV con la plantilla
   `data/encuestas/plantilla_respuestas.csv` y corre
   `python -m src.psicometria data/encuestas/respuestas.csv --pdf`. El CLI valida rangos,
   ítems faltantes y tamaño de muestra antes de reportar.
4. **Lectura del dashboard (vista agregada):**
   - En la pestaña **Riesgo psicosocial**, RRHH revisa la distribución de riesgo
     (Bajo/Medio/Alto) **por dimensión, subescala y global**, con los puntos de corte oficiales,
     y los indicadores de fiabilidad del instrumento. Los grupos con **menos de 5 respondientes
     (n < 5) no se muestran**: si el área "Compras" tiene 4 personas, no aparece.
   - En la pestaña **Simulador (escenario hipotético)**, dimensiona intervenciones candidatas
     usando tamaños de efecto de la literatura (d = 0.526, Richardson & Rothstein, 2008).
   - En el **módulo demostrativo de rotación**, compara métricas agregadas de rotación por
     departamento con el dataset de demo IBM HR (el demo de rotación no usa datos de Textitla).
5. **Discusión:** RRHH lleva al comité solo **promedios y distribuciones por grupo**, nunca
   respuestas ni perfiles de personas.

## Decisiones que podría apoyar RRHH (escenario ilustrativo)

- **Priorizar dimensiones de riesgo** con más casos en nivel Alto a nivel agregado
  (p. ej., si "Exigencias psicológicas del ambiente de trabajo" concentra el mayor porcentaje
  de grupos en Alto — cifra por definir con datos reales).
- **Dimensionar un presupuesto de intervención** comparando escenarios hipotéticos en el
  simulador antes de comprometer recursos.
- **Rediseñar jornadas rotativas** si las dimensiones ligadas a horarios aparecen consistentemente
  elevadas en los reportes grupales.
- **Programar seguimiento** repetiendo la medición tras la intervención, con los mismos resguardos éticos.

## Qué NO se puede concluir (límites explícitos)

- **Nada sobre personas concretas:** la herramienta no evalúa individuos ni sustenta decisiones
  de contratación, despido, ascenso o sanción. Los grupos con n < 5 se ocultan.
- **No es diagnóstico clínico ni certificación:** es una herramienta de apoyo, NO certificada,
  que no sustituye la práctica profesional.
- **No hay causalidad demostrada:** el simulador es un escenario hipotético basado en
  literatura; no garantiza que una intervención reduzca la rotación en Textitla Andina.
- **La validación psicométrica con datos reales está en construcción:** los resultados del
  instrumento con esta empresa serían exploratorios mientras no exista trabajo de campo validado.
- **El módulo de rotación no usa datos propios de la empresa ficticia:** sus métricas provienen
  del dataset público IBM HR Analytics (sintético) y sirven solo de demostración.
- **Sin monitoreo ni generalización:** el comportamiento observado en una organización no es
  trasladable a otra población.

---

*Documento de demostración del proyecto Vigía RH. Ninguna empresa ni persona real está
representada aquí.*
