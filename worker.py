import time
import datetime
import uuid

import redis

from infrastructure.database.redis.redis_config import redis_client

from infrastructure.database.cassandra.cassandra_consumo_repository import (
    CassandraConsumoRepository
)

from application.services.procesar_consumo_service import (
    procesar_consumo_service
)

from config.logging_config import logger


# =========================================
# CONFIG REDIS STREAMS
# =========================================

STREAM_NAME = "consumo_stream"
GROUP_NAME = "grupo_consumo_energia"
MIN_IDLE_TIME = 10000

CONSUMER_NAME = f"worker-{uuid.uuid4().hex[:6]}"

logger.info(f"Worker iniciado: {CONSUMER_NAME}")

# =========================================
# DEPENDENCIAS
# =========================================

cassandra_repository = CassandraConsumoRepository()


# =========================================
# UTILIDADES
# =========================================

def _normalize_stream_entry(datos):
    parsed = {}

    for key, value in datos.items():

        if isinstance(key, bytes):
            key = key.decode('utf-8', 'ignore')

        if isinstance(value, bytes):
            try:
                value = value.decode('utf-8')
            except Exception:
                pass

        parsed[key] = value

    return parsed


def _ensure_stream_group():
    try:
        redis_client.xgroup_create(
            STREAM_NAME,
            GROUP_NAME,
            id='0',
            mkstream=True
        )
    except redis.exceptions.ResponseError as e:
        error_message = str(e)

        if 'BUSYGROUP' in error_message:
            return

        if 'NOGROUP' in error_message:
            # El stream existe pero el grupo no; intentamos crear el grupo nuevamente.
            redis_client.xgroup_create(
                STREAM_NAME,
                GROUP_NAME,
                id='0'
            )
            return

        logger.error(f"Error creando consumer group: {e}", exc_info=True)
        raise


def ensure_stream_group():
    try:
        _ensure_stream_group()
    except Exception as e:
        logger.error(f"No se pudo asegurar el consumer group: {e}", exc_info=True)
        raise


# =========================================
# PROCESAMIENTO PRINCIPAL
# =========================================

def procesar_evento(datos):
    return procesar_consumo_service(datos, cassandra_repository)


# =========================================
# RECUPERACIÓN DE PENDIENTES
# =========================================

def recuperar_pendientes():

    ensure_stream_group()

    try:
        pendientes = redis_client.xpending_range(
            STREAM_NAME,
            GROUP_NAME,
            min='-',
            max='+',
            count=10
        )

        for mensaje in pendientes:

            mensaje_id = mensaje["message_id"]
            idle = mensaje["time_since_delivered"]
            consumidor = mensaje["consumer"]

            if idle > MIN_IDLE_TIME:

                logger.warning(
                    f"Recuperando mensaje {mensaje_id} de {consumidor}"
                )

                reclamado = redis_client.xclaim(
                    STREAM_NAME,
                    GROUP_NAME,
                    CONSUMER_NAME,
                    min_idle_time=MIN_IDLE_TIME,
                    message_ids=[mensaje_id]
                )

                for msg_id, datos in reclamado:

                    datos = _normalize_stream_entry(datos)

                    if procesar_evento(datos):

                        redis_client.xack(
                            STREAM_NAME,
                            GROUP_NAME,
                            msg_id
                        )

                        logger.info(f"Mensaje recuperado ACK: {msg_id}")

    except Exception as e:
        logger.error(f"Error recuperando pendientes: {e}", exc_info=True)


# =========================================
# INIT STREAM GROUP
# =========================================

_ensure_stream_group()


# =========================================
# LOOP PRINCIPAL
# =========================================

while True:

    try:

        recuperar_pendientes()

        ensure_stream_group()

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

                datos = _normalize_stream_entry(datos)

                logger.info(f"Procesando evento: {mensaje_id}")

                if procesar_evento(datos):

                    redis_client.xack(
                        STREAM_NAME,
                        GROUP_NAME,
                        mensaje_id
                    )

                    logger.info(f"ACK enviado: {mensaje_id}")

                else:
                    logger.warning(f"NO procesado: {mensaje_id}")

    except redis.exceptions.ResponseError as e:
        error_message = str(e)

        if 'NOGROUP' in error_message:
            logger.warning(
                "Grupo de consumidor faltante; recreando y reintentando en el siguiente ciclo."
            )
            ensure_stream_group()
            time.sleep(1)
            continue

        logger.error(f"Error worker principal: {e}", exc_info=True)
        time.sleep(2)
    except KeyboardInterrupt:
        logger.info("Worker detenido por interrupción del usuario.")
        break
    except Exception as e:
        logger.error(f"Error worker principal: {e}", exc_info=True)
        time.sleep(2)