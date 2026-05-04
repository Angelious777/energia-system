class Consumo:

    def __init__(
        self,
        event_id,
        dispositivo_id,
        zona,
        consumo,
        timestamp
    ):

        self.event_id = event_id

        self.dispositivo_id = dispositivo_id

        self.zona = zona

        self.consumo = consumo

        self.timestamp = timestamp