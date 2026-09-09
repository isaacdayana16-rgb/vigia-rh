# 🔎 Vigía RH — Analítica Predictiva de Rotación de Personal

Sistema de People Analytics que combina ciencia de datos con psicología organizacional para predecir, explicar y entender el riesgo de rotación de personal.

**🔗 Demo en vivo:** https://vigia-rh-iomyd5oyurcsmkmfssdkzs.streamlit.app

## El problema
Reemplazar a un empleado le cuesta a una empresa entre 6 y 9 meses de su salario. La mayoría de reportes de RRHH muestran *qué* está pasando, pero no *por qué*.

## La solución
Vigía RH no solo predice quién se va, explica el por qué de cada caso y lo traduce a un marco psicológico real.

## Qué hace
1. **Modelo predictivo** (Random Forest) que calcula riesgo de rotación por empleado
2. **Explicabilidad con SHAP**: qué variables empujan el riesgo de cada persona
3. **Marco JD-R**: traduce variables a un índice de burnout con base teórica
4. **Análisis de sentimiento en español** (pysentimiento)
5. **Dashboard interactivo** en Streamlit
6. **Reporte PDF automático** con resumen ejecutivo

## Hallazgo clave
El índice de burnout JD-R fue 8.35 en los que renunciaron vs 7.18 en los que se quedaron, validando la teoría con datos reales.

## Stack
Python · pandas · scikit-learn · SHAP · pysentimiento · Plotly · Streamlit · fpdf2

## Cómo adaptarlo a una empresa real
1. Reemplazar CSV en `data/` por datos de la empresa
2. Ajustar nombres de columnas
3. Correr `modelo.py` → `explicabilidad.py` → `marco_psicologico.py`

## Limitaciones
Usa dataset público IBM HR Analytics como demo. Arquitectura lista para datos reales.

## Autor
Isaac Reyes — Psicología Organizacional | People Analytics