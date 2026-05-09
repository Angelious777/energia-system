from infrastructure.database.redis.redis_config import redis_client

from domain.services.cassandra_service import (
    guardar_alerta,
    guardar_consumo,
    guardar_consumo_zona
)

from domain.services.stream_service import (
    guardar_cache_consumo,
    publicar_alerta
)

from domain.services.cache_service import (
    guardar_cache_zona
)

from domain.services.alerta_domain_service import (
    generar_alerta
)

from domain.services.analisis_estadistico_service import (
    analizar_consumo
)

from domain.entities.consumo import Consumo

from config.logging_config import logger

import datetime
import uuid
import time


# =========================================
# CONFIG REDIS STREAMS
# =========================================

STREAM_NAME = "consumo_stream"

GROUP_NAME = "grupo_consumo_energia"

CONSUMER_NAME = f"worker-{uuid.uuid4().hex[:6]}"


logger.info(
    f"Worker iniciado: {CONSUMER_NAME}"
)


# =========================================
# PROCESAMIENTO
# =========================================

def procesar_evento(datos):

    try:

        dispositivo_id = datos.get(
            "dispositivo_id"
        )

        consumo = float(
            datos.get("consumo", 0)
        )

        zona = datos.get("zona")

        timestamp = datos.get("timestamp")

        if not dispositivo_id or not zona:

            raise ValueError(
                "Datos incompletos"
            )

        # =========================
        # ENTITY
        # =========================

        consumo_obj = Consumo(
            dispositivo_id=dispositivo_id,
            consumo=consumo,
            zona=zona,
            timestamp=datetime.datetime.fromisoformat(
                timestamp
            )
        )

        logger.info(
            f"Procesando consumo: "
            f"{dispositivo_id} -> {consumo}"
        )

        # =========================
        # PERSISTENCIA
        # =========================

        guardar_consumo(
            vars(consumo_obj)
        )

        guardar_consumo_zona(
            vars(consumo_obj)
        )

        # =========================
        # CACHE
        # =========================

        guardar_cache_consumo(
            vars(consumo_obj)
        )

        guardar_cache_zona(
            vars(consumo_obj)
        )

        # =========================
        # ANÁLISIS ESTADÍSTICO
        # =========================

        resultado = analizar_consumo(
            dispositivo_id,
            consumo
        )

        logger.info(
            f"Resultado análisis: "
            f"{resultado}"
        )

        if resultado["anomalia"]:

            alerta_obj = generar_alerta(
                vars(consumo_obj)
            )

            if alerta_obj:

                alerta_dict = {

                    "alerta_id":
                        alerta_obj.alerta_id,

                    "dispositivo_id":
                        alerta_obj.dispositivo_id,

                    "zona":
                        alerta_obj.zona,

                    "consumo":
                        alerta_obj.consumo,

                    "severidad":
                        alerta_obj.severidad,

                    "recomendacion":
                        alerta_obj.recomendacion,

                    "timestamp":
                        alerta_obj.timestamp,

                    "fecha":
                        alerta_obj.timestamp.date().isoformat()
                }

                logger.warning(
                    f"ALERTA: {alerta_dict}"
                )

                guardar_alerta(
                    alerta_dict
                )

                publicar_alerta(
                    alerta_dict
                )

    except Exception as e:

        logger.error(
            f"Error procesando evento: {e}",
            exc_info=True
        )


# =========================================
# LOOP PRINCIPAL
# =========================================

while True:

    try:

        eventos = redis_client.xreadgroup(

            GROUP_NAME,

            CONSUMER_NAME,

            {STREAM_NAME: ">"},

            count=10,

            block=5000
        )

        if not eventos:
            continue

        for stream, mensajes in eventos:

            for mensaje_id, datos in mensajes:

                logger.info(
                    f"Mensaje recibido: "
                    f"{mensaje_id}"
                )

                procesar_evento(datos)

                # =====================
                # ACK
                # =====================

                redis_client.xack(
                    STREAM_NAME,
                    GROUP_NAME,
                    mensaje_id
                )

                logger.info(
                    f"ACK enviado: "
                    f"{mensaje_id}"
                )

    except Exception as e:

        logger.error(
            f"Error worker principal: {e}",
            exc_info=True
        )

        time.sleep(2)