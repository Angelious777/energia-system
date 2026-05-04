from infrastructure.database.redis.redis_config import redis_client
import json


STREAM_NAME = "consumo_stream"


def publicar_evento(data):

    redis_client.xadd(
        STREAM_NAME,
        data
    )


def guardar_cache_consumo(evento):

    clave = f"consumo:dispositivo:{evento['dispositivo_id']}"

    redis_client.set(
        clave,
        evento["consumo"]
    )

    redis_client.expire(
        clave,
        60
    )


def publicar_alerta(alerta):

    alerta_redis = {

        "alerta_id": str(alerta["alerta_id"]),
        "fecha": str(alerta["fecha"]),
        "timestamp": str(alerta["timestamp"]),
        "dispositivo_id": alerta["dispositivo_id"],
        "zona": alerta["zona"],
        "consumo": str(alerta["consumo"]),
        "severidad": alerta["severidad"],
        "recomendacion": alerta["recomendacion"]
    }

    redis_client.publish(
        "consumo_excesivo",
        str(alerta_redis)
    )

    redis_client.xadd(
        "alertas_stream",
        alerta_redis
    )