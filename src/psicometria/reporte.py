"""Generación de reportes de validación psicométrica (consola y PDF).

El reporte documenta: tamaño de muestra, cobertura de ítems, clasificación de
riesgo con los puntos de corte OFICIALES (Tablas 3-4 del PDF del MDT),
fiabilidad (α/ω para subescalas de 3+ ítems; Spearman-Brown y marca
"descriptiva, no psicométrica" para subescalas de 2 ítems), validez de
constructo (AFE exploratorio), validez de criterio (regresión logística) y el
aviso ético obligatorio.

PDF generado con fpdf2 (fuentes core + latin-1, portable sin binarios).
"""
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np

from .instrumento import (
    ITEMS,
    DIMENSIONES,
    SUBESCALAS_OTROS,
    items_de_dimension,
    items_de_subescala,
    clasificar_riesgo_dimension,
    clasificar_riesgo_global,
)
from .puntuaciones import (
    calcular_puntuaciones,
    calcular_puntuaciones_subescala,
    calcular_suma_global,
    validar_datos_respuestas,
)
from .fiabilidad import cronbach_alpha, mcdonald_omega, spearman_brown, clasificar_subescala
from .validacion import analisis_factorial, regresion_logistica, validacion_cruzada_estratificada

# N objetivo fijado por simulación (simulador_muestra.py): la fiabilidad α/ω de
# las dimensiones principales es estable a cualquier N simulado (30-400); el N
# objetivo alinea el umbral de la validación cruzada (n < 100 -> exploratorio).
N_OBJETIVO_SIMULACION = 100

# Dimensiones heterogéneas: la simulación muestra que su α no alcanza 0.70 a
# ningún N (24 ítems de 8 subconstructos); la guía oficial (pág. 17) las define
# como "punto de partida para evaluaciones más específicas".
DIMENSIONES_HETEROGENEAS = ("otros_puntos_importantes",)


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


def _distribucion_riesgo(serie_niveles: pd.Series) -> dict:
    """Cuenta respondientes por nivel de riesgo ('Bajo'/'Medio'/'Alto')."""
    clasificados = serie_niveles.dropna()
    total = len(clasificados)
    return {
        nivel: {
            "n": int((clasificados == nivel).sum()),
            "pct": float((clasificados == nivel).mean()) if total else None,
        }
        for nivel in ("Bajo", "Medio", "Alto")
    }


def _linea_distribucion(nombre: str, dist: dict) -> str:
    """Formatea una línea de distribución de riesgo."""
    partes = []
    for nivel in ("Bajo", "Medio", "Alto"):
        d = dist[nivel]
        pct = f"{d['pct']:.0%}" if d["pct"] is not None else "N/D"
        partes.append(f"{nivel}={d['n']} ({pct})")
    return f"  {nombre:26s}: " + "  ".join(partes)


