from infrastructure.database.redis.redis_config import redis_client


TTL_EVENTO = 3600


def evento_ya_procesado(
    event_id
):

    clave = (
        f"evento_procesado:{event_id}"
    )

    return redis_client.exists(
        clave
    )


def marcar_evento_procesado(
    event_id
):

    clave = (
        f"evento_procesado:{event_id}"
    )

    redis_client.set(
        clave,
        "1",
        ex=TTL_EVENTO
    )