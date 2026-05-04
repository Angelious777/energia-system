from infrastructure.database.redis.redis_config import (
    redis_client
)


def obtener_alertas_recientes():

    alertas = redis_client.xrevrange(
        "alertas_stream",
        count=20
    )

    resultado = []

    for alerta_id, datos in alertas:

        resultado.append({

            "stream_id":
                alerta_id,

            "alerta_id":
                datos["alerta_id"],

            "fecha":
                datos["fecha"],

            "timestamp":
                datos["timestamp"],

            "dispositivo_id":
                datos["dispositivo_id"],

            "zona":
                datos["zona"],

            "consumo":
                datos["consumo"],

            "severidad":
                datos["severidad"],

            "recomendacion":
                datos["recomendacion"]
        })

    return resultado