from domain.repositories.consumo_repository import ConsumoRepository

from domain.entities.consumo import Consumo

from infrastructure.database.cassandra.cassandra_config import session

from typing import List


class CassandraConsumoRepository(
    ConsumoRepository
):

    # =====================================
    # GUARDAR
    # =====================================

    def guardar(
        self,
        consumo: Consumo
    ) -> None:

        query = """
        INSERT INTO consumo_por_dispositivo (
            dispositivo_id,
            fecha,
            timestamp,
            consumo,
            zona
        )
        VALUES (%s, %s, %s, %s, %s)
        """

        fecha = consumo.timestamp.date()

        session.execute(query, (

            consumo.dispositivo_id,

            fecha,

            consumo.timestamp,

            consumo.consumo,

            consumo.zona
        ))

    # =====================================
    # OBTENER POR DISPOSITIVO
    # =====================================

    def obtener_por_dispositivo(
        self,
        dispositivo_id: str,
        fecha
    ) -> List[Consumo]:

        query = """
        SELECT *
        FROM consumo_por_dispositivo
        WHERE dispositivo_id = %s
        AND fecha = %s
        """

        rows = session.execute(
            query,
            (dispositivo_id, fecha)
        )

        consumos = []

        for row in rows:

            consumo = Consumo(

                dispositivo_id=row.dispositivo_id,

                zona=row.zona,

                consumo=row.consumo,

                timestamp=row.timestamp
            )

            consumos.append(consumo)

        return consumos

    # =====================================
    # HISTORIAL
    # =====================================

    def obtener_historial(
        self,
        dispositivo_id: str,
        fecha
    ) -> List[Consumo]:

        return self.obtener_por_dispositivo(
            dispositivo_id,
            fecha
        )