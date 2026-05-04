import unittest
from domain.entities.alerta import Alerta
from domain.value_objects.severidad import Severidad
from datetime import datetime

class TestAlerta(unittest.TestCase):
    def test_alerta_creation(self):
        alerta = Alerta(
            alerta_id="123",
            dispositivo_id="dev1",
            zona="zona1",
            consumo=150.0,
            severidad=Severidad.CRITICA,
            recomendacion="Apagar dispositivo",
            timestamp=datetime.now()
        )
        self.assertEqual(alerta.dispositivo_id, "dev1")
        self.assertEqual(alerta.severidad, Severidad.CRITICA)

if __name__ == '__main__':
    unittest.main()