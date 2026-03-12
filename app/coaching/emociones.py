EMOCIONES = {
    "estres": ["estresado", "agotado", "presión", "cansado"],
    "tristeza": ["triste", "desanimado", "vacío"],
    "frustracion": ["frustrado", "molesto", "impotente"],
    "alegria": ["feliz", "motivado", "contento"]
}

def detectar_emocion(texto: str) -> str:
    texto = texto.lower()
    for emocion, palabras in EMOCIONES.items():
        for p in palabras:
            if p in texto:
                return emocion
    return "neutral"
