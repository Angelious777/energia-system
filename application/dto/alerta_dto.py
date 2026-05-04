class AlertaDTO:

    def __init__(
        self,
        alerta_id,
        dispositivo_id,
        zona,
        consumo,
        severidad,
        recomendacion,
        timestamp
    ):

        self.alerta_id = alerta_id

        self.dispositivo_id = dispositivo_id

        self.zona = zona

        self.consumo = consumo

        self.severidad = severidad

        self.recomendacion = recomendacion

        self.timestamp = timestamp