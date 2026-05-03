from config.redis_config import redis_client
from services.cassandra_service import guardar_consumo
from services.stream_service import guardar_cache_consumo, guardar_cache_zona, publicar_alerta
from services.analisis_service import detectar_consumo_excesivo

STREAM_NAME = "consumo_stream"

ultimo_id = '0'

print("Worker escuchando eventos...")

while True:

    eventos = redis_client.xread(
        {STREAM_NAME: ultimo_id},
        block=0
    )

    for stream, mensajes in eventos:

        for mensaje_id, datos in mensajes:

            print("\nEvento recibido:")
            print(datos)

            if detectar_consumo_excesivo(datos):
                print("ALERTA: consumo excesivo")
                publicar_alerta(datos)

            guardar_consumo(datos)
            guardar_cache_consumo(datos)
            guardar_cache_zona(datos)
            ultimo_id = mensaje_id