from statistics import mean, stdev

from datetime import datetime


def analizar_consumo(
    dispositivo_id,
    consumo_actual,
    repository
):

    fecha = datetime.utcnow().date()

    historial = repository.obtener_historial(
        dispositivo_id,
        fecha
    )

    consumos = [
        c.consumo
        for c in historial
    ]

    # evitar análisis pobre
    if len(consumos) < 5:

        return {
            "anomalia": False,
            "motivo": "Datos insuficientes"
        }

    # excluir evento actual
    consumos = consumos[:-1]

    if len(consumos) < 5:

        return {
            "anomalia": False,
            "motivo": "Historial insuficiente"
        }

    promedio = mean(consumos)

    desviacion = stdev(consumos)

    if desviacion == 0:

        return {
            "anomalia": False,
            "motivo": "Sin variabilidad"
        }

    limite_superior = promedio + (
        2 * desviacion
    )

    umbral_relevante = promedio + (
        1.5 * desviacion
    )

    recientes = consumos[-5:]

    repeticiones = len([
        valor for valor in recientes
        if valor > umbral_relevante
    ])

    ratio = consumo_actual / promedio if promedio > 0 else 0

    hay_anomalia = (
        consumo_actual > promedio + (3 * desviacion)
        or (
            consumo_actual > limite_superior
            and repeticiones >= 2
        )
    )

    return {

        "anomalia": hay_anomalia,

        "motivo": (
            "Picos recurrentes detectados" if repeticiones >= 2
            else "Pico aislado"
        ),

        "promedio": round(
            promedio,
            2
        ),

        "desviacion": round(
            desviacion,
            2
        ),

        "limite_superior": round(
            limite_superior,
            2
        ),

        "repeticiones": repeticiones,

        "ratio": round(ratio, 2),

        "consumo_actual": consumo_actual
    }