from datetime import date

class EstadisticaZona:

    def __init__(
        self,
        zona,
        fecha,
        total_consumo,
        promedio
    ):

        self.zona = zona
        self.fecha = fecha
        self.total_consumo = total_consumo
        self.promedio = promedio