def _interpretacion_general(r: dict) -> list:
    """Genera una interpretación cualitativa (resumen ejecutivo) de los resultados.

    Usa únicamente caracteres ASCII para máxima compatibilidad (consola y PDF).
    """
    puntos = []

    # Fiabilidad (solo subescalas psicometricas; las de 2 items son descriptivas)
    fiab = r["fiabilidad"]
    descriptivas = [n for n, d in fiab.items() if d.get("tipo") == "descriptiva_no_psicometrica"]
    psicometricas = {
        n: d for n, d in fiab.items()
        if d.get("tipo") == "psicometrica" and np.isfinite(d["alpha"]) and np.isfinite(d["omega"])
    }
    if descriptivas:
        puntos.append(
            "- Subescalas de 2 items reportadas como descriptivas (no psicometricas): "
            f"{', '.join(descriptivas)}. Se reporta Spearman-Brown, no alpha "
            "(el alpha es inestable en escalas de 2 items)."
        )
    heterogeneas = [
        n for n in psicometricas
        if n in DIMENSIONES_HETEROGENEAS and (psicometricas[n]["alpha"] < 0.70 or psicometricas[n]["omega"] < 0.70)
    ]
    for n in heterogeneas:
        d = psicometricas[n]
        puntos.append(
            f"- {n} es heterogenea por diseno (24 items de 8 subconstructos debilmente "
            f"correlacionados): alpha={_fmt_fiabilidad(d['alpha'])}, omega={_fmt_fiabilidad(d['omega'])}. "
            "La simulacion muestra que su fiabilidad no alcanza 0.70 a cualquier N: "
            "es un limite estructural, no de muestra. Analiza sus subescalas por "
            "separado (la guia oficial la define como punto de partida para "
            "evaluaciones mas especificas)."
        )
    sustantivas = {
        n: d for n, d in psicometricas.items()
        if n not in DIMENSIONES_HETEROGENEAS
    }
    if sustantivas:
        # Subescalas del bloque heterogéneo: fiabilidad baja anticipada por diseño
        debajo_subescalas = [
            n for n, d in sustantivas.items()
            if n in SUBESCALAS_OTROS and (d["alpha"] < 0.70 or d["omega"] < 0.70)
        ]
        for n in debajo_subescalas:
            d = sustantivas[n]
            puntos.append(
                f"- La subescala {n} tiene fiabilidad baja "
                f"(alpha={_fmt_fiabilidad(d['alpha'])}, omega={_fmt_fiabilidad(d['omega'])}): "
                "el bloque 'Otros puntos importantes' es heterogeneo por diseno y sus "
                "subescalas se interpretan como descriptivas/especificas (guia oficial, "
                "pag. 17), no como escalas psicometricas de uso inferencial."
            )
        # Dimensiones principales: la alarma genérica aplica solo a estas
        debajo_dimensiones = [
            n for n, d in sustantivas.items()
            if n in DIMENSIONES and (d["alpha"] < 0.70 or d["omega"] < 0.70)
        ]
        if debajo_dimensiones:
            for n in debajo_dimensiones:
                d = sustantivas[n]
                puntos.append(
                    f"- Fiabilidad de {n} no alcanza el umbral de 0.70 "
                    f"(alpha={_fmt_fiabilidad(d['alpha'])}, omega={_fmt_fiabilidad(d['omega'])}). "
                    "Revisa la redaccion de items o la calidad de datos."
                )
        else:
            puntos.append(
                "- Fiabilidad aceptable en las dimensiones principales "
                "(alpha y omega >= 0.70): la consistencia interna es suficiente "
                "para analisis grupales."
            )

    # Estructura factorial (exploratoria)
    afc = r["afc"]
    if afc:
        varianza = afc["varianza"]
        puntos.append(
            "- Analisis factorial exploratorio: los primeros 2 factores explican "
            + ", ".join(f"F{i+1}={v:.2%}" for i, v in enumerate(varianza))
            + ". El instrumento oficial MDT no postula una estructura "
            "bidimensional; este resultado es exploratorio."
        )

    # Criterio (correlaciones univariadas: estables frente a multicolinealidad)
    if r["correlaciones"]:
        correlaciones = r["correlaciones"]
        direccion_ok = all(v < 0 for v in correlaciones.values())
        if direccion_ok:
            puntos.append(
                "- La direccion de la asociacion (correlaciones univariadas) es "
                "consistente con la direccion del puntaje oficial (menor puntaje = "
                "mayor riesgo): a mayor puntaje por dimension, menor intencion de rotacion."
            )
        else:
            inconsistentes = [c for c, v in correlaciones.items() if v >= 0]
            puntos.append(
                f"- Correlaciones con direccion inesperada: {', '.join(inconsistentes)}. "
                "Sospecha de datos ruidosos o muestra no representativa."
            )

    # Validación cruzada estratificada
    vc = r["validacion_cruzada"]
    if vc:
        if vc["viable"]:
            etiqueta = (
                "EXPLORATORIO, NO GENERALIZABLE" if vc["etiqueta"] == "exploratorio_no_generalizable"
                else "indicativo"
            )
            puntos.append(
                f"- Validacion cruzada estratificada (k={vc['k']}): F1 macro="
                f"{vc['f1_macro']:.3f}, accuracy balanceada={vc['balanced_accuracy']:.3f} "
                f"({etiqueta}). No se usa accuracy simple: el instrumento suele "
                "concentrar respuestas en riesgo bajo."
            )
        else:
            puntos.append(
                "- Validacion cruzada estratificada no viable: alguna clase tiene "
                "menos miembros que k."
            )

    if not puntos:
        puntos.append("- No hay suficientes datos para una interpretacion completa.")

    return puntos


# --- Cálculo de todos los indicadores ---------------------------------------

