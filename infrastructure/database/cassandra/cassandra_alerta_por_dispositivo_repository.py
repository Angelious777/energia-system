from domain.repositories.alerta_repository import AlertaRepository
from domain.entities.alerta import Alerta
from infrastructure.database.cassandra.cassandra_config import session

from typing import List
from datetime import date

class CassandraAlertaPorDispositivoRepository(AlertaRepository):

    def guardar(self, alerta: Alerta) -> None:

        if session is None:
            return

        query = """
        INSERT INTO alertas_por_dispositivo (
            dispositivo_id,
            fecha,
            timestamp,
            alerta_id,
            zona,
            consumo,
            severidad,
            recomendacion
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        fecha = alerta.timestamp.date()

        session.execute(query, (
            alerta.dispositivo_id,
            fecha,
            alerta.timestamp,
            alerta.alerta_id,
            alerta.zona,
            alerta.consumo,
            alerta.severidad,
            alerta.recomendacion
        ))

    def obtener_por_fecha(self, fecha: str) -> List[Alerta]:

        if session is None:
            return []

        query = """
        SELECT *
        FROM alertas_por_dispositivo
        WHERE fecha = %s
        ALLOW FILTERING
        """

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

    def obtener_por_dispositivo(self, dispositivo_id: str, fecha: date) -> List[Alerta]:

        if session is None:
            return []

        query = """
        SELECT *
        FROM alertas_por_dispositivo
        WHERE dispositivo_id = %s
        AND fecha = %s
        """

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

        query = """
        SELECT *
        FROM alertas_por_dispositivo
        LIMIT 10
        ALLOW FILTERING
        """

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
