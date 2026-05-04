from abc import ABC, abstractmethod
from typing import List
from domain.entities.consumo import Consumo

class ConsumoRepository(ABC):
    @abstractmethod
    def guardar(self, consumo: Consumo) -> None:
        pass

    @abstractmethod
    def obtener_por_dispositivo(self, dispositivo_id: str, fecha: str) -> List[Consumo]:
        pass

    @abstractmethod
    def obtener_historial(self, dispositivo_id: str, fecha: str) -> List[Consumo]:
        pass