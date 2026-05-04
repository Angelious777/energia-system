from config.redis_config import redis_client
from services.cassandra_service import guardar_consumo, guardar_alerta
from services.stream_service import guardar_cache_consumo, publicar_alerta
from services.analisis_service import detectar_consumo_excesivo
from services.alerta_service import generar_alerta
from services.anomalia_service import detectar_anomalia_consecutiva
from services.cache_service import obtener_consumo_zona, guardar_cache_zona
from config.logging_config import logger

STREAM_NAME = "consumo_stream"

ultimo_id = '0'

logger.info(
    "Worker escuchando eventos..."
)

while True:

    eventos = redis_client.xread(
        {STREAM_NAME: ultimo_id},
        block=0
    )

    for stream, mensajes in eventos:

        for mensaje_id, datos in mensajes:

            try:
                print(
                    f"Procesando evento: {datos}"
                )

                consumo = float(datos["consumo"])
                
                hay_anomalia = detectar_anomalia_consecutiva(
                    datos["dispositivo_id"],
                    consumo
                )

                if hay_anomalia:

                    alerta = generar_alerta(datos)

                    print(
                        f"ALERTA DETECTADA: {alerta}"
                    )

                    guardar_alerta(alerta)
                    
                    publicar_alerta(alerta)

                guardar_consumo(datos)
                guardar_cache_consumo(datos)
                guardar_cache_zona(datos)
                ultimo_id = mensaje_id
                
            except Exception as e:
                logger.error(
                    f"Error procesando evento "
                    f"{mensaje_id}: {e}"
                )