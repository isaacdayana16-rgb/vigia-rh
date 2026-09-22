"""Definición del instrumento psicosocial OFICIAL (Ministerio del Trabajo, Ecuador).

Cuestionario de Evaluación de Riesgo Psicosocial del MDT-Ecuador (58 ítems,
escala Likert 1-4, sumatoria simple por dimensión con puntos de corte oficiales).

FUENTE PRIMARIA (leída y transcrita del PDF oficial; NO reconstruida de memoria):
    "Guía para la aplicación del cuestionario de evaluación de riesgo psicosocial",
    Ministerio del Trabajo del Ecuador — Dirección de Seguridad, Salud en el
    Trabajo y Gestión Integral de Riesgos (DSSTGIR).
    PDF oficial publicado en trabajo.gob.ec (carpeta wp-content/uploads/2024/01/).
    El texto interno lleva fecha "Octubre 2018": es la versión vigente alojada
    en el sitio oficial al momento de la transcripción (septiembre 2026).
    URL oficial:
    https://www.trabajo.gob.ec/wp-content/uploads/2024/01/Guia-para-la-aplicacion-del-cuestionario-de-prevencion-de-riesgo-psicosocial.pdf
    Copia local verificable: docs/fuentes/guia_aplicacion_cuestionario_mdt_ecuador.pdf
    y extracto de texto: docs/fuentes/guia_mdt_extracto_texto.txt

SECCIONES EXACTAS TRANSCRITAS:
    - Sección 3.3.1 "Diseño del cuestionario", Tabla 1 (escala de respuesta
      1-4) y Tabla 2 (58 ítems agrupados en 8 dimensiones + subescalas de
      "Otros puntos importantes"), págs. 9-10.
    - Tabla 3 "Nivel de riesgo por dimensión" (puntos de corte), pág. 11.
    - Tabla 4 "Nivel de riesgo general", págs. 11-12.
    - Anexo 11.1 "Cuestionario de evaluación de riesgo psicosocial": texto
      literal de los 58 ítems y de los datos generales (campos A-I),
      págs. 23-27.

MARCO LEGAL (citado en el propio PDF, pág. 5):
    Acuerdo Ministerial 82 (16-jun-2017), "Normativa erradicación de la
    discriminación en el ámbito laboral", art. 9: obligatoriedad de un programa
    de prevención de riesgo psicosocial en empresas con más de 10 trabajadores.
    El cuestionario MDT en sí no es de aplicación obligatoria: la empresa puede
    usar otro instrumento con validez y fiabilidad nacional o internacional
    (sección 3.2, pág. 8).

ESCALA (Tabla 1, pág. 9):
    4 = Completamente de acuerdo | 3 = Parcialmente de acuerdo
    2 = Poco de acuerdo          | 1 = En desacuerdo
    (El formulario oficial incluye además una columna "NR" = No Responde;
    en el pipeline se trata como valor faltante/NaN.)

DIRECCIÓN DEL PUNTAJE (Análisis e interpretación de resultados, pág. 27):
    "el menor puntaje indica un mayor riesgo en esa dimensión". A MAYOR
    puntaje total, MENOR riesgo. Los puntos de corte oficiales se definen
    sobre sumatorias simples (Tabla 3) y sobre la suma global (Tabla 4:
    Alto 58-116, Medio 117-174, Bajo 175-232).

PSICOMETRÍA PUBLICADA POR EL MDT (sección 3.3.2, págs. 12-14; muestra n=4346):
    - Universidad Central del Ecuador: alfa global 0.967; alfa por dimensión
      0.806-0.904; validez ítem r > 0.30.
    - Universidad Internacional SEK: alfa global 0.967; alfa por dimensión
      0.675-0.928.
    Nota: estas figuras corresponden a la validación nacional del instrumento,
    no a datos locales del proyecto.

⚠️ Aviso ético: Este instrumento es de uso grupal/psicosocial. No es un test
psicométrico clínico ni diagnóstico. No debe usarse para decisiones
individuales de personal.
"""

