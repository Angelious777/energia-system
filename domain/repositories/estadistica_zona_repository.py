from abc import ABC, abstractmethod
from typing import List
from datetime import date
from domain.entities.estadistica_zona import EstadisticaZona

class EstadisticaZonaRepository(ABC):

    @abstractmethod
    def guardar(self, estadistica: EstadisticaZona) -> None:
        pass

    @abstractmethod
    def obtener_por_zona(self, zona: str, fecha: date) -> EstadisticaZona:
        pass

    @abstractmethod
    def obtener_por_fecha(self, fecha: date) -> List[EstadisticaZona]:
        pass