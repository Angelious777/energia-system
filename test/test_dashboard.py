import unittest
from application.use_cases.obtener_dashboard import obtener_dashboard
# Asumir que obtener_dashboard existe y retorna algo

class TestDashboard(unittest.TestCase):
    def test_obtener_dashboard(self):
        # Mock or actual test
        resultado = obtener_dashboard()
        self.assertIsInstance(resultado, dict)

if __name__ == '__main__':
    unittest.main()