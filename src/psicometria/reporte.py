"""Generación de reportes de validación psicométrica (consola y PDF).

El reporte documenta: tamaño de muestra, cobertura de ítems, fiabilidad
(alpha/omega), validez de constructo (análisis factorial) y validez de
criterio (regresión logística), además del aviso ético obligatorio.

PDF generado con fpdf2 (fuentes core + latin-1, portable sin binarios).
"""
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np

from .instrumento import ITEMS, items_de_dimension
from .puntuaciones import calcular_puntuaciones, validar_datos_respuestas
from .fiabilidad import cronbach_alpha, mcdonald_omega
from .validacion import analisis_factorial, regresion_logistica


def _fmt_fiabilidad(valor) -> str:
    """Formatea un valor de fiabilidad, mostrando 'N/D' si no es finito."""
    if valor is None or not np.isfinite(valor):
        return "N/D"
    return f"{valor:.3f}"


def _clasificar_fiabilidad(valor) -> str:
    """Clasifica el valor de fiabilidad según umbrales convencionales."""
    if valor is None or not np.isfinite(valor):
        return "N/D"
    if valor >= 0.80:
        return "Buena"
    if valor >= 0.70:
        return "Aceptable"
    if valor >= 0.60:
        return "Cuestionable"
    return "Insuficiente"


def _interpretacion_general(r: dict) -> list:
    """Genera una interpretación cualitativa (resumen ejecutivo) de los resultados.

    Usa únicamente caracteres ASCII para máxima compatibilidad (consola y PDF).
    """
    puntos = []

    # Fiabilidad
    fiab = r["fiabilidad"]
    if fiab:
        aceptable = True
        for dimension, datos in fiab.items():
            a = datos["alpha"]
            o = datos["omega"]
            umbrales_ok = (
                (a is not None and a >= 0.70) and (o is not None and o >= 0.70)
            )
            if not umbrales_ok:
                aceptable = False
                puntos.append(
                    f"- Fiabilidad de {dimension} no alcanza el umbral de 0.70 "
                    f"(alpha={_fmt_fiabilidad(a)}, omega={_fmt_fiabilidad(o)}). "
                    "Revisa la redacción de ítems o la calidad de datos."
                )
        if aceptable:
            puntos.append(
                "- Fiabilidad aceptable en ambas dimensiones (alpha y omega >= 0.70): "
                "la consistencia interna es suficiente para análisis grupales."
            )
    else:
        puntos.append("- Fiabilidad no calculable por falta de ítems por dimensión.")

    # Estructura factorial
    afc = r["afc"]
    if afc:
        cargas = afc["cargas"]
        dem_f1 = cargas.loc[items_de_dimension("demandas"), "F1"].abs().mean()
        dem_f2 = cargas.loc[items_de_dimension("demandas"), "F2"].abs().mean()
        rec_f1 = cargas.loc[items_de_dimension("recursos"), "F1"].abs().mean()
        rec_f2 = cargas.loc[items_de_dimension("recursos"), "F2"].abs().mean()
        separado = (dem_f1 > rec_f1) != (dem_f2 > rec_f2)
        if separado:
            puntos.append(
                "- El análisis factorial separa demandas y recursos en 2 factores: "
                "evidencia de validez de constructo."
            )
        else:
            puntos.append(
                "- Los ítems NO se separan en 2 factores. Esto cuestiona la validez de "
                "constructo; revisa el instrumento o los datos."
            )

    # Criterio
    reg = r["regresion"]
    if reg:
        coef = reg["coeficientes"]
        direccion_ok = coef["demandas"] > 0 and coef["recursos"] < 0
        if direccion_ok:
            puntos.append(
                "- La dirección de la regresión es consistente con el modelo JD-R: "
                "más demandas se asocian a mayor rotación, más recursos a menor."
            )
        else:
            puntos.append(
                "- La dirección de la regresión NO es consistente con el modelo JD-R. "
                "Sospecha de datos ruidosos o muestra no representativa."
            )

    if not puntos:
        puntos.append("- No hay suficientes datos para una interpretación completa.")

    return puntos


# --- Cálculo de todos los indicadores ---------------------------------------

def _calcular_indicadores(df: pd.DataFrame) -> dict:
    """Calcula todos los indicadores psicométricos a partir de las respuestas."""
    estructura = validar_datos_respuestas(df)
    punt = calcular_puntuaciones(df)

    fiabilidad = {}
    for dimension in ["demandas", "recursos"]:
        items = [i for i in items_de_dimension(dimension) if i in df.columns]
        if len(items) >= 2:
            fiabilidad[dimension] = {
                "alpha": cronbach_alpha(df[items]),
                "omega": mcdonald_omega(df[items]),
                "n_items": len(items),
            }

    afc = None
    presentes = estructura["presentes"]
    if len(presentes) >= 2:
        cargas, varianza = analisis_factorial(df[presentes], n_factores=2)
        afc = {"cargas": cargas, "varianza": varianza}

    regresion = None
    if estructura["tiene_outcome"]:
        X = punt[["demandas", "recursos"]]
        y = df["intencion_rotacion"].to_numpy()
        regresion = regresion_logistica(X, y)

    return {
        "estructura": estructura,
        "puntuaciones": punt,
        "fiabilidad": fiabilidad,
        "afc": afc,
        "regresion": regresion,
        "n": len(df),
    }


