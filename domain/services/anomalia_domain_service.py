from infrastructure.database.redis.redis_config import redis_client

def detectar_anomalia_consecutiva(
    dispositivo_id,
    consumo,
    umbral=100,
    limite=3
):

    clave = (
        f"contador_alertas:{dispositivo_id}"
    )

    if consumo > umbral:

        contador = redis_client.incr(clave)

        redis_client.expire(clave, 300)

        if contador >= limite:

            redis_client.delete(clave)

            return True

    else:

        redis_client.delete(clave)

    return False