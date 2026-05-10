from domain.repositories.alerta_repository import AlertaRepository
from domain.entities.alerta import Alerta
from infrastructure.database.cassandra.cassandra_config import session
from typing import List
from datetime import datetime

class CassandraAlertaRepository(AlertaRepository):
    def guardar(self, alerta: Alerta) -> None:
        if session is None:
            return

        query = """
        INSERT INTO alertas (alerta_id, dispositivo_id, zona, consumo, severidad, recomendacion, timestamp, fecha)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        fecha = alerta.timestamp.date().isoformat()
        session.execute(query, (str(alerta.alerta_id), alerta.dispositivo_id, alerta.zona, alerta.consumo, alerta.severidad, alerta.recomendacion, alerta.timestamp, fecha))

    def obtener_por_fecha(self, fecha: str) -> List[Alerta]:
        if session is None:
            return []

        query = "SELECT * FROM alertas WHERE fecha = %s ALLOW FILTERING"
        rows = session.execute(query, (fecha,))
        alertas = []
        for row in rows:
            alerta = Alerta(
                alerta_id=row.alerta_id,
                dispositivo_id=row.dispositivo_id,
                zona=row.zona,
                consumo=row.consumo,
                severidad=row.severidad,
                recomendacion=row.recomendacion,
                timestamp=row.timestamp
            )
            alertas.append(alerta)
        return alertas

    def obtener_por_dispositivo(self, dispositivo_id: str, fecha: str) -> List[Alerta]:
        if session is None:
            return []

        query = "SELECT * FROM alertas WHERE dispositivo_id = %s AND fecha = %s ALLOW FILTERING"
        rows = session.execute(query, (dispositivo_id, fecha))
        alertas = []
        for row in rows:
            alerta = Alerta(
                alerta_id=row.alerta_id,
                dispositivo_id=row.dispositivo_id,
                zona=row.zona,
                consumo=row.consumo,
                severidad=row.severidad,
                recomendacion=row.recomendacion,
                timestamp=row.timestamp
            )
            alertas.append(alerta)
        return alertas

    def obtener_recientes(self) -> List[Alerta]:
        if session is None:
            return []

        # Obtener las últimas 10 alertas ordenadas por timestamp
        query = "SELECT * FROM alertas LIMIT 10 ALLOW FILTERING"
        rows = session.execute(query)
        alertas = []
        for row in rows:
            alerta = Alerta(
                alerta_id=row.alerta_id,
                dispositivo_id=row.dispositivo_id,
                zona=row.zona,
                consumo=row.consumo,
                severidad=row.severidad,
                recomendacion=row.recomendacion,
                timestamp=row.timestamp
            )
            alertas.append(alerta)
        return sorted(alertas, key=lambda x: x.timestamp, reverse=True)