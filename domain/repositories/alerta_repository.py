from abc import ABC, abstractmethod
from typing import List
from domain.entities.alerta import Alerta

class AlertaRepository(ABC):
    @abstractmethod
    def guardar(self, alerta: Alerta) -> None:
        pass

    @abstractmethod
    def obtener_por_fecha(self, fecha: str) -> List[Alerta]:
        pass

    @abstractmethod
    def obtener_por_dispositivo(self, dispositivo_id: str, fecha: str) -> List[Alerta]:
        pass

    @abstractmethod
    def obtener_recientes(self) -> List[Alerta]:
        pass