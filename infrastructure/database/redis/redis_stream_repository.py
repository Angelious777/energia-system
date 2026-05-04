from infrastructure.database.redis.redis_config import redis_client

class RedisStreamRepository:
    def publicar_alerta(self, alerta):
        alerta_redis = {
            "alerta_id": str(alerta.alerta_id),
            "fecha": alerta.timestamp.date().isoformat(),
            "timestamp": str(alerta.timestamp),
            "dispositivo_id": alerta.dispositivo_id,
            "zona": alerta.zona,
            "consumo": str(alerta.consumo),
            "severidad": alerta.severidad,
            "recomendacion": alerta.recomendacion
        }
        redis_client.publish("consumo_excesivo", str(alerta_redis))
        redis_client.xadd("alertas_stream", alerta_redis)