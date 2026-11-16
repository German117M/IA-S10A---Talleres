"""
Pruebas Semana 16 - Motor de referencia HIS_IA.
"""

from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest


RAIZ = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(RAIZ / "src")
)


from semana15_base_conocimiento import (
    inicializar_base,
)

from semana16_motor_referencia import (
    normalizar,
    consultar,
)


class TestSemana16MotorReferencia(
    unittest.TestCase
):


    def setUp(self):

        self.temporal = (
            TemporaryDirectory()
        )

        self.ruta = (
            Path(self.temporal.name)
            / "semana16_prueba.db"
        )

        inicializar_base(
            self.ruta
        )


    def tearDown(self):

        self.temporal.cleanup()


    # ======================================================
    # 1. NORMALIZACIÓN
    # ======================================================

    def test_normaliza_tildes(self):

        resultado = normalizar(
            "RADIOLOGÍA"
        )

        self.assertIn(
            "radiologia",
            resultado
        )


    # ======================================================
    # 2. REFERENCIA VALIDADA
    # ======================================================

    def test_encuentra_referencia_validada(self):

        resultado = consultar(
            "crear orden laboratorio",
            self.ruta
        )

        self.assertEqual(
            resultado["estado"],
            "ENCONTRADA"
        )

        self.assertEqual(
            resultado["referencia"]["id"],
            "ART-001"
        )


    # ======================================================
    # 3. NO INVENTAR
    # ======================================================

    def test_no_inventa_respuesta(self):

        resultado = consultar(
            "parqueo bicicleta",
            self.ruta
        )

        self.assertEqual(
            resultado["estado"],
            "SIN_REFERENCIA"
        )

        self.assertIsNone(
            resultado["referencia"]
        )


    # ======================================================
    # 4. IGNORAR BORRADOR
    # ======================================================

    def test_ignora_articulo_borrador(self):

        resultado = consultar(
            "procedimiento contingencia",
            self.ruta
        )

        self.assertEqual(
            resultado["estado"],
            "SIN_REFERENCIA"
        )


    # ======================================================
    # 5. CONSULTA VACÍA
    # ======================================================

    def test_rechaza_consulta_vacia(self):

        resultado = consultar(
            "   ",
            self.ruta
        )

        self.assertEqual(
            resultado["estado"],
            "SIN_DATOS"
        )


if __name__ == "__main__":

    unittest.main()
