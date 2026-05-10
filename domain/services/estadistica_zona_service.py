from domain.repositories.estadistica_zona_repository import EstadisticaZonaRepository
from domain.entities.estadistica_zona import EstadisticaZona
from infrastructure.database.cassandra.cassandra_consumo_repository import CassandraConsumoRepository
from infrastructure.database.redis.redis_config import redis_client
from datetime import date
import json

class EstadisticaZonaService:

    def __init__(self, repository: EstadisticaZonaRepository):
        self.repository = repository

    def calcular_y_guardar_estadistica_zona(self, zona: str, fecha: date) -> None:
        consumo_repo = CassandraConsumoRepository()
        consumos = consumo_repo.obtener_por_fecha(fecha)

        consumos_zona = [c for c in consumos if c.zona == zona]

        if not consumos_zona:
            return

        total_consumo = sum(c.consumo for c in consumos_zona)
        promedio = total_consumo / len(consumos_zona)

        estadistica = EstadisticaZona(
            zona=zona,
            fecha=fecha,
            total_consumo=round(total_consumo, 2),
            promedio=round(promedio, 2)
        )

        self.repository.guardar(estadistica)

        # Cache en Redis
        clave = f"estadistica_zona:{zona}:{fecha.isoformat()}"
        redis_client.setex(clave, 3600, json.dumps({
            "zona": zona,
            "total_consumo": estadistica.total_consumo,
            "promedio": estadistica.promedio
        }))

    def obtener_estadistica_zona(self, zona: str, fecha: date) -> dict:
        # Intentar obtener de Redis primero
        clave = f"estadistica_zona:{zona}:{fecha.isoformat()}"
        cached = redis_client.get(clave)
        if cached:
            return json.loads(cached)

        # Si no está en cache, obtener de Cassandra
        estadistica = self.repository.obtener_por_zona(zona, fecha)
        if estadistica:
            data = {
                "zona": estadistica.zona,
                "total_consumo": estadistica.total_consumo,
                "promedio": estadistica.promedio
            }
            # Cachear por 1 hora
            redis_client.setex(clave, 3600, json.dumps(data))
            return data

        return None

    def obtener_estadisticas_por_fecha(self, fecha: date) -> list:
        estadisticas = self.repository.obtener_por_fecha(fecha)
        return [
            {
                "zona": e.zona,
                "total_consumo": e.total_consumo,
                "promedio": e.promedio
            }
            for e in estadisticas
        ]