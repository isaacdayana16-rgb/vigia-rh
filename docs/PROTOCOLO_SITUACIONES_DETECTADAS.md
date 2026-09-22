# Protocolo de Manejo de Situaciones Detectadas (Acoso, Salud, Crisis)

> **Documento operativo y compromiso escrito** — requerido antes de recolectar
> (Fase 10). Aplica aunque el proyecto sea de portafolio. Cumple los principios de la
> **LOPDP (Ecuador, 2021)** y el aviso ético de la guía oficial del MDT.

**Proyecto:** Vigía RH — Analítica Ética de Riesgo Psicosocial
**Instrumento:** Cuestionario oficial MDT (58 ítems), que incluye ítems de acoso laboral
(41, 50), acoso sexual (43, 48) y acoso discriminatorio (35, 38, 53, 56).

---

## 1. Principios no negociables

1. **Anonimato irreversible:** la encuesta es anónima y se mantiene anónima. NUNCA se
   intenta identificar a quien respondió (no se cruza con listas de personal, IPs,
   timestamps de formulario, ni combinaciones de datos generales que permitan
   reidentificación). Si un grupo tiene < 5 respondientes, no se reporta separado.
2. **El cuestionario NO es un canal de denuncia ni una línea de emergencia.** Es una
   herramienta de diagnóstico grupal. Ninguna respuesta genera una acción individual
   automática.
3. **Minimización de datos:** se almacena solo lo necesario (plantilla CSV sin
   identificadores), en `data/encuestas/`, acceso restringido al responsable del
   análisis.

## 2. Escenario A — Una respuesta individual sugiere una situación real

*P. ej., una fila marca "NR" masivo en acoso, o el texto libre de observaciones (ítem 59)
describe una situación de acoso o un problema de salud.*

Acciones (en orden):

1. **No reidentificar.** La respuesta se mantiene anónima; no se busca a la persona.
2. **Documentar el hallazgo de forma agregada** en el reporte (fecha, descripción
   genérica del patrón, sin datos identificables).
3. **Derivar a canales institucionales** (informar al responsable del proyecto, quien
   debe activar los canales previstos por la guía MDT, pág. 14):
   - Dirección de Talento Humano de la empresa/institución.
   - Comité de convivencia laboral / encargado de integridad laboral.
   - Médico ocupacional / psicólogo / trabajadora social del equipo de aplicación.
4. **Canal externo si corresponde:** Dirección de Seguridad, Salud en el Trabajo del
   MDT (seguridadysalud@trabajo.gob.ec). Para acoso laboral/sexual, la vía del
   Acuerdo Ministerial 122 (Reglamento de integridad laboral).
5. **Informar en el consentimiento** (ya incluido, sección 6) que los participantes
   pueden acercarse directamente a esos canales sin esperar al análisis.

## 3. Escenario B — Los datos agregados muestran una señal seria

*P. ej., % relevante de "riesgo alto" en acoso sexual o acoso laboral con los puntos de
corte oficiales, o patrón por área/turno.*

Acciones:

1. Reportar la señal al responsable del proyecto **con el dato agregado** (n y % por
   nivel de riesgo), sin mostrar filas individuales.
2. Recomendar al responsable activar el **plan de acción** previsto por el programa de
   prevención de riesgos psicosociales (formato estandarizado del MDT): medidas de
   prevención e intervención (ver guía oficial, sección 8: programa SOLVE de la OIT,
   medidas de control HSE, intervenciones OMS).
3. Si la señal sugiere riesgo inmediato para personas (p. ej., acoso sexual activo),
   comunicar explícitamente al responsable del proyecto la obligación de **derivar a los
   canales institucionales competentes** de inmediato, en paralelo al plan de acción.
4. Documentar por escrito (log del proyecto, `logs/`) la fecha, la señal agregada y la
   recomendación realizada.

## 4. Escenario C — Malestar evocado en un participante durante la aplicación

1. El facilitador brinda asistencia (previsto en las instrucciones oficiales del
   cuestionario, Anexo 11.1).
2. Informar la opción "NR" (puede dejar ítems sin responder) y la posibilidad de
   retirarse sin consecuencia.
3. Ofrecer el contacto del médico ocupacional/psicólogo del equipo de aplicación.
4. No presionar para completar; la aplicación se detiene si la persona lo solicita.

## 5. Retención y supresión de datos (LOPDP)

- Los datos anonimizados se conservan solo durante el periodo del estudio y su análisis;
  después se archivan o eliminan según la política del portafolio.
- Si un participante solicita supresión: como los datos son anónimos no es posible
  localizar su registro individual; se le comunica la imposibilidad técnica (prueba de
  que no hay trazabilidad) y, si el formulario digital guarda metadatos identificables,
  se eliminan de inmediato.
- Los datos NUNCA se comparten con terceros (incluida la empresa patrocinante) a nivel
  individual.

## 6. Registro de cumplimiento

| Verificación | Estado |
|---|---|
| Consentimiento menciona explícitamente temas de acoso | ✔ (CONSENTIMIENTO.md, sección 2) |
| Anonimato reforzado documentado | ✔ (CONSENTIMIENTO.md, sección 4) |
| Protocolo escrito para respuestas que revelan situaciones reales | ✔ (este documento) |
| Canal de derivación institucional definido | ✔ (secciones 2-3) |
| Principios LOPDP (finalidad, minimización, supresión) | ✔ (sección 5) |
| El cuestionario no es canal de denuncia/urgencia | ✔ (sección 1) |

**Responsable del protocolo:** el/la responsable del proyecto (Vigía RH).
**Fecha de redacción:** 2026-09-22 (antes del trabajo de campo, Fase 10).
