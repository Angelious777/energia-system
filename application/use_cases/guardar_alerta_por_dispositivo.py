from domain.services.alerta_por_dispositivo_service import AlertaPorDispositivoService
from domain.entities.alerta import Alerta
from infrastructure.database.cassandra.cassandra_alerta_por_dispositivo_repository import CassandraAlertaPorDispositivoRepository
from datetime import datetime
import uuid

def guardar_alerta_por_dispositivo(data: dict):
    alerta = Alerta(
        alerta_id=uuid.uuid4(),
        dispositivo_id=data["dispositivo_id"],
        zona=data["zona"],
        consumo=data["consumo"],
        severidad=data["severidad"],
        recomendacion=data.get("recomendacion", ""),
        timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.utcnow()
    )

    repository = CassandraAlertaPorDispositivoRepository()
    service = AlertaPorDispositivoService(repository)

    service.guardar_alerta_por_dispositivo(alerta)
    return {"mensaje": "Alerta guardada por dispositivo", "alerta_id": str(alerta.alerta_id)}