from domain.repositories.alerta_repository import AlertaRepository
from domain.entities.alerta import Alerta
from infrastructure.database.cassandra.cassandra_alerta_repository import CassandraAlertaRepository
from datetime import date

class AlertaPorDispositivoService:

    def __init__(self, repository: AlertaRepository):
        self.repository = repository

    def guardar_alerta_por_dispositivo(self, alerta: Alerta) -> None:
        # También guardar en la tabla general si es necesario
        general_repo = CassandraAlertaRepository()
        general_repo.guardar(alerta)

        # Guardar en la tabla por dispositivo
        self.repository.guardar(alerta)

    def obtener_alertas_por_dispositivo(self, dispositivo_id: str, fecha: date) -> list:
        alertas = self.repository.obtener_por_dispositivo(dispositivo_id, fecha)
        return [
            {
                "alerta_id": a.alerta_id,
                "dispositivo_id": a.dispositivo_id,
                "zona": a.zona,
                "consumo": a.consumo,
                "severidad": a.severidad,
                "recomendacion": a.recomendacion,
                "timestamp": a.timestamp.isoformat()
            }
            for a in alertas
        ]