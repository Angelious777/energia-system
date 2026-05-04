from infrastructure.database.redis.redis_config import redis_client

class RedisCacheRepository:
    def guardar_consumo(self, evento):
        clave = f"consumo:dispositivo:{evento['dispositivo_id']}"
        redis_client.set(clave, evento["consumo"])
        redis_client.expire(clave, 60)  # Expira en 60 segundos

    def guardar_zona(self, evento):
        zona = evento["zona"]
        dispositivo = evento["dispositivo_id"]
        consumo = evento["consumo"]
        clave_zona = f"zona:{zona}:consumos"
        redis_client.hset(clave_zona, dispositivo, consumo)
        redis_client.expire(clave_zona, 3600)  # Expira en 1 hora

    def obtener_consumo_zona(self, zona):
        clave = f"zona:{zona}:consumos"
        return redis_client.hgetall(clave)