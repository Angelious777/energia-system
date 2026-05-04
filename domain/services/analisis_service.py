from infrastructure.database.redis.redis_config import redis_client

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

def detectar_consumo_excesivo(evento):

    consumo = float(evento["consumo"])

    if consumo > 100:
        return True

    return False