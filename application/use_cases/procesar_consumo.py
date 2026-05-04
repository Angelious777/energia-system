from domain.services.alerta_domain_service import generar_alerta
from domain.services.anomalia_domain_service import detectar_anomalia_consecutiva

from infrastructure.database.cassandra.cassandra_consumo_repository import CassandraConsumoRepository
from infrastructure.database.cassandra.cassandra_alerta_repository import CassandraAlertaRepository

from infrastructure.database.redis.redis_cache_repository import RedisCacheRepository
from infrastructure.database.redis.redis_stream_repository import RedisStreamRepository

from domain.entities.consumo import Consumo
from domain.entities.alerta import Alerta
import datetime

consumo_repository = CassandraConsumoRepository()
alerta_repository = CassandraAlertaRepository()
cache_repository = RedisCacheRepository()
stream_repository = RedisStreamRepository()

def procesar_consumo(datos):
    consumo = Consumo(
        event_id=datos["event_id"],
        dispositivo_id=datos["dispositivo_id"],
        zona=datos["zona"],
        consumo=float(datos["consumo"]),
        timestamp=datetime.datetime.fromisoformat(datos["timestamp"])
    )
    consumo_repository.guardar(consumo)

    cache_repository.guardar_consumo(datos)

    cache_repository.guardar_zona(datos)

    consumo = float(datos["consumo"])

    hay_anomalia = (
        detectar_anomalia_consecutiva(
            datos["dispositivo_id"],
            consumo
        )
    )

    if hay_anomalia:

        alerta = generar_alerta(datos)

        if alerta:

            alerta_repository.guardar(alerta)

            stream_repository.publicar_alerta(
                alerta
            )