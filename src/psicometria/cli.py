"""CLI de validación psicométrica.

Uso:
    python -m src.psicometria <archivo.csv> [--pdf RUTA]
    python -m src.psicometria          # genera datos de demostración

Valida la estructura, calcula fiabilidad (alpha/omega), validez de constructo
(análisis factorial) y validez de criterio (regresión logística), y produce un
reporte en consola y (opcionalmente) un PDF.
"""


def main(argv=None) -> int:
    """Punto de entrada del CLI. Ejecutable vía `python -m src.psicometria`."""
    import argparse
    import sys
    from pathlib import Path

    import pandas as pd

    # Asegurar salida UTF-8 en consolas Windows (cp1252) para símbolos unicode
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    PROJECT_ROOT = Path.cwd()
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from src.psicometria.reporte import generar_reporte_texto, generar_reporte_pdf
    from src.psicometria.ejemplos_datos import generar_datos_ejemplo
    from src.psicometria.puntuaciones import validar_datos_respuestas
    from src.psicometria.calidad_datos import reporte_calidad_datos

    parser = argparse.ArgumentParser(
        prog="python -m src.psicometria",
        description="Valida psicométricamente las respuestas de la encuesta (COPSOQ).",
    )
    parser.add_argument("archivo", nargs="?", help="Ruta al CSV de respuestas.")
    parser.add_argument(
        "--pdf",
        nargs="?",
        const="output/reporte_validacion_psicometria.pdf",
        default=None,
        help="Genera reporte PDF en la ruta indicada (default: output/reporte_validacion_psicometria.pdf).",
    )
    args = parser.parse_args(argv)

    def _cargar_datos(ruta):
        if ruta is None:
            return generar_datos_ejemplo(n=200, semilla=42), "(datos sintéticos de demostración)"
        if not Path(ruta).is_file():
            raise FileNotFoundError(f"El archivo no existe: {ruta}")
        return pd.read_csv(ruta), str(ruta)

    try:
        df, ruta_origen = _cargar_datos(args.archivo)
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 2

    if df.empty:
        print("❌ El archivo no contiene datos.", file=sys.stderr)
        return 2

    est = validar_datos_respuestas(df)
    if est["faltantes"]:
        print(f"⚠️ Aviso: faltan {len(est['faltantes'])} ítems del instrumento: "
              f"{', '.join(est['faltantes'])}")
    if len(df) < 150:
        print(f"⚠️ Aviso: muestra de {len(df)} < 150. Recomendado ≥150 para análisis factorial estable.")
    if not est["tiene_outcome"]:
        print("⚠️ Aviso: sin columna 'intencion_rotacion'. Se omite la validez de criterio.")

    # Control de calidad de datos antes de validar
    calidad = reporte_calidad_datos(df)
    if calidad["advertencias"]:
        print("\n📋 Control de calidad de datos:")
        for adv in calidad["advertencias"]:
            print(f"  [!] {adv}")
        if calidad["items_varianza_cero"]:
            print(f"  -> Sugerencia: elimina los ítems con varianza nula "
                  f"({', '.join(calidad['items_varianza_cero'])}) para evitar errores en el AFE.")

    print(generar_reporte_texto(df, ruta_origen))

    if args.pdf:
        ruta_pdf = generar_reporte_pdf(df, args.pdf, ruta_origen)
        print(f"\n📄 Reporte PDF generado: {ruta_pdf}")

    return 0


if __name__ == "__main__":
    sys.exit(main())