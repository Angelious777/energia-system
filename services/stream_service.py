from config.redis_config import redis_client
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


def guardar_cache_zona(evento):

    clave = f"consumo:zona:{evento['zona']}"

    redis_client.set(
        clave,
        evento["consumo"]
    )

    redis_client.expire(
        clave,
        60
    )


def publicar_alerta(evento):

    redis_client.publish(
        "consumo_excesivo",
        str(evento)
    )

    redis_client.xadd(
        "alertas_stream",
        evento
    )