def _calcular_indicadores(df: pd.DataFrame) -> dict:
    """Calcula todos los indicadores psicométricos a partir de las respuestas."""
    estructura = validar_datos_respuestas(df)
    punt = calcular_puntuaciones(df)
    punt_sub = calcular_puntuaciones_subescala(df)
    punt_norm = calcular_puntuaciones(df, normalizar=True)

    # Fiabilidad por dimensión principal y por subescala
    fiabilidad = {}
    for dimension in DIMENSIONES:
        items = [i for i in items_de_dimension(dimension) if i in df.columns]
        if len(items) >= 2:
            fiabilidad[dimension] = {
                "alpha": cronbach_alpha(df[items]),
                "omega": mcdonald_omega(df[items]),
                "sb": float("nan"),
                "n_items": len(items),
                "tipo": clasificar_subescala(len(items)),
            }
    for subescala in SUBESCALAS_OTROS:
        items = [i for i in items_de_subescala(subescala) if i in df.columns]
        if len(items) >= 2:
            tipo = clasificar_subescala(len(items))
            # Subescalas de 2 items: reportar Spearman-Brown, NO alpha
            # (el alfa es inestable por construccion en escalas de 2 items).
            fiabilidad[subescala] = {
                "alpha": cronbach_alpha(df[items]) if tipo == "psicometrica" else float("nan"),
                "omega": mcdonald_omega(df[items]) if tipo == "psicometrica" else float("nan"),
                "sb": spearman_brown(df[items]) if tipo == "descriptiva_no_psicometrica" else float("nan"),
                "n_items": len(items),
                "tipo": tipo,
            }

    # Clasificación oficial de riesgo (Tablas 3-4)
    riesgo_dim = {
        dimension: _distribucion_riesgo(
            punt[dimension].apply(lambda s: clasificar_riesgo_dimension(dimension, s))
        )
        for dimension in DIMENSIONES
        if dimension in punt.columns
    }
    riesgo_sub = {
        subescala: _distribucion_riesgo(
            punt_sub[subescala].apply(lambda s: clasificar_riesgo_dimension(subescala, s))
        )
        for subescala in SUBESCALAS_OTROS
        if subescala in punt_sub.columns
    }
    suma_global = calcular_suma_global(df)
    riesgo_global = _distribucion_riesgo(suma_global.apply(clasificar_riesgo_global))

    afc = None
    presentes = estructura["presentes"]
    if len(presentes) >= 2:
        cargas, varianza = analisis_factorial(df[presentes], n_factores=2)
        afc = {"cargas": cargas, "varianza": varianza}

    correlaciones = None
    regresion = None
    validacion_cruzada = None
    if estructura["tiene_outcome"] and not estructura["faltantes"]:
        X = punt_norm[list(DIMENSIONES)]
        y = df["intencion_rotacion"].to_numpy()
        # Correlaciones univariadas dimensión-rotación (estables frente a la
        # multicolinealidad entre dimensiones; la dirección individual de una
        # regresión multivariada NO lo es).
        correlaciones = {
            dim: float(np.corrcoef(X[dim], y)[0, 1])
            for dim in DIMENSIONES
            if np.isfinite(np.corrcoef(X[dim], y)[0, 1])
        }
        regresion = regresion_logistica(X, y)
        validacion_cruzada = validacion_cruzada_estratificada(X, y, k=5)

    return {
        "estructura": estructura,
        "puntuaciones": punt,
        "puntuaciones_norm": punt_norm,
        "fiabilidad": fiabilidad,
        "riesgo_dim": riesgo_dim,
        "riesgo_sub": riesgo_sub,
        "riesgo_global": riesgo_global,
        "afc": afc,
        "correlaciones": correlaciones,
        "regresion": regresion,
        "validacion_cruzada": validacion_cruzada,
        "n": len(df),
    }


def _seccion_riesgo(r: dict) -> list:
    """Sección de clasificación oficial de riesgo (Tablas 3-4)."""
    lineas = []
    lineas.append("Clasificacion con puntos de corte oficiales (menor puntaje = mayor riesgo):")
    for dimension in DIMENSIONES:
        if dimension in r["riesgo_dim"]:
            lineas.append(_linea_distribucion(dimension, r["riesgo_dim"][dimension]))
    for subescala, dist in r["riesgo_sub"].items():
        lineas.append(_linea_distribucion(subescala, dist))
    lineas.append(_linea_distribucion("RIESGO GLOBAL (58 items)", r["riesgo_global"]))
    return lineas


def _seccion_fiabilidad(r: dict) -> list:
    """Sección de fiabilidad con la distinción psicométrica/descriptiva."""
    lineas = []
    for nombre, datos in r["fiabilidad"].items():
        base = f"  {nombre:26s} (n={datos['n_items']}, {datos['tipo']})"
        if datos["tipo"] == "descriptiva_no_psicometrica":
            lineas.append(
                base + f": SB={_fmt_fiabilidad(datos['sb'])} "
                "[descriptiva, no psicometrica: alpha no reportable]"
            )
        else:
            lineas.append(
                base + f": alpha={_fmt_fiabilidad(datos['alpha'])} "
                f"[{_clasificar_fiabilidad(datos['alpha'])}]  "
                f"omega={_fmt_fiabilidad(datos['omega'])} "
                f"[{_clasificar_fiabilidad(datos['omega'])}]"
            )
    return lineas


