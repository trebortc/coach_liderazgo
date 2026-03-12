FASES = ["META", "REALIDAD", "OPCIONES", "VOLUNTAD", "REFLEXION"]

def siguiente_fase(fase_actual: str) -> str:
    try:
        index = FASES.index(fase_actual)
        return FASES[index + 1]
    except (ValueError, IndexError):
        return "REFLEXION"