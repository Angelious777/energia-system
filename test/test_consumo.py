import unittest
from domain.entities.consumo import Consumo
from datetime import datetime

class TestConsumo(unittest.TestCase):
    def test_consumo_creation(self):
        consumo = Consumo(
            event_id="event1",
            dispositivo_id="dev1",
            zona="zona1",
            consumo=100.0,
            timestamp=datetime.now()
        )
        self.assertEqual(consumo.dispositivo_id, "dev1")
        self.assertEqual(consumo.consumo, 100.0)

if __name__ == '__main__':
    unittest.main()