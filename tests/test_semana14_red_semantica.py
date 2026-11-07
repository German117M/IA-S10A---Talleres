import sys
import unittest
from pathlib import Path


RAIZ_PROYECTO = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(RAIZ_PROYECTO / "src")
)


from semana14_red_semantica import (
    RedSemantica,
    crear_red_his_ia,
    buscar_camino,
    consultar_propiedad_heredada,
    interpretar_oracion,
    agregar_oracion,
)


class TestSemana14RedSemantica(unittest.TestCase):


    def setUp(self):

        self.red = crear_red_his_ia()


    # ======================================================
    # PRUEBA 1
    # RELACIÓN DIRECTA
    # ======================================================

    def test_relacion_directa(self):

        resultado = self.red.consultar(
            "orden_laboratorio",
            "se_envia_a"
        )

        self.assertEqual(
            resultado,
            ["lis"]
        )


    # ======================================================
    # PRUEBA 2
    # INFERENCIA JERÁRQUICA
    # ======================================================

    def test_es_un(self):

        self.assertTrue(
            self.red.es_un(
                "orden_laboratorio",
                "orden_diagnostica"
            )
        )

        self.assertTrue(
            self.red.es_un(
                "orden_radiologia",
                "orden_diagnostica"
            )
        )


    # ======================================================
    # PRUEBA 3
    # HERENCIA DE PROPIEDADES
    # ======================================================

    def test_propiedad_heredada(self):

        resultado = consultar_propiedad_heredada(
            self.red,
            "orden_laboratorio",
            "se_registra_en"
        )

        self.assertEqual(
            resultado,
            ["his"]
        )


    # ======================================================
    # PRUEBA 4
    # BÚSQUEDA DE CAMINO
    # ======================================================

    def test_buscar_camino(self):

        camino = buscar_camino(
            self.red,
            "orden_laboratorio",
            "his"
        )

        self.assertTrue(
            len(camino) > 0
        )

        self.assertEqual(
            camino[-1]["hasta"],
            "his"
        )


    # ======================================================
    # PRUEBA 5
    # ORACIÓN A TRIPLE
    # ======================================================

    def test_interpretar_oracion(self):

        triple = interpretar_oracion(
            "La orden de laboratorio se envía al LIS"
        )

        self.assertEqual(
            triple,
            (
                "orden_laboratorio",
                "se_envia_a",
                "lis"
            )
        )


    # ======================================================
    # PRUEBA 6
    # ORACIÓN INVÁLIDA
    # ======================================================

    def test_oracion_invalida(self):

        with self.assertRaises(
            ValueError
        ):

            interpretar_oracion(
                "El paciente toma café"
            )


    # ======================================================
    # PRUEBA 7
    # EVITAR CICLOS
    # ======================================================

    def test_ciclo_jerarquico(self):

        red = RedSemantica()

        red.agregar(
            "a",
            "es_un",
            "b"
        )

        red.agregar(
            "b",
            "es_un",
            "a"
        )

        resultado = red.es_un(
            "a",
            "b"
        )

        self.assertTrue(
            resultado
        )


    # ======================================================
    # PRUEBA 8
    # AGREGAR ORACIÓN A LA RED
    # ======================================================

    def test_agregar_oracion(self):

        red = RedSemantica()

        resultado = agregar_oracion(
            red,
            "RIS genera imagen"
        )

        self.assertEqual(
            resultado["triple"],
            (
                "ris",
                "genera",
                "imagen"
            )
        )

        self.assertEqual(
            red.consultar(
                "ris",
                "genera"
            ),
            ["imagen"]
        )


if __name__ == "__main__":

    unittest.main()