# --- Reporte en consola ------------------------------------------------------

def generar_reporte_texto(df: pd.DataFrame, ruta_origen: str = "") -> str:
    """Genera el texto del reporte de validación (para imprimir en consola)."""
    r = _calcular_indicadores(df)
    est = r["estructura"]

    lineas = []
    lineas.append("=" * 64)
    lineas.append("REPORTE DE VALIDACIÓN PSICOMÉTRICA — Vigía RH")
    lineas.append("=" * 64)
    lineas.append("Instrumento oficial MDT-Ecuador (58 items, escala Likert 1-4)")
    lineas.append(f"Archivo analizado : {ruta_origen or '(datos en memoria)'}")
    lineas.append(f"Fecha             : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lineas.append(f"Tamaño de muestra : {r['n']} respondientes")
    lineas.append(f"Ítems del inst.   : {est['total_items_instrumento']}")
    lineas.append(f"Ítems presentes   : {len(est['presentes'])}")
    lineas.append(f"Outcome presente  : {est['tiene_outcome']}")
    if est["faltantes"]:
        lineas.append(f"[!] Ítems ausentes   : {', '.join(est['faltantes'])}")

    lineas.append("\n[1] RIESGO POR DIMENSIÓN (puntos de corte oficiales)")
    lineas.append("-" * 64)
    lineas.extend(_seccion_riesgo(r))

    lineas.append("\n[2] FIABILIDAD (consistencia interna)")
    lineas.append("-" * 64)
    lineas.extend(_seccion_fiabilidad(r))

    lineas.append("\n[3] VALIDEZ DE CONSTRUCTO (análisis factorial exploratorio)")
    lineas.append("-" * 64)
    if r["afc"]:
        varianza = r["afc"]["varianza"]
        lineas.append("  Varianza explicada: " + ", ".join(
            f"F{i+1}={v:.2%}" for i, v in enumerate(varianza)
        ))
        lineas.append(
            "  [i] El instrumento oficial MDT no postula una estructura"
        )
        lineas.append("  bidimensional; este análisis es exploratorio.")
    else:
        lineas.append("  No hay suficientes ítems para análisis factorial.")

    lineas.append("\n[4] VALIDEZ DE CRITERIO (relación con rotación)")
    lineas.append("-" * 64)
    if r["correlaciones"]:
        lineas.append("  Dirección univariada (estable frente a multicolinealidad):")
        for dimension, valor in r["correlaciones"].items():
            lineas.append(
                f"  {dimension:26s}: r={valor:+.3f}  (signo esperado: -)"
            )
        direccion_ok = all(v < 0 for v in r["correlaciones"].values())
        lineas.append(
            "  Dirección consistente con puntaje oficial (menor puntaje = mayor riesgo): "
            f"{'SÍ' if direccion_ok else 'NO'}"
        )
        if not direccion_ok:
            lineas.append(
                "  [!] La dirección de los coeficientes no coincide con la esperada."
            )
    elif not r["regresion"]:
        lineas.append(
            "  No se encontró la columna 'intencion_rotacion'; se omite este análisis."
        )
    if r["regresion"]:
        coef = r["regresion"]["coeficientes"]
        lineas.append("  Modelo multivariado (regresión logística):")
        lineas.append(f"    Intercepto: {coef['intercepto']:.3f}")
        for dimension in DIMENSIONES:
            lineas.append(
                f"    {dimension:24s}: {coef[dimension]:+.3f}"
            )
        lineas.append(
            "    [i] Con dimensiones colineales, los coeficientes individuales son"
        )
        lineas.append(
            "    inestables; interpretar con cautela y priorizar por la dirección"
        )
        lineas.append("    univariada y la validación cruzada.")
    if r["validacion_cruzada"]:
        vc = r["validacion_cruzada"]
        if vc["viable"]:
            etiqueta = (
                "EXPLORATORIO, NO GENERALIZABLE"
                if vc["etiqueta"] == "exploratorio_no_generalizable"
                else "indicativo"
            )
            lineas.append(
                f"  Validación cruzada estratificada (k={vc['k']}): "
                f"F1 macro={vc['f1_macro']:.3f}, "
                f"accuracy balanceada={vc['balanced_accuracy']:.3f} [{etiqueta}]"
            )
            lineas.append(
                "  [i] No se reporta accuracy simple: el instrumento suele"
            )
            lineas.append("  concentrar respuestas en 'riesgo bajo' (clases desbalanceadas).")
        else:
            lineas.append(
                "  Validación cruzada estratificada no viable: alguna clase tiene "
                "menos miembros que k."
            )

    lineas.append("\n[5] INTERPRETACIÓN (resumen ejecutivo)")
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
    pdf.cell(0, 6, _texto_latin1("Instrumento oficial MDT-Ecuador (58 items, escala Likert 1-4)"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, _texto_latin1(f"Archivo: {ruta_origen or '(datos en memoria)'}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, _texto_latin1(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, _texto_latin1(f"Tamaño de muestra: {r['n']} respondientes"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Riesgo por dimensión (puntos de corte oficiales)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, _texto_latin1("1. Riesgo por dimensión (puntos de corte oficiales)"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    for linea in _seccion_riesgo(r):
        pdf.multi_cell(pdf.epw, 5, _texto_latin1(linea))

    pdf.ln(3)

    # Fiabilidad
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, _texto_latin1("2. Fiabilidad (consistencia interna)"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    for linea in _seccion_fiabilidad(r):
        pdf.multi_cell(pdf.epw, 5, _texto_latin1(linea))

    pdf.ln(3)

    # Validez de constructo
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, _texto_latin1("3. Validez de constructo (análisis factorial exploratorio)"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    if r["afc"]:
        varianza = r["afc"]["varianza"]
        pdf.cell(0, 6, _texto_latin1("  Varianza explicada: " + ", ".join(
            f"F{i+1}={v:.2%}" for i, v in enumerate(varianza)
        )), new_x="LMARGIN", new_y="NEXT")
        pdf.multi_cell(
            pdf.epw, 5,
            _texto_latin1(
                "  Nota: el instrumento oficial MDT no postula una estructura "
                "bidimensional; este análisis es exploratorio."
            ),
        )
    else:
        pdf.cell(0, 6, _texto_latin1("  Sin datos suficientes."), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)

    # Validez de criterio
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, _texto_latin1("4. Validez de criterio (relación con rotación)"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    if r["correlaciones"]:
        for dimension, valor in r["correlaciones"].items():
            pdf.cell(
                0, 6,
                _texto_latin1(f"  {dimension}: r={valor:+.3f} (esperado -)"),
                new_x="LMARGIN", new_y="NEXT",
            )
        direccion_ok = all(v < 0 for v in r["correlaciones"].values())
        pdf.cell(0, 6, _texto_latin1(
            f"  Dirección consistente (menor puntaje = mayor riesgo): {'SÍ' if direccion_ok else 'NO'}"
        ), new_x="LMARGIN", new_y="NEXT")
    elif not r["regresion"]:
        pdf.cell(0, 6, _texto_latin1("  Sin columna 'intencion_rotacion'; se omite."), new_x="LMARGIN", new_y="NEXT")
    if r["regresion"]:
        coef = r["regresion"]["coeficientes"]
        pdf.multi_cell(
            pdf.epw, 5,
            _texto_latin1(
                "  Modelo multivariado: los coeficientes individuales son inestables "
                "con dimensiones colineales; interpretar con cautela y priorizar por "
                "la dirección univariada y la validación cruzada."
            ),
        )
    if r["validacion_cruzada"]:
        vc = r["validacion_cruzada"]
        if vc["viable"]:
            etiqueta = (
                "EXPLORATORIO, NO GENERALIZABLE"
                if vc["etiqueta"] == "exploratorio_no_generalizable"
                else "indicativo"
            )
            pdf.multi_cell(
                pdf.epw, 5,
                _texto_latin1(
                    f"  Validación cruzada estratificada (k={vc['k']}): "
                    f"F1 macro={vc['f1_macro']:.3f}, accuracy balanceada="
                    f"{vc['balanced_accuracy']:.3f} [{etiqueta}]. No se reporta "
                    "accuracy simple (clases desbalanceadas)."
                ),
            )
        else:
            pdf.multi_cell(
                pdf.epw, 5,
                _texto_latin1(
                    "  Validación cruzada estratificada no viable: alguna clase "
                    "tiene menos miembros que k."
                ),
            )

    # Interpretación (resumen ejecutivo)
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, _texto_latin1("5. Interpretación (resumen ejecutivo)"), new_x="LMARGIN", new_y="NEXT")
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
