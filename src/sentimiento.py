from pysentimiento import create_analyzer

analizador = create_analyzer(task="sentiment", lang="es")

comentarios = [
    "Me siento agotado, las horas extra no paran nunca",
    "Excelente ambiente de trabajo, mi jefe me apoya mucho",
    "No veo oportunidades de crecimiento aquí, estoy pensando en irme",
    "Estoy contento con mi equipo y el balance de vida",
    "El salario no compensa la carga de trabajo que tengo",
    "Me gusta lo que hago, aunque el estrés a veces es mucho",
]

print("Análisis de sentimiento de comentarios de encuesta:\n")
for comentario in comentarios:
    resultado = analizador.predict(comentario)
    print(f'"{comentario}"')
    print(f"  → Sentimiento: {resultado.output} (confianza: {resultado.probas})\n")
