from domain.repositories.estadistica_zona_repository import EstadisticaZonaRepository
from domain.entities.estadistica_zona import EstadisticaZona
from infrastructure.database.cassandra.cassandra_config import session

from typing import List
from datetime import date

class CassandraEstadisticaZonaRepository(EstadisticaZonaRepository):

    def guardar(self, estadistica: EstadisticaZona) -> None:

        if session is None:
            return

        query = """
        INSERT INTO estadisticas_por_zona (
            zona,
            fecha,
            total_consumo,
            promedio
        )
        VALUES (%s, %s, %s, %s)
        """

        session.execute(query, (
            estadistica.zona,
            estadistica.fecha,
            estadistica.total_consumo,
            estadistica.promedio
        ))

    def obtener_por_zona(self, zona: str, fecha: date) -> EstadisticaZona:

        if session is None:
            return None

        query = """
        SELECT *
        FROM estadisticas_por_zona
        WHERE zona = %s
        AND fecha = %s
        """

        row = session.execute(query, (zona, fecha)).one()

        if row:
            return EstadisticaZona(
                zona=row.zona,
                fecha=row.fecha,
                total_consumo=row.total_consumo,
                promedio=row.promedio
            )

        return None

    def obtener_por_fecha(self, fecha: date) -> List[EstadisticaZona]:

        if session is None:
            return []

        query = """
        SELECT *
        FROM estadisticas_por_zona
        WHERE fecha = %s
        ALLOW FILTERING
        """

        rows = session.execute(query, (fecha,))

        estadisticas = []

        for row in rows:
            estadistica = EstadisticaZona(
                zona=row.zona,
                fecha=row.fecha,
                total_consumo=row.total_consumo,
                promedio=row.promedio
            )
            estadisticas.append(estadistica)

        return estadisticas