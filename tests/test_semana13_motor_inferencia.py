import sys
import unittest
from pathlib import Path


# ==========================================================
# PERMITIR IMPORTAR DESDE /src
# ==========================================================

RAIZ_PROYECTO = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(RAIZ_PROYECTO / "src")
)


from semana13_motor_inferencia import (
    Regla,
    inferir,
    analizar_caso_his,
    generar_interpretacion,
)


# ==========================================================
# PRUEBAS SEMANA 13 - HIS_IA
# ==========================================================

class TestSemana13MotorInferencia(unittest.TestCase):


    # ------------------------------------------------------
    # PRUEBA 1
    # Caso prioritario completo
    # ------------------------------------------------------

    def test_caso_prioritario_con_pendientes(self):

        resultado = analizar_caso_his(
            prioridad="Prioritaria",
            documentos_pendientes=1,
            resultados_pendientes=3,
            imagenes_pendientes=2,
            revision_recomendada=True,
        )


        self.assertIn(
            "requiere_seguimiento",
            resultado["hechos_derivados"]
        )


        self.assertIn(
            "validar_resultados_diagnosticos",
            resultado["hechos_derivados"]
        )


        self.assertIn(
            "revision_manual_prioritaria",
            resultado["hechos_derivados"]
        )


        self.assertIn(
            "completar_documentacion",
            resultado["hechos_derivados"]
        )


    # ------------------------------------------------------
    # PRUEBA 2
    # Caso normal sin pendientes
    # ------------------------------------------------------

    def test_caso_normal_sin_pendientes(self):

        resultado = analizar_caso_his(
            prioridad="Normal",
            documentos_pendientes=0,
            resultados_pendientes=0,
            imagenes_pendientes=0,
            revision_recomendada=False,
        )


        self.assertIn(
            "caso_listo_para_cierre",
            resultado["hechos_derivados"]
        )


        self.assertNotIn(
            "revision_manual_prioritaria",
            resultado["hechos_derivados"]
        )


        interpretacion = generar_interpretacion(
            resultado=resultado,
            documentos_pendientes=0,
            resultados_pendientes=0,
            imagenes_pendientes=0,
        )


        self.assertEqual(
            interpretacion["estado"],
            "Caso completo y listo para cierre"
        )


    # ------------------------------------------------------
    # PRUEBA 3
    # Los hechos originales no deben modificarse
    # ------------------------------------------------------

    def test_hechos_iniciales_no_se_modifican(self):

        hechos_originales = {
            "prioridad_alta",
            "resultados_pendientes",
        }


        copia_original = hechos_originales.copy()


        inferir(
            hechos_originales
        )


        self.assertEqual(
            hechos_originales,
            copia_original
        )


    # ------------------------------------------------------
    # PRUEBA 4
    # Regla circular
    # ------------------------------------------------------

    def test_reglas_circulares_no_generan_bucle(self):

        reglas_circulares = [

            Regla(
                nombre="RC1",
                premisas=frozenset({
                    "hecho_a"
                }),
                conclusion="hecho_b",
                descripcion=(
                    "A permite derivar B."
                ),
            ),

            Regla(
                nombre="RC2",
                premisas=frozenset({
                    "hecho_b"
                }),
                conclusion="hecho_a",
                descripcion=(
                    "B permite derivar A."
                ),
            ),
        ]


        hechos_finales, trazas = inferir(
            {"hecho_a"},
            reglas_circulares
        )


        self.assertEqual(
            hechos_finales,
            {
                "hecho_a",
                "hecho_b"
            }
        )


        self.assertEqual(
            len(trazas),
            1
        )


    # ------------------------------------------------------
    # PRUEBA 5
    # No debe inventar una conclusión
    # ------------------------------------------------------

    def test_sin_premisas_suficientes(self):

        hechos_finales, trazas = inferir(
            {
                "prioridad_alta"
            }
        )


        self.assertNotIn(
            "requiere_seguimiento",
            hechos_finales
        )


        self.assertNotIn(
            "revision_manual_prioritaria",
            hechos_finales
        )


        self.assertEqual(
            len(trazas),
            0
        )


if __name__ == "__main__":

    unittest.main()