# Cada ítem: id oficial (item_01..item_58) -> metadatos
#   dimension: dimensión principal del instrumento oficial (Tabla 2)
#   subdimension: subescala de "Otros puntos importantes" (None en dimensiones
#                 principales); se usa para reporte y análisis
#   El texto de cada ítem es LITERAL del Anexo 11.1 del PDF oficial.
ITEMS = {
    # ---- CARGA Y RITMO DE TRABAJO (4 ítems) ----
    "item_01": {
        "texto": "Considero que son aceptables las solicitudes y requerimientos que me piden otras personas (compañeros de trabajo, usuarios, clientes)",
        "dimension": "carga_ritmo_trabajo",
        "subdimension": None,
    },
    "item_02": {
        "texto": "Decido el ritmo de trabajo en mis actividades",
        "dimension": "carga_ritmo_trabajo",
        "subdimension": None,
    },
    "item_03": {
        "texto": "Las actividades y/o responsabilidades que me fueron asignadas no me causan estrés",
        "dimension": "carga_ritmo_trabajo",
        "subdimension": None,
    },
    "item_04": {
        "texto": "Tengo suficiente tiempo para realizar todas las actividades que me han sido encomendadas dentro de mi jornada laboral",
        "dimension": "carga_ritmo_trabajo",
        "subdimension": None,
    },
    # ---- DESARROLLO DE COMPETENCIAS (4 ítems) ----
    "item_05": {
        "texto": "Considero que tengo los suficientes conocimientos, habilidades y destrezas para desarrollar el trabajo para el cual fuí contratado",
        "dimension": "desarrollo_competencias",
        "subdimension": None,
    },
    "item_06": {
        "texto": "En mi trabajo aprendo y adquiero nuevos conocimientos, habilidades y destrezas de mis compañeros de trabajo",
        "dimension": "desarrollo_competencias",
        "subdimension": None,
    },
    "item_07": {
        "texto": "En mi trabajo se cuenta con un plan de carrera, capacitación y/o entrenamiento para el desarrollo de mis conocimientos, habilidades y destrezas",
        "dimension": "desarrollo_competencias",
        "subdimension": None,
    },
    "item_08": {
        "texto": "En mi trabajo se evalúa objetiva y periódicamente las actividades que realizo",
        "dimension": "desarrollo_competencias",
        "subdimension": None,
    },
    # ---- LIDERAZGO (6 ítems) ----
    "item_09": {
        "texto": "En mi trabajo se reconoce y se da crédito a la persona que realiza un buen trabajo o logran sus objetivos.",
        "dimension": "liderazgo",
        "subdimension": None,
    },
    "item_10": {
        "texto": "Mi jefe inmediato está dispuesto a escuchar propuestas de cambio e iniciativas de trabajo",
        "dimension": "liderazgo",
        "subdimension": None,
    },
    "item_11": {
        "texto": "Mi jefe inmediato establece metas, plazos claros y factibles para el cumplimiento de mis funciones o actividades",
        "dimension": "liderazgo",
        "subdimension": None,
    },
    "item_12": {
        "texto": "Mi jefe inmediato interviene, brinda apoyo, soporte y se preocupa cuando tengo demasiado trabajo que realizar",
        "dimension": "liderazgo",
        "subdimension": None,
    },
    "item_13": {
        "texto": "Mi jefe inmediato me brinda suficientes lineamientos y retroalimentación para el desempeño de mi trabajo",
        "dimension": "liderazgo",
        "subdimension": None,
    },
    "item_14": {
        "texto": "Mi jefe inmediato pone en consideración del equipo de trabajo, las decisiones que pueden afectar a todos.",
        "dimension": "liderazgo",
        "subdimension": None,
    },
    # ---- MARGEN DE ACCIÓN Y CONTROL (4 ítems) ----
    "item_15": {
        "texto": "En mi trabajo existen espacios de discusión para debatir abiertamente los problemas comunes y diferencias de opinión",
        "dimension": "margen_accion_control",
        "subdimension": None,
    },
    "item_16": {
        "texto": "Me es permitido realizar el trabajo con colaboración de mis compañeros de trabajo y/u otras áreas",
        "dimension": "margen_accion_control",
        "subdimension": None,
    },
    "item_17": {
        "texto": "Mi opinión es tomada en cuenta con respecto a fechas límites en el cumplimiento de mis actividades o cuando exista cambio en mis funciones",
        "dimension": "margen_accion_control",
        "subdimension": None,
    },
    "item_18": {
        "texto": "Se me permite aportar con ideas para mejorar las actividades y la organización del trabajo",
        "dimension": "margen_accion_control",
        "subdimension": None,
    },
    # ---- ORGANIZACIÓN DEL TRABAJO (6 ítems) ----
    "item_19": {
        "texto": "Considero que las formas de comunicación en mi trabajo son adecuados, accesibles y de fácil comprensión",
        "dimension": "organizacion_trabajo",
        "subdimension": None,
    },
    "item_20": {
        "texto": "En mi trabajo se informa regularmente de la gestión y logros de la empresa o institución a todos los trabajadores y servidores",
        "dimension": "organizacion_trabajo",
        "subdimension": None,
    },
    "item_21": {
        "texto": "En mi trabajo se respeta y se toma en consideración las limitaciones de las personas con discapacidad para la asignación de roles y tareas",
        "dimension": "organizacion_trabajo",
        "subdimension": None,
    },
    "item_22": {
        "texto": "En mi trabajo tenemos reuniones suficientes y significantes para el cumplimiento de los objetivos",
        "dimension": "organizacion_trabajo",
        "subdimension": None,
    },
    "item_23": {
        "texto": "Las metas y objetivos en mi trabajo son claros y alcanzables",
        "dimension": "organizacion_trabajo",
        "subdimension": None,
    },
    "item_24": {
        "texto": "Siempre dispongo de tareas y actividades a realizar en mi jornada y lugar de trabajo",
        "dimension": "organizacion_trabajo",
        "subdimension": None,
    },
    # ---- RECUPERACIÓN (5 ítems) ----
    "item_25": {
        "texto": "Después del trabajo tengo la suficiente energía como para realizar otras actividades",
        "dimension": "recuperacion",
        "subdimension": None,
    },
    "item_26": {
        "texto": "En mi trabajo se me permite realizar pausas de periodo corto para renovar y recuperar la energía.",
        "dimension": "recuperacion",
        "subdimension": None,
    },
    "item_27": {
        "texto": "En mi trabajo tengo tiempo para dedicarme a reflexionar sobre mi desempeño en el trabajo",
        "dimension": "recuperacion",
        "subdimension": None,
    },
    "item_28": {
        "texto": "Tengo un horario y jornada de trabajo que se ajusta a mis expectativas y exigencias laborales",
        "dimension": "recuperacion",
        "subdimension": None,
    },
    "item_29": {
        "texto": "Todos los días siento que he descansado lo suficiente y que tengo la energía para iniciar mi trabajo",
        "dimension": "recuperacion",
        "subdimension": None,
    },
    # ---- SOPORTE Y APOYO (5 ítems) ----
    "item_30": {
        "texto": "El trabajo está organizado de tal manera que fomenta la colaboración de equipo y el diálogo con otras personas",
        "dimension": "soporte_apoyo",
        "subdimension": None,
    },
    "item_31": {
        "texto": "En mi trabajo percibo un sentimiento de compañerismo y bienestar con mis colegas",
        "dimension": "soporte_apoyo",
        "subdimension": None,
    },
    "item_32": {
        "texto": "En mi trabajo se brinda el apoyo necesario a los trabajadores sustitutos o trabajadores con algún grado de discapacidad y enfermedad",
        "dimension": "soporte_apoyo",
        "subdimension": None,
    },
    "item_33": {
        "texto": "En mi trabajo se me brinda ayuda técnica y administrativa cuando lo requiero",
        "dimension": "soporte_apoyo",
        "subdimension": None,
    },
    "item_34": {
        "texto": "En mi trabajo tengo acceso a la atención de un médico, psicólogo, trabajadora social, consejero, etc. en situaciones de crisis y/o rehabilitación",
        "dimension": "soporte_apoyo",
        "subdimension": None,
    },
    # ---- OTROS PUNTOS IMPORTANTES (24 ítems: 35-58) ----
    "item_35": {
        "texto": "En mi trabajo tratan por igual a todos, indistintamente la edad que tengan",
        "dimension": "otros_puntos_importantes",
        "subdimension": "acoso_discriminatorio",
    },
    "item_36": {
        "texto": "Las directrices y metas que me autoimpongo, las cumplo dentro de mi jornada y horario de trabajo",
        "dimension": "otros_puntos_importantes",
        "subdimension": "adiccion_trabajo",
    },
    "item_37": {
        "texto": "En mi trabajo existe un buen ambiente laboral",
        "dimension": "otros_puntos_importantes",
        "subdimension": "estabilidad_emocional",
    },
    "item_38": {
        "texto": "Tengo un trabajo donde los hombres y mujeres tienen las mismas oportunidades",
        "dimension": "otros_puntos_importantes",
        "subdimension": "acoso_discriminatorio",
    },
    "item_39": {
        "texto": "En mi trabajo me siento aceptado y valorado",
        "dimension": "otros_puntos_importantes",
        "subdimension": "estabilidad_emocional",
    },
    "item_40": {
        "texto": "Los espacios y ambientes físicos en mi trabajo brindan las facilidades para el acceso de las personas con discapacidad",
        "dimension": "otros_puntos_importantes",
        "subdimension": "condiciones_trabajo",
    },
    "item_41": {
        "texto": "Considero que mi trabajo está libre de amenazas, humillaciones, ridiculizaciones, burlas, calumnias o difamaciones reiteradas con el fin de causarme daño",
        "dimension": "otros_puntos_importantes",
        "subdimension": "acoso_laboral",
    },
    "item_42": {
        "texto": "Me siento estable a pesar de cambios que se presentan en mi trabajo",
        "dimension": "otros_puntos_importantes",
        "subdimension": "estabilidad_emocional",
    },
    "item_43": {
        "texto": "En mi trabajo estoy libre de conductas sexuales que afecten mi integridad física, psicológica y moral",
        "dimension": "otros_puntos_importantes",
        "subdimension": "acoso_sexual",
    },
    "item_44": {
        "texto": "Considero que el trabajo que realizo no me causa efectos negativos a mi salud física y mental",
        "dimension": "otros_puntos_importantes",
        "subdimension": "salud_auto_percebida",
    },
    "item_45": {
        "texto": "Me resulta fácil relajarme cuando no estoy trabajando",
        "dimension": "otros_puntos_importantes",
        "subdimension": "adiccion_trabajo",
    },
    "item_46": {
        "texto": "Siento que mis problemas familiares o personales no influyen en el desempeño de las actividades en el trabajo",
        "dimension": "otros_puntos_importantes",
        "subdimension": "doble_presencia",
    },
    "item_47": {
        "texto": "Las instalaciones, ambientes, equipos, maquinaria y herramientas que utilizo para realizar el trabajo son las adecuadas para no sufrir accidentes de trabajo y enfermedades profesionales",
        "dimension": "otros_puntos_importantes",
        "subdimension": "condiciones_trabajo",
    },
    "item_48": {
        "texto": "Mi trabajo esta libre de acoso sexual",
        "dimension": "otros_puntos_importantes",
        "subdimension": "acoso_sexual",
    },
    "item_49": {
        "texto": "En mi trabajo se me permite solucionar mis problemas familiares y personales",
        "dimension": "otros_puntos_importantes",
        "subdimension": "doble_presencia",
    },
    "item_50": {
        "texto": "Tengo un trabajo libre de conflictos estresantes, rumores maliciosos o calumniosos sobre mi persona",
        "dimension": "otros_puntos_importantes",
        "subdimension": "acoso_laboral",
    },
    "item_51": {
        "texto": "Tengo un equilibrio y separo bien el trabajo de mi vida personal",
        "dimension": "otros_puntos_importantes",
        "subdimension": "adiccion_trabajo",
    },
    "item_52": {
        "texto": "Estoy orgulloso de trabajar en mi empresa o institución",
        "dimension": "otros_puntos_importantes",
        "subdimension": "estabilidad_emocional",
    },
    "item_53": {
        "texto": "En mi trabajo se respeta mi ideología, opinión política, religiosa, nacionalidad y orientación sexual.",
        "dimension": "otros_puntos_importantes",
        "subdimension": "acoso_discriminatorio",
    },
    "item_54": {
        "texto": "Mi trabajo y los aportes que realizo son valorados y me generan motivación",
        "dimension": "otros_puntos_importantes",
        "subdimension": "estabilidad_emocional",
    },
    "item_55": {
        "texto": "Me siento libre de culpa cuando no estoy trabajando en algo",
        "dimension": "otros_puntos_importantes",
        "subdimension": "adiccion_trabajo",
    },
    "item_56": {
        "texto": "En mi trabajo no existen espacios de uso exclusivo de un grupo determinado de personas ligados a un privilegio, por ejemplo, cafetería exclusiva, baños exclusivos, etc., mismo que causa malestar y perjudica mi ambiente laboral",
        "dimension": "otros_puntos_importantes",
        "subdimension": "acoso_discriminatorio",
    },
    "item_57": {
        "texto": "Puedo dejar de pensar en el trabajo durante mi tiempo libre (pasatiempos, actividades de recreación, otros)",
        "dimension": "otros_puntos_importantes",
        "subdimension": "adiccion_trabajo",
    },
    "item_58": {
        "texto": "Considero que me encuentro física y mentalmente saludable",
        "dimension": "otros_puntos_importantes",
        "subdimension": "salud_auto_percebida",
    },
}

