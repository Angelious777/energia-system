from config.redis_config import redis_client
import json

def guardar_cache_zona(datos):

    zona = datos["zona"]

    dispositivo = datos["dispositivo_id"]

    consumo = float(datos["consumo"])

    clave = f"zona:{zona}"

    zona_actual = redis_client.get(clave)

    if zona_actual:

        zona_actual = json.loads(zona_actual)

    else:

        zona_actual = {
            "consumo_total": 0,
            "dispositivos": {}
        }

    zona_actual["dispositivos"][dispositivo] = consumo

    zona_actual["consumo_total"] = sum(
        zona_actual["dispositivos"].values()
    )

    redis_client.set(
        clave,
        json.dumps(zona_actual)
    )




def obtener_consumo_zona(zona):

    clave = f"zona:{zona}"

    datos = redis_client.get(clave)

    if not datos:

        return {
            "mensaje": "Zona no encontrada"
        }

    datos = json.loads(datos)

    return {
        "zona": zona,
        "consumo_total": datos["consumo_total"],
        "dispositivos": len(
            datos["dispositivos"]
        )
    }