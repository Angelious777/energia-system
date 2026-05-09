from infrastructure.database.redis.redis_config import redis_client


# =========================================
# CONSUMO TOTAL POR ZONA
# =========================================

def incrementar_consumo_zona(
    zona,
    consumo
):

    clave = (
        f"metrica:zona:{zona}:total"
    )

    redis_client.incrbyfloat(
        clave,
        consumo
    )


# =========================================
# TOP DISPOSITIVOS
# =========================================

def incrementar_dispositivo(
    dispositivo_id,
    consumo
):

    redis_client.zincrby(

        "metrica:top_dispositivos",

        consumo,

        dispositivo_id
    )


# =========================================
# ALERTAS POR SEVERIDAD
# =========================================

def incrementar_alerta(
    severidad
):

    clave = (
        f"metrica:alertas:{severidad}"
    )

    redis_client.incr(
        clave
    )


# =========================================
# OBTENER TOP DISPOSITIVOS
# =========================================

def obtener_top_dispositivos(
    limite=5
):

    resultado = redis_client.zrevrange(

        "metrica:top_dispositivos",

        0,

        limite - 1,

        withscores=True
    )

    datos = []

    for dispositivo, consumo in resultado:

        datos.append({

            "dispositivo_id":
                dispositivo,

            "consumo_total":
                round(consumo, 2)
        })

    return datos


# =========================================
# OBTENER CONSUMO ZONA
# =========================================

def obtener_consumo_zona(
    zona
):

    clave = (
        f"metrica:zona:{zona}:total"
    )

    valor = redis_client.get(
        clave
    )

    if not valor:
        return 0

    return round(float(valor), 2)


# =========================================
# OBTENER ALERTAS
# =========================================

def obtener_total_alertas(
    severidad
):

    clave = (
        f"metrica:alertas:{severidad}"
    )

    valor = redis_client.get(
        clave
    )

    if not valor:
        return 0

    return int(valor)