FASES_GROW = ["META", "REALIDAD", "OPCIONES", "VOLUNTAD"]

def siguiente_fase(fase_actual):
    try:
        idx = FASES_GROW.index(fase_actual)
        return FASES_GROW[idx + 1]
    except (ValueError, IndexError):
        return "META"