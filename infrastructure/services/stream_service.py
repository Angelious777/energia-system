from infrastructure.database.redis.redis_config import redis_client
import json


STREAM_NAME = "consumo_stream"


def publicar_evento(data):

    redis_client.xadd(
        STREAM_NAME,
        data
    )


def publicar_consumo_realtime(evento):

    evento_realtime = {
        "dispositivo_id": evento["dispositivo_id"],
        "zona": evento["zona"],
        "consumo": float(evento["consumo"]),
        "timestamp": str(evento["timestamp"]),
        "event_id": evento.get("event_id")
    }

    redis_client.publish(
        "realtime_consumo",
        json.dumps(evento_realtime)
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
        json.dumps(alerta_redis)
    )

    redis_client.xadd(
        "alertas_stream",
        alerta_redis
    )