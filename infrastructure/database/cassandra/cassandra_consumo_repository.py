from domain.repositories.consumo_repository import ConsumoRepository
from domain.entities.consumo import Consumo
from infrastructure.database.cassandra.cassandra_config import session
from typing import List
from datetime import datetime

class CassandraConsumoRepository(ConsumoRepository):
    def guardar(self, consumo: Consumo) -> None:
        query = """
        INSERT INTO consumos (
            dispositivo_id,
            timestamp,
            zona,
            consumo,
            event_id,
            fecha
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        fecha = consumo.timestamp.date().isoformat()
        session.execute(query, (
            consumo.dispositivo_id,
            consumo.timestamp,
            consumo.zona,
            consumo.consumo,
            consumo.event_id,
            fecha
        ))

    def obtener_por_dispositivo(self, dispositivo_id: str, fecha: str) -> List[Consumo]:
        query = "SELECT * FROM consumos WHERE dispositivo_id = %s AND fecha = %s ALLOW FILTERING"
        rows = session.execute(query, (dispositivo_id, fecha))
        consumos = []
        for row in rows:
            consumo = Consumo(
                event_id=row.event_id,
                dispositivo_id=row.dispositivo_id,
                zona=row.zona,
                consumo=row.consumo,
                timestamp=row.timestamp
            )
            consumos.append(consumo)
        return consumos

    def obtener_historial(self, dispositivo_id: str, fecha: str) -> List[Consumo]:
        return self.obtener_por_dispositivo(dispositivo_id, fecha)