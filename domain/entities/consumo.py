from datetime import datetime
import uuid


class Consumo:

    def __init__(
        self,
        dispositivo_id,
        zona,
        consumo,
        timestamp=None,
        event_id=None
    ):

        self.event_id = (
            event_id
            if event_id
            else str(uuid.uuid4())
        )

        self.dispositivo_id = dispositivo_id

        self.zona = zona

        self.consumo = float(consumo)

        self.timestamp = (
            timestamp
            if timestamp
            else datetime.utcnow()
        )