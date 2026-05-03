def detectar_consumo_excesivo(promedio):

    if promedio > 500:
        return True

    return False


def generar_recomendacion(
    movimiento,
    potencia
):

    if not movimiento and potencia > 300:

        return (
            "Apagar luces por inactividad"
        )

    return None