# Dimensiones principales (Tabla 2 del PDF oficial, págs. 9-10)
DIMENSIONES = [
    "carga_ritmo_trabajo",
    "desarrollo_competencias",
    "liderazgo",
    "margen_accion_control",
    "organizacion_trabajo",
    "recuperacion",
    "soporte_apoyo",
    "otros_puntos_importantes",
]

# Subescalas de "Otros puntos importantes" (Tabla 2, págs. 9-10)
SUBESCALAS_OTROS = {
    "acoso_discriminatorio": [35, 38, 53, 56],
    "acoso_laboral": [41, 50],
    "acoso_sexual": [43, 48],
    "adiccion_trabajo": [36, 45, 51, 55, 57],
    "condiciones_trabajo": [40, 47],
    "doble_presencia": [46, 49],
    "estabilidad_emocional": [37, 39, 42, 52, 54],
    "salud_auto_percebida": [44, 58],
}

# Puntos de corte por dimensión (Tabla 3 del PDF oficial, pág. 11).
# Escala: sumatoria simple de los ítems de la dimensión.
# menor puntaje = mayor riesgo. Rangos: bajo/medio/alto (mín, máx).
PUNTOS_CORTE = {
    "carga_ritmo_trabajo": {"bajo": (13, 16), "medio": (8, 12), "alto": (4, 7)},
    "desarrollo_competencias": {"bajo": (13, 16), "medio": (8, 12), "alto": (4, 7)},
    "liderazgo": {"bajo": (18, 24), "medio": (12, 17), "alto": (6, 11)},
    "margen_accion_control": {"bajo": (13, 16), "medio": (8, 12), "alto": (4, 7)},
    "organizacion_trabajo": {"bajo": (18, 24), "medio": (12, 17), "alto": (6, 11)},
    "recuperacion": {"bajo": (16, 20), "medio": (10, 15), "alto": (5, 9)},
    "soporte_apoyo": {"bajo": (16, 20), "medio": (10, 15), "alto": (5, 9)},
    "otros_puntos_importantes": {"bajo": (73, 96), "medio": (49, 72), "alto": (24, 48)},
    "acoso_discriminatorio": {"bajo": (13, 16), "medio": (8, 12), "alto": (4, 7)},
    "acoso_laboral": {"bajo": (7, 8), "medio": (5, 6), "alto": (2, 4)},
    "acoso_sexual": {"bajo": (7, 8), "medio": (5, 6), "alto": (2, 4)},
    "adiccion_trabajo": {"bajo": (16, 20), "medio": (10, 15), "alto": (5, 9)},
    "condiciones_trabajo": {"bajo": (7, 8), "medio": (5, 6), "alto": (2, 4)},
    "doble_presencia": {"bajo": (7, 8), "medio": (5, 6), "alto": (2, 4)},
    "estabilidad_emocional": {"bajo": (16, 20), "medio": (10, 15), "alto": (5, 9)},
    "salud_auto_percebida": {"bajo": (7, 8), "medio": (5, 6), "alto": (2, 4)},
}

