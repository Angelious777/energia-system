from infrastructure.database.redis.redis_config import redis_client
import json


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