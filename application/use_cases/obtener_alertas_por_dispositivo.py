from domain.services.alerta_por_dispositivo_service import AlertaPorDispositivoService
from infrastructure.database.cassandra.cassandra_alerta_por_dispositivo_repository import CassandraAlertaPorDispositivoRepository
from datetime import date

def obtener_alertas_por_dispositivo(dispositivo_id: str, fecha_str: str):
    try:
        fecha = date.fromisoformat(fecha_str)
    except ValueError:
        raise ValueError("Formato de fecha inválido")

    repository = CassandraAlertaPorDispositivoRepository()
    service = AlertaPorDispositivoService(repository)

    return service.obtener_alertas_por_dispositivo(dispositivo_id, fecha)