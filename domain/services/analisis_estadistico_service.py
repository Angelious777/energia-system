from statistics import mean, stdev

from infrastructure.database.cassandra.cassandra_consumo_repository import (
    CassandraConsumoRepository
)

from datetime import datetime


repository = CassandraConsumoRepository()


def analizar_consumo(
    dispositivo_id,
    consumo_actual
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

    # evitar análisis con pocos datos
    if len(consumos) < 5:

        return {
            "anomalia": False,
            "motivo": "Datos insuficientes"
        }

    promedio = mean(consumos)

    desviacion = stdev(consumos)

    limite_superior = promedio + (
        2 * desviacion
    )

    hay_anomalia = (
        consumo_actual > limite_superior
    )

    return {

        "anomalia": hay_anomalia,

        "promedio": round(promedio, 2),

        "desviacion": round(desviacion, 2),

        "limite_superior": round(
            limite_superior,
            2
        ),

        "consumo_actual": consumo_actual
    }