# --- Reporte en consola ------------------------------------------------------

def generar_reporte_texto(df: pd.DataFrame, ruta_origen: str = "") -> str:
    """Genera el texto del reporte de validación (para imprimir en consola)."""
    r = _calcular_indicadores(df)
    est = r["estructura"]

    lineas = []
    lineas.append("=" * 64)
    lineas.append("REPORTE DE VALIDACIÓN PSICOMÉTRICA — Vigía RH")
    lineas.append("=" * 64)
    lineas.append(f"Archivo analizado : {ruta_origen or '(datos en memoria)'}")
    lineas.append(f"Fecha             : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lineas.append(f"Tamaño de muestra : {r['n']} respondientes")
    lineas.append(f"Ítems del inst.   : {est['total_items_instrumento']}")
    lineas.append(f"Ítems presentes   : {len(est['presentes'])}")
    lineas.append(f"Outcome presente  : {est['tiene_outcome']}")
    if est["faltantes"]:
        lineas.append(f"[!] Ítems ausentes   : {', '.join(est['faltantes'])}")

    lineas.append("\n[1] FIABILIDAD (consistencia interna)")
    lineas.append("-" * 64)
    for dimension, datos in r["fiabilidad"].items():
        lineas.append(
            f"  {dimension.capitalize():9s} (n={datos['n_items']}): "
            f"alpha={_fmt_fiabilidad(datos['alpha'])} [{_clasificar_fiabilidad(datos['alpha'])}]  "
            f"omega={_fmt_fiabilidad(datos['omega'])} [{_clasificar_fiabilidad(datos['omega'])}]"
        )
    if not r["fiabilidad"]:
        lineas.append("  No hay suficientes ítems por dimensión para calcular fiabilidad.")

    lineas.append("\n[2] VALIDEZ DE CONSTRUCTO (análisis factorial)")
    lineas.append("-" * 64)
    if r["afc"]:
        cargas = r["afc"]["cargas"]
        varianza = r["afc"]["varianza"]
        dem_items = items_de_dimension("demandas")
        rec_items = items_de_dimension("recursos")
        dem_f1 = cargas.loc[dem_items, "F1"].abs().mean()
        dem_f2 = cargas.loc[dem_items, "F2"].abs().mean()
        rec_f1 = cargas.loc[rec_items, "F1"].abs().mean()
        rec_f2 = cargas.loc[rec_items, "F2"].abs().mean()
        f1_dom = "demandas" if dem_f1 > rec_f1 else "recursos"
        f2_dom = "demandas" if dem_f2 > rec_f2 else "recursos"
        lineas.append(f"  Cargas medias — Demandas: F1={dem_f1:.3f}, F2={dem_f2:.3f}")
        lineas.append(f"  Cargas medias — Recursos: F1={rec_f1:.3f}, F2={rec_f2:.3f}")
        lineas.append(f"  Factor F1 dominado por: {f1_dom}")
        lineas.append(f"  Factor F2 dominado por: {f2_dom}")
        separado = f1_dom != f2_dom
        lineas.append(f"  Estructura de 2 factores separada: {'SÍ' if separado else 'NO'}")
        lineas.append(f"  Varianza explicada: " + ", ".join(
            f"F{i+1}={v:.2%}" for i, v in enumerate(varianza)
        ))
        if not separado:
            lineas.append("  [!] Los ítems no se separan en 2 factores: revisa el instrumento.")
    else:
        lineas.append("  No hay suficientes ítems para análisis factorial.")

    lineas.append("\n[3] VALIDEZ DE CRITERIO (regresión logística sobre rotación)")
    lineas.append("-" * 64)
    if r["regresion"]:
        coef = r["regresion"]["coeficientes"]
        lineas.append(f"  Intercepto: {coef['intercepto']:.3f}")
        lineas.append(f"  Demandas  : {coef['demandas']:+.3f}  (signo esperado: +)")
        lineas.append(f"  Recursos  : {coef['recursos']:+.3f}  (signo esperado: -)")
        direccion_ok = coef["demandas"] > 0 and coef["recursos"] < 0
        lineas.append(f"  Dirección consistente con modelo JD-R: {'SÍ' if direccion_ok else 'NO'}")
        if not direccion_ok:
            lineas.append("  [!] La dirección de los coeficientes no coincide con el modelo JD-R.")
    else:
        lineas.append("  No se encontró la columna 'intencion_rotacion'; se omite este análisis.")

    lineas.append("\n[4] INTERPRETACIÓN (resumen ejecutivo)")
    lineas.append("-" * 64)
    for punto in _interpretacion_general(r):
        lineas.append(f"  {punto}")

    lineas.append("\n" + "=" * 64)
    lineas.append("[!] AVISO ÉTICO: Este análisis mide constructos psicosociales a nivel")
    lineas.append("grupal. NO es diagnóstico clínico y NO debe usarse para decisiones")
    lineas.append("individuales de contratación, despido, ascenso o sanción.")
    lineas.append("=" * 64)

    return "\n".join(lineas)


# --- Reporte PDF -------------------------------------------------------------

def _texto_latin1(texto: str) -> str:
    """Codifica texto a latin-1 (replace) para compatibilidad con fuentes core."""
    return texto.encode("latin-1", errors="replace").decode("latin-1")


def generar_reporte_pdf(df: pd.DataFrame, ruta_destino, ruta_origen: str = "") -> str:
    """Genera un reporte PDF de validación psicométrica.

    Args:
        df: DataFrame de respuestas.
        ruta_destino: Ruta donde guardar el PDF.
        ruta_origen: Ruta del archivo de origen (para el encabezado).

    Returns:
        str: Ruta del PDF generado.
    """
    from fpdf import FPDF

    r = _calcular_indicadores(df)
    est = r["estructura"]

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, _texto_latin1("Vigía RH — Reporte de Validación Psicométrica"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, _texto_latin1(f"Archivo: {ruta_origen or '(datos en memoria)'}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, _texto_latin1(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, _texto_latin1(f"Tamaño de muestra: {r['n']} respondientes"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Fiabilidad
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, _texto_latin1("1. Fiabilidad (consistencia interna)"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for dimension, datos in r["fiabilidad"].items():
        pdf.cell(
            0, 6,
            _texto_latin1(
                f"  {dimension.capitalize()} (n={datos['n_items']}): "
                f"alpha={_fmt_fiabilidad(datos['alpha'])} [{_clasificar_fiabilidad(datos['alpha'])}], "
                f"omega={_fmt_fiabilidad(datos['omega'])} [{_clasificar_fiabilidad(datos['omega'])}]"
            ),
            new_x="LMARGIN", new_y="NEXT",
        )
    if not r["fiabilidad"]:
        pdf.cell(0, 6, _texto_latin1("  Sin datos suficientes por dimensión."), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)

    # Validez de constructo
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, _texto_latin1("2. Validez de constructo (análisis factorial)"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    if r["afc"]:
        cargas = r["afc"]["cargas"]
        varianza = r["afc"]["varianza"]
        dem_items = items_de_dimension("demandas")
        rec_items = items_de_dimension("recursos")
        dem_f1 = cargas.loc[dem_items, "F1"].abs().mean()
        dem_f2 = cargas.loc[dem_items, "F2"].abs().mean()
        rec_f1 = cargas.loc[rec_items, "F1"].abs().mean()
        rec_f2 = cargas.loc[rec_items, "F2"].abs().mean()
        f1_dom = "demandas" if dem_f1 > rec_f1 else "recursos"
        f2_dom = "demandas" if dem_f2 > rec_f2 else "recursos"
        separado = f1_dom != f2_dom
        pdf.cell(0, 6, _texto_latin1(f"  Cargas Demandas: F1={dem_f1:.3f}, F2={dem_f2:.3f}"), new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, _texto_latin1(f"  Cargas Recursos: F1={rec_f1:.3f}, F2={rec_f2:.3f}"), new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, _texto_latin1(f"  F1 dominado por: {f1_dom}; F2 dominado por: {f2_dom}"), new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, _texto_latin1(f"  Estructura 2 factores separada: {'SÍ' if separado else 'NO'}"), new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, _texto_latin1("  Varianza explicada: " + ", ".join(
            f"F{i+1}={v:.2%}" for i, v in enumerate(varianza)
        )), new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 6, _texto_latin1("  Sin datos suficientes."), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)

    # Validez de criterio
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, _texto_latin1("3. Validez de criterio (regresión logística)"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    if r["regresion"]:
        coef = r["regresion"]["coeficientes"]
        direccion_ok = coef["demandas"] > 0 and coef["recursos"] < 0
        pdf.cell(0, 6, _texto_latin1(f"  Intercepto: {coef['intercepto']:.3f}"), new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, _texto_latin1(f"  Demandas: {coef['demandas']:+.3f} (esperado +)"), new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, _texto_latin1(f"  Recursos: {coef['recursos']:+.3f} (esperado -)"), new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, _texto_latin1(f"  Dirección JD-R consistente: {'SÍ' if direccion_ok else 'NO'}"), new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 6, _texto_latin1("  Sin columna 'intencion_rotacion'; se omite."), new_x="LMARGIN", new_y="NEXT")

    # Interpretación (resumen ejecutivo)
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, _texto_latin1("4. Interpretación (resumen ejecutivo)"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for punto in _interpretacion_general(r):
        pdf.multi_cell(pdf.epw, 6, _texto_latin1(f"  - {punto}"))

    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(
        pdf.epw, 5,
        _texto_latin1(
            "AVISO ÉTICO: Este análisis mide constructos psicosociales a nivel grupal. "
            "NO es diagnóstico clínico y NO debe usarse para decisiones individuales de "
            "contratación, despido, ascenso o sanción."
        ),
    )

    ruta_destino = str(Path(ruta_destino))
    Path(ruta_destino).parent.mkdir(parents=True, exist_ok=True)
    pdf.output(ruta_destino)
    return ruta_destino