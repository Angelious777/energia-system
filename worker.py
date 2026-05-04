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

ultimo_id = '$'

logger.info("Worker escuchando eventos...")

while True:
    try:
        eventos = redis_client.xread({STREAM_NAME: ultimo_id}, block=1000)
        if not eventos:
            continue
        for stream, mensajes in eventos:
            for mensaje_id, datos in mensajes:
                try:
                    print(f"Procesando evento: {datos}")
                    
                    # Guardar consumo en ambas tablas de Cassandra
                    guardar_consumo(datos)
                    guardar_consumo_zona(datos)
                    guardar_cache_consumo(datos)
                    guardar_cache_zona(datos)
                    
                    # Detectar anomalías y generar alertas
                    hay_anomalia = detectar_anomalia_consecutiva(datos["dispositivo_id"], float(datos["consumo"]))
                    if hay_anomalia:
                        alerta_obj = generar_alerta(datos)
                        if alerta_obj:
                            # Convertir objeto Alerta a diccionario
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
                            print(f"ALERTA DETECTADA: {alerta_dict}")
                            guardar_alerta(alerta_dict)
                            publicar_alerta(alerta_dict)
                    
                    ultimo_id = mensaje_id
                    logger.info(f"Evento procesado: {mensaje_id}")
                    
                except Exception as e:
                    logger.error(f"Error procesando evento {mensaje_id}: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Error en el bucle de lectura: {e}", exc_info=True)
        continue