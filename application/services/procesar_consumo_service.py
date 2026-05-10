from infrastructure.services.metricas_service import (
    incrementar_consumo_zona,
    incrementar_dispositivo,
    incrementar_alerta
)

from infrastructure.services.idempotencia_service import (
    evento_ya_procesado,
    marcar_evento_procesado
)

from infrastructure.services.cassandra_service import (
    guardar_alerta,
    guardar_consumo,
    guardar_consumo_zona
)

from infrastructure.services.realtime_service import (
    publicar_alerta,
    publicar_consumo_realtime
)

from infrastructure.services.cache_service import (
    guardar_cache_consumo,
    guardar_cache_zona
)

from domain.services.motor_inteligente_service import motor_inteligente

from domain.entities.consumo import Consumo

from config.logging_config import logger

import datetime
import uuid


def procesar_consumo_service(datos, repository):

    try:
        dispositivo_id = datos.get("dispositivo_id")
        consumo = float(datos.get("consumo", 0))
        zona = datos.get("zona")
        event_id = datos.get("event_id") or str(uuid.uuid4())
        timestamp_str = datos.get("timestamp")

        # =========================
        # IDEMPOTENCIA
        # =========================
        if evento_ya_procesado(event_id):
            logger.warning(f"Evento duplicado ignorado: {event_id}")
            return True

        # =========================
        # VALIDACIÓN
        # =========================
        if not dispositivo_id or zona is None:
            raise ValueError("Datos incompletos")

        # =========================
        # TIMESTAMP
        # =========================
        if timestamp_str:
            timestamp = datetime.datetime.fromisoformat(timestamp_str)
        else:
            timestamp = datetime.datetime.utcnow()

        # =========================
        # ENTITY
        # =========================
        consumo_obj = Consumo(
            event_id=event_id,
            dispositivo_id=dispositivo_id,
            zona=zona,
            consumo=consumo,
            timestamp=timestamp
        )

        logger.info(
            f"Procesando consumo {dispositivo_id} -> {consumo}"
        )

        # =========================
        # PERSISTENCIA
        # =========================
        guardar_consumo(vars(consumo_obj))
        guardar_consumo_zona(vars(consumo_obj))

        # =========================
        # CACHE + REALTIME
        # =========================
        guardar_cache_consumo(vars(consumo_obj))
        guardar_cache_zona(vars(consumo_obj))
        publicar_consumo_realtime(vars(consumo_obj))

        # =========================
        # MÉTRICAS
        # =========================
        incrementar_consumo_zona(zona, consumo)
        incrementar_dispositivo(dispositivo_id, consumo)

        # =========================
        # MOTOR INTELIGENTE
        # =========================
        resultado = motor_inteligente(vars(consumo_obj), repository)

        logger.info(f"Motor inteligente: {resultado}")

        # =========================
        # ALERTAS
        # =========================
        if resultado["anomalia"]:

            alerta = resultado["alerta"]

            if alerta:

                alerta_dict = {
                    "alerta_id": alerta.alerta_id,
                    "dispositivo_id": alerta.dispositivo_id,
                    "zona": alerta.zona,
                    "consumo": alerta.consumo,
                    "severidad": alerta.severidad,
                    "recomendacion": alerta.recomendacion,
                    "timestamp": alerta.timestamp,
                    "fecha": alerta.timestamp.date().isoformat()
                }

                logger.warning(f"ALERTA DETECTADA: {alerta_dict}")

                guardar_alerta(alerta_dict)
                publicar_alerta(alerta_dict)

                incrementar_alerta(alerta.severidad)

        # =========================
        # MARCAR EVENTO
        # =========================
        marcar_evento_procesado(event_id)

        return True

    except Exception as e:
        logger.error(f"Error procesando evento: {e}", exc_info=True)
        return False