# Nivel de riesgo general (Tabla 4 del PDF oficial, págs. 11-12).
# Suma de los 58 ítems: Alto 58-116, Medio 117-174, Bajo 175-232.
RIESGO_GLOBAL = {
    "alto": (58, 116),
    "medio": (117, 174),
    "bajo": (175, 232),
}

# Datos generales del cuestionario oficial (Anexo 11.1, págs. 23-24, campos A-I)
# + tipo_jornada (extensión del proyecto; ver docs/CUESTIONARIO.md).
CAMPOS_GENERALES = {
    "fecha": {"etiqueta": "Fecha", "opciones": None},
    "provincia": {"etiqueta": "Provincia", "opciones": None},
    "ciudad": {"etiqueta": "Ciudad", "opciones": None},
    "area_trabajo": {
        "etiqueta": "Área de trabajo",
        "opciones": ["Administrativa", "Operativa"],
    },
    "nivel_instruccion": {
        "etiqueta": "Nivel más alto de instrucción",
        "opciones": [
            "Ninguno",
            "Educación básica",
            "Educación media",
            "Bachillerato",
            "Técnico / Tecnológico",
            "Tercer nivel",
            "Cuarto nivel",
            "Otro",
        ],
    },
    "antiguedad": {
        "etiqueta": "Antigüedad en la empresa o institución",
        "opciones": ["0-2 años", "3-10 años", "11-20 años", "Igual o superior a 21 años"],
    },
    "edad": {
        "etiqueta": "Edad del trabajador o servidor",
        "opciones": [
            "16-24 años",
            "25-34 años",
            "35-43 años",
            "44-52 años",
            "Igual o superior a 53 años",
        ],
    },
    "autoidentificacion_etnica": {
        "etiqueta": "Auto-identificación étnica",
        "opciones": ["Indígena", "Mestizo/a", "Montubio/a", "Afro-ecuatoriano", "Blanco/a", "Otro"],
    },
    "genero": {
        "etiqueta": "Género del trabajador o servidor",
        "opciones": ["Masculino", "Femenino"],
    },
    "tipo_jornada": {
        "etiqueta": "Tipo de jornada / turno",
        "opciones": ["turno_fijo", "turno_rotativo", "otro"],
    },
}

