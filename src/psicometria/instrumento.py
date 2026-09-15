"""Definición del instrumento psicosocial.

Cuestionario basado en COPSOQ-ISTAS21 (Moncada et al., 2014), validado en
español. Mide DOS constructos por separado (Job Demands y Job Resources),
según el modelo Job Demands-Resources (Bakker & Demerouti, 2007).

⚠️ Aviso ético: Este instrumento es de uso grupal/psicosocial. No es un test
psicométrico clínico ni diagnóstico. No debe usarse para decisiones
individuales de personal.

Escala: Likert 1-5 (1 = nunca/casi nunca, 5 = siempre/casi siempre).
"""

# Cada ítem: id -> metadatos
#   dimension: 'demandas' | 'recursos'
#   subdimension: subescala para reporte
#   reversa: True si el ítem debe invertirse al puntuar
ITEMS = {
    # ---- DEMANDAS ----
    "d_cant_1": {
        "texto": "¿Tienes que trabajar muy rápido?",
        "dimension": "demandas",
        "subdimension": "cuantitativas",
        "reversa": False,
    },
    "d_cant_2": {
        "texto": "¿Tu trabajo exige demasiada cantidad de trabajo?",
        "dimension": "demandas",
        "subdimension": "cuantitativas",
        "reversa": False,
    },
    "d_cant_3": {
        "texto": "¿Tu ritmo de trabajo te desborda?",
        "dimension": "demandas",
        "subdimension": "cuantitativas",
        "reversa": False,
    },
    "d_emoc_1": {
        "texto": "¿Tu trabajo exige implicarte emocionalmente?",
        "dimension": "demandas",
        "subdimension": "emocionales",
        "reversa": False,
    },
    "d_emoc_2": {
        "texto": "¿Tu trabajo te obliga a reprimir emociones?",
        "dimension": "demandas",
        "subdimension": "emocionales",
        "reversa": False,
    },
    "d_emoc_3": {
        "texto": "¿Atiendes personas en situaciones difíciles?",
        "dimension": "demandas",
        "subdimension": "emocionales",
        "reversa": False,
    },
    # ---- RECURSOS ----
    "r_apoy_1": {
        "texto": "¿Tu superior inmediato te apoya para terminar el trabajo?",
        "dimension": "recursos",
        "subdimension": "apoyo_superior",
        "reversa": False,
    },
    "r_apoy_2": {
        "texto": "¿Tu superior inmediato valora tu trabajo?",
        "dimension": "recursos",
        "subdimension": "apoyo_superior",
        "reversa": False,
    },
    "r_apoy_3": {
        "texto": "¿Tu superior inmediato te da feedback claro sobre tu desempeño?",
        "dimension": "recursos",
        "subdimension": "apoyo_superior",
        "reversa": False,
    },
    "r_auto_1": {
        "texto": "¿Tienes influencia sobre cómo haces tu trabajo?",
        "dimension": "recursos",
        "subdimension": "autonomia",
        "reversa": False,
    },
    "r_auto_2": {
        "texto": "¿Tienes control sobre la cantidad de trabajo que se te asigna?",
        "dimension": "recursos",
        "subdimension": "autonomia",
        "reversa": False,
    },
    "r_clar_1": {
        "texto": "¿Sabes cuáles son tus responsabilidades exactas?",
        "dimension": "recursos",
        "subdimension": "claridad_rol",
        "reversa": False,
    },
    "r_clar_2": {
        "texto": "¿Conoces los objetivos de tu puesto?",
        "dimension": "recursos",
        "subdimension": "claridad_rol",
        "reversa": False,
    },
}

# Ítems de criterio (outcome). No forman parte de demandas/recursos.
CRITERIO_ITEMS = [
    "Estoy pensando activamente en buscar otro trabajo.",
    "A menudo deseo dejar esta organización.",
    "Probablemente cambiaré de trabajo en los próximos 12 meses.",
]

# Subescalas por dimensión (para reporte)
SUBESCALAS = {
    "demandas": ["cuantitativas", "emocionales"],
    "recursos": ["apoyo_superior", "autonomia", "claridad_rol"],
}

DIMENSIONES = ["demandas", "recursos"]


def items_de_dimension(dimension: str) -> list:
    """Retorna la lista de ids de ítems de una dimensión ('demandas'|'recursos')."""
    return [iid for iid, meta in ITEMS.items() if meta["dimension"] == dimension]


def validar_instrumento() -> list:
    """Valida la coherencia del instrumento.

    Returns:
        list de errores encontrados (vacío si el instrumento es válido).
    """
    errores = []
    if not ITEMS:
        errores.append("El instrumento no define ítems.")
        return errores

    ids = set(ITEMS.keys())
    for iid, meta in ITEMS.items():
        if meta["dimension"] not in DIMENSIONES:
            errores.append(f"Ítem {iid}: dimensión inválida '{meta['dimension']}'.")
        if "texto" not in meta or not meta["texto"].strip():
            errores.append(f"Ítem {iid}: falta texto.")
        if "reversa" not in meta or not isinstance(meta["reversa"], bool):
            errores.append(f"Ítem {iid}: campo 'reversa' debe ser booleano.")

    for dimension in DIMENSIONES:
        if not items_de_dimension(dimension):
            errores.append(f"La dimensión '{dimension}' no tiene ítems.")
        else:
            for iid in items_de_dimension(dimension):
                sub = ITEMS[iid]["subdimension"]
                if sub not in SUBESCALAS[dimension]:
                    errores.append(f"Ítem {iid}: subdimensión '{sub}' no declarada en {dimension}.")

    for subescala_lista in SUBESCALAS.values():
        for sub in subescala_lista:
            if not any(ITEMS[i]["subdimension"] == sub for i in ids):
                errores.append(f"Subescala '{sub}' declarada pero sin ítems.")

    return errores