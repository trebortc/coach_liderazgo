import random

PREGUNTAS = {
    "META": [
        "¿Qué te gustaría lograr realmente?",
        "¿Por qué esta meta es importante para ti?"
    ],
    "REALIDAD": [
        "¿Qué está pasando ahora mismo?",
        "¿Qué dificultades estás enfrentando?"
    ],
    "OPCIONES": [
        "¿Qué alternativas podrías considerar?",
        "¿Qué opciones están bajo tu control?"
    ],
    "VOLUNTAD": [
        "¿Qué acción concreta vas a tomar?",
        "¿Cuándo te comprometes a hacerlo?"
    ]
}

def obtener_pregunta(fase):
    return random.choice(PREGUNTAS.get(fase, []))