# Escala de respuesta oficial (Tabla 1, pág. 9)
ESCALA = {
    "minimo": 1,
    "maximo": 4,
    "etiquetas": {
        1: "En desacuerdo",
        2: "Poco de acuerdo",
        3: "Parcialmente de acuerdo",
        4: "Completamente de acuerdo",
    },
}

# Ítem de criterio (outcome) EXTERNO al instrumento oficial. El cuestionario
# MDT no lo incluye: se agrega como columna opcional para la validez de
# criterio (relación con la intención de rotación).
CRITERIO_ITEMS = ["intencion_rotacion"]


def items_de_dimension(dimension: str) -> list:
    """Retorna la lista de ids de ítems de una dimensión del instrumento."""
    return [iid for iid, meta in ITEMS.items() if meta["dimension"] == dimension]


def items_de_subescala(subescala: str) -> list:
    """Retorna la lista de ids de ítems de una subescala de 'Otros puntos importantes'."""
    return [f"item_{n:02d}" for n in SUBESCALAS_OTROS.get(subescala, [])]


def clasificar_riesgo_dimension(dimension: str, suma) -> str:
    """Clasifica una sumatoria por dimensión según la Tabla 3 oficial.

    Args:
        dimension: Nombre de la dimensión (claves de PUNTOS_CORTE).
        suma: Sumatoria simple de los ítems de la dimensión.

    Returns:
        'Bajo', 'Medio', 'Alto', o None si la suma es NaN o está fuera de rango.
    """
    if suma is None or suma != suma:
        return None
    cortes = PUNTOS_CORTE.get(dimension)
    if cortes is None:
        return None
    for nivel, (minimo, maximo) in cortes.items():
        if minimo <= suma <= maximo:
            return {"bajo": "Bajo", "medio": "Medio", "alto": "Alto"}[nivel]
    return None


