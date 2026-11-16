"""
Pruebas Semana 15 - Base de conocimiento HIS_IA.
"""

from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3
import sys
import unittest

RAIZ = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(RAIZ / "src")
)

from semana15_base_conocimiento import (
    inicializar_base,
    buscar_articulos,
    registrar_articulo,
    validar_articulo,
)


class TestSemana15BaseConocimiento(unittest.TestCase):

    def setUp(self):
        self.temporal = TemporaryDirectory()
        self.ruta = (
            Path(self.temporal.name)
            / "semana15_prueba.db"
        )

        inicializar_base(self.ruta)

    def tearDown(self):
        self.temporal.cleanup()

    def test_solo_articulos_validados(self):
        laboratorio = buscar_articulos(
            "Laboratorio",
            self.ruta
        )

        radiologia = buscar_articulos(
            "Radiología",
            self.ruta
        )

        self.assertEqual(
            len(laboratorio),
            2
        )

        titulos = [
            articulo["titulo"]
            for articulo in radiologia
        ]

        self.assertIn(
            "Flujo de imagenes RIS hacia PACS",
            titulos
        )

        self.assertNotIn(
            "Procedimiento de contingencia RIS",
            titulos
        )

    def test_ciclo_registro_validacion(self):
        articulo_id = registrar_articulo(
            titulo="Guia de validacion LIS",
            contenido="Procedimiento de prueba.",
            dominio_id=2,
            experto_id=2,
            fuente="Fuente ficticia",
            aplicacion_id=2,
            herramienta_id=1,
            ruta=self.ruta
        )

        antes = buscar_articulos(
            "Laboratorio",
            self.ruta
        )

        titulos_antes = [
            articulo["titulo"]
            for articulo in antes
        ]

        self.assertNotIn(
            "Guia de validacion LIS",
            titulos_antes
        )

        validar_articulo(
            articulo_id,
            self.ruta
        )

        despues = buscar_articulos(
            "Laboratorio",
            self.ruta
        )

        titulos_despues = [
            articulo["titulo"]
            for articulo in despues
        ]

        self.assertIn(
            "Guia de validacion LIS",
            titulos_despues
        )

    def test_campos_obligatorios(self):
        with self.assertRaises(ValueError):
            registrar_articulo(
                titulo="",
                contenido="Contenido",
                dominio_id=2,
                experto_id=2,
                fuente="Fuente",
                ruta=self.ruta
            )

    def test_dominio_inexistente(self):
        with self.assertRaises(
            sqlite3.IntegrityError
        ):
            registrar_articulo(
                titulo="Articulo invalido",
                contenido="Contenido",
                dominio_id=999,
                experto_id=2,
                fuente="Fuente",
                ruta=self.ruta
            )

    def test_articulo_inexistente(self):
        with self.assertRaises(ValueError):
            validar_articulo(
                9999,
                self.ruta
            )


if __name__ == "__main__":
    unittest.main()
