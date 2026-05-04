from infrastructure.database.redis.redis_config import redis_client
from domain.services.cassandra_service import guardar_alerta, guardar_consumo, guardar_consumo_zona
from domain.services.stream_service import guardar_cache_consumo, publicar_alerta
from domain.services.analisis_service import detectar_consumo_excesivo
from domain.services.alerta_domain_service import generar_alerta
from domain.services.anomalia_domain_service import detectar_anomalia_consecutiva
from domain.services.cache_service import obtener_consumo_zona, guardar_cache_zona
from config.logging_config import logger

from infrastructure.database.cassandra.cassandra_consumo_repository import CassandraConsumoRepository
from domain.entities.consumo import Consumo
import datetime

repository_consumo = CassandraConsumoRepository()

STREAM_NAME = "consumo_stream"

# Leer desde el inicio (más seguro para pruebas)
ultimo_id = '0'

logger.info("Worker escuchando eventos...")


def procesar_evento(datos):
    try:
        # =========================
        # VALIDACIÓN Y NORMALIZACIÓN
        # =========================
        dispositivo_id = datos.get("dispositivo_id")
        consumo = float(datos.get("consumo", 0))
        zona = datos.get("zona")

        if not dispositivo_id or zona is None:
            raise ValueError("Datos incompletos")

        # =========================
        # CREAR ENTIDAD (DDD REAL)
        # =========================
        consumo_obj = Consumo(
            dispositivo_id=dispositivo_id,
            consumo=consumo,
            zona=zona,
            timestamp=datetime.datetime.utcnow()
        )

        # =========================
        # PERSISTENCIA
        # =========================
        guardar_consumo(vars(consumo_obj))
        guardar_consumo_zona(vars(consumo_obj))

        # =========================
        # CACHE (REDIS)
        # =========================
        guardar_cache_consumo(vars(consumo_obj))
        guardar_cache_zona(vars(consumo_obj))

        # =========================
        # DETECCIÓN DE ANOMALÍAS
        # =========================
        hay_anomalia = detectar_anomalia_consecutiva(
            dispositivo_id,
            consumo
        )

        if hay_anomalia:
            alerta_obj = generar_alerta(vars(consumo_obj))

            if alerta_obj:
                alerta_dict = {
                    "alerta_id": alerta_obj.alerta_id,
                    "dispositivo_id": alerta_obj.dispositivo_id,
                    "zona": alerta_obj.zona,
                    "consumo": alerta_obj.consumo,
                    "severidad": alerta_obj.severidad,
                    "recomendacion": alerta_obj.recomendacion,
                    "timestamp": alerta_obj.timestamp,
                    "fecha": alerta_obj.timestamp.date().isoformat()
                }

                logger.warning(f"ALERTA DETECTADA: {alerta_dict}")

                guardar_alerta(alerta_dict)
                publicar_alerta(alerta_dict)

    except Exception as e:
        logger.error(f"Error procesando evento: {e}", exc_info=True)


# =========================
# LOOP PRINCIPAL
# =========================
while True:
    try:
        eventos = redis_client.xread(
            {STREAM_NAME: ultimo_id},
            block=1000
        )

        if not eventos:
            continue

        for stream, mensajes in eventos:
            for mensaje_id, datos in mensajes:
                logger.info(f"Procesando evento: {mensaje_id}")

                procesar_evento(datos)

                ultimo_id = mensaje_id

    except Exception as e:
        logger.error(f"Error en el bucle principal: {e}", exc_info=True)