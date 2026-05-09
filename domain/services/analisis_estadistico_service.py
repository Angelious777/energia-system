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

    hay_anomalia = (
        consumo_actual > limite_superior
    )

    return {

        "anomalia": hay_anomalia,

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

        "consumo_actual": consumo_actual
    }