def clasificar_riesgo_global(suma) -> str:
    """Clasifica la suma global (58 ítems) según la Tabla 4 oficial.

    Returns:
        'Bajo', 'Medio', 'Alto', o None si la suma es NaN o está fuera de rango.
    """
    if suma is None or suma != suma:
        return None
    for nivel, (minimo, maximo) in RIESGO_GLOBAL.items():
        if minimo <= suma <= maximo:
            return {"bajo": "Bajo", "medio": "Medio", "alto": "Alto"}[nivel]
    return None


def validar_instrumento() -> list:
    """Valida la coherencia estructural del instrumento contra el PDF oficial.

    Comprueba: 58 ítems, textos, dimensiones/subescalas declaradas, y que los
    puntos de corte (Tabla 3) cubran el rango completo de la sumatoria de cada
    dimensión/subescala.

    Returns:
        list de errores encontrados (vacío si el instrumento es válido).
    """
    errores = []
    if not ITEMS:
        errores.append("El instrumento no define ítems.")
        return errores

    if len(ITEMS) != 58:
        errores.append(f"El instrumento oficial tiene 58 ítems; se definieron {len(ITEMS)}.")

    ids_esperados = {f"item_{n:02d}" for n in range(1, 59)}
    ids = set(ITEMS.keys())
    if ids != ids_esperados:
        errores.append(
            "Los ids de ítems deben ser item_01..item_58 (numeración oficial del MDT)."
        )

    for iid, meta in ITEMS.items():
        if meta["dimension"] not in DIMENSIONES:
            errores.append(f"Ítem {iid}: dimensión inválida '{meta['dimension']}'.")
        if "texto" not in meta or not meta["texto"].strip():
            errores.append(f"Ítem {iid}: falta texto.")

    for dimension in DIMENSIONES:
        if not items_de_dimension(dimension):
            errores.append(f"La dimensión '{dimension}' no tiene ítems.")

    for subescala, numeros in SUBESCALAS_OTROS.items():
        if not numeros:
            errores.append(f"La subescala '{subescala}' no tiene ítems.")
        for n in numeros:
            iid = f"item_{n:02d}"
            if iid not in ITEMS:
                errores.append(f"Subescala '{subescala}': ítem {iid} no existe.")
            elif ITEMS[iid]["subdimension"] != subescala:
                errores.append(f"Ítem {iid}: no está asignado a la subescala '{subescala}'.")

    for iid, meta in ITEMS.items():
        if meta["dimension"] == "otros_puntos_importantes":
            sub = meta.get("subdimension")
            if sub not in SUBESCALAS_OTROS:
                errores.append(f"Ítem {iid}: subdimensión '{sub}' no declarada en SUBESCALAS_OTROS.")

    # Puntos de corte: cubrir el rango completo de la sumatoria
    def _rango_items(numeros: list) -> tuple:
        return len(numeros) * ESCALA["minimo"], len(numeros) * ESCALA["maximo"]

    cortes_para_validar = {
        dim: _rango_items(items_de_dimension(dim)) for dim in DIMENSIONES
    }
    cortes_para_validar.update(
        {sub: _rango_items(numeros) for sub, numeros in SUBESCALAS_OTROS.items()}
    )
    for nombre, (rango_min, rango_max) in cortes_para_validar.items():
        cortes = PUNTOS_CORTE.get(nombre)
        if cortes is None:
            errores.append(f"Faltan puntos de corte (Tabla 3) para '{nombre}'.")
            continue
        todo = sorted(cortes.values())
        cubierto = todo[0][0] == rango_min and todo[-1][1] == rango_max
        contiguo = all(
            todo[i][1] + 1 == todo[i + 1][0] for i in range(len(todo) - 1)
        )
        if not (cubierto and contiguo):
            errores.append(
                f"Puntos de corte de '{nombre}' no cubren el rango {rango_min}-{rango_max} de forma contigua."
            )

    if sorted(RIESGO_GLOBAL.values()) != [(58, 116), (117, 174), (175, 232)]:
        errores.append("El rango global (Tabla 4) no coincide con el PDF oficial (58-116/117-174/175-232).")

    return errores
