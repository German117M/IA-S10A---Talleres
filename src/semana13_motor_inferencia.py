from dataclasses import dataclass
from typing import Iterable


# ==========================================================
# SEMANA 13
# INGENIERÍA DEL CONOCIMIENTO - HIS_IA
# ==========================================================


@dataclass(frozen=True)
class Regla:
    nombre: str
    premisas: frozenset[str]
    conclusion: str
    descripcion: str


# ==========================================================
# BASE DE REGLAS
# ==========================================================

REGLAS_HIS = [

    Regla(
        nombre="R1",
        premisas=frozenset({
            "prioridad_alta",
            "resultados_pendientes",
        }),
        conclusion="requiere_seguimiento",
        descripcion=(
            "Un caso prioritario con resultados pendientes "
            "requiere seguimiento."
        ),
    ),

    Regla(
        nombre="R2",
        premisas=frozenset({
            "requiere_seguimiento",
            "imagenes_pendientes",
        }),
        conclusion="validar_resultados_diagnosticos",
        descripcion=(
            "Si el caso requiere seguimiento y tiene "
            "imágenes pendientes, deben revisarse los "
            "resultados diagnósticos."
        ),
    ),

    Regla(
        nombre="R3",
        premisas=frozenset({
            "prioridad_alta",
            "revision_recomendada",
        }),
        conclusion="revision_manual_prioritaria",
        descripcion=(
            "Un caso prioritario con discrepancias "
            "requiere revisión manual."
        ),
    ),

    Regla(
        nombre="R4",
        premisas=frozenset({
            "prioridad_alta",
            "documentos_pendientes",
        }),
        conclusion="completar_documentacion",
        descripcion=(
            "Un caso prioritario con documentos pendientes "
            "debe completar su documentación."
        ),
    ),

    Regla(
        nombre="R5",
        premisas=frozenset({
            "documentos_completos",
            "resultados_completos",
            "imagenes_completas",
        }),
        conclusion="caso_listo_para_cierre",
        descripcion=(
            "Un caso sin pendientes puede marcarse "
            "como listo para cierre."
        ),
    ),
]


# ==========================================================
# MOTOR DE INFERENCIA
# ENCADENAMIENTO HACIA ADELANTE
# ==========================================================

def inferir(
    hechos_iniciales: Iterable[str],
    reglas: Iterable[Regla] = REGLAS_HIS,
):

    hechos = set(
        hechos_iniciales
    )

    trazas = []

    cambios = True


    while cambios:

        cambios = False


        for regla in reglas:

            if (
                regla.premisas.issubset(hechos)
                and
                regla.conclusion not in hechos
            ):

                hechos.add(
                    regla.conclusion
                )

                trazas.append(
                    {
                        "regla": regla.nombre,
                        "premisas": sorted(regla.premisas),
                        "conclusion": regla.conclusion,
                        "descripcion": regla.descripcion,
                    }
                )

                cambios = True


    return hechos, trazas


# ==========================================================
# CONSTRUIR HECHOS DESDE UN CASO HIS
# ==========================================================

def construir_hechos_caso(
    prioridad,
    documentos_pendientes,
    resultados_pendientes,
    imagenes_pendientes,
    revision_recomendada=False,
):

    hechos = set()


    # Prioridad
    if str(prioridad).strip().lower() == "prioritaria":

        hechos.add(
            "prioridad_alta"
        )

    else:

        hechos.add(
            "prioridad_normal"
        )


    # Documentos
    if int(documentos_pendientes) > 0:

        hechos.add(
            "documentos_pendientes"
        )

    else:

        hechos.add(
            "documentos_completos"
        )


    # Resultados
    if int(resultados_pendientes) > 0:

        hechos.add(
            "resultados_pendientes"
        )

    else:

        hechos.add(
            "resultados_completos"
        )


    # Imágenes
    if int(imagenes_pendientes) > 0:

        hechos.add(
            "imagenes_pendientes"
        )

    else:

        hechos.add(
            "imagenes_completas"
        )


    # Revisión sugerida por Semana 11
    if revision_recomendada:

        hechos.add(
            "revision_recomendada"
        )


    return hechos


# ==========================================================
# ANALIZAR CASO COMPLETO
# ==========================================================

def analizar_caso_his(
    prioridad,
    documentos_pendientes,
    resultados_pendientes,
    imagenes_pendientes,
    revision_recomendada=False,
):

    hechos_iniciales = construir_hechos_caso(
        prioridad=prioridad,
        documentos_pendientes=documentos_pendientes,
        resultados_pendientes=resultados_pendientes,
        imagenes_pendientes=imagenes_pendientes,
        revision_recomendada=revision_recomendada,
    )


    hechos_finales, trazas = inferir(
        hechos_iniciales
    )


    hechos_derivados = sorted(
        hechos_finales - hechos_iniciales
    )


    acciones = [
        hecho
        for hecho in hechos_derivados
        if hecho in {
            "requiere_seguimiento",
            "validar_resultados_diagnosticos",
            "revision_manual_prioritaria",
            "completar_documentacion",
            "caso_listo_para_cierre",
        }
    ]


    return {
        "hechos_iniciales": sorted(hechos_iniciales),
        "hechos_derivados": hechos_derivados,
        "acciones": acciones,
        "trazas": trazas,
        "total_reglas_activadas": len(trazas),
    }


# ==========================================================
# INTERPRETACIÓN HUMANA DEL RESULTADO
# ==========================================================

def generar_interpretacion(
    resultado,
    documentos_pendientes,
    resultados_pendientes,
    imagenes_pendientes,
):

    hechos = set(
        resultado["hechos_iniciales"]
    )

    derivados = set(
        resultado["hechos_derivados"]
    )


    # ------------------------------------------------------
    # HALLAZGOS
    # ------------------------------------------------------

    hallazgos = []


    if documentos_pendientes > 0:

        hallazgos.append(
            f"Se identificaron {documentos_pendientes} "
            "documento(s) pendiente(s)."
        )


    if resultados_pendientes > 0:

        hallazgos.append(
            f"Se identificaron {resultados_pendientes} "
            "resultado(s) pendiente(s)."
        )


    if imagenes_pendientes > 0:

        hallazgos.append(
            f"Se identificaron {imagenes_pendientes} "
            "imagen(es) pendiente(s)."
        )


    if "revision_recomendada" in hechos:

        hallazgos.append(
            "Existe una discrepancia entre los métodos "
            "de inteligencia artificial utilizados en "
            "la evaluación del caso."
        )


    if not hallazgos:

        hallazgos.append(
            "No se identificaron pendientes en el caso."
        )


    # ------------------------------------------------------
    # ESTADO DEL CASO
    # ------------------------------------------------------

    if "revision_manual_prioritaria" in derivados:

        estado = (
            "Caso prioritario que requiere revisión manual"
        )

    elif "validar_resultados_diagnosticos" in derivados:

        estado = (
            "Caso prioritario con información diagnóstica pendiente"
        )

    elif "completar_documentacion" in derivados:

        estado = (
            "Caso prioritario con documentación pendiente"
        )

    elif "caso_listo_para_cierre" in derivados:

        estado = (
            "Caso completo y listo para cierre"
        )

    elif "requiere_seguimiento" in derivados:

        estado = (
            "Caso que requiere seguimiento"
        )

    else:

        estado = (
            "Caso sin acciones adicionales derivadas"
        )


    # ------------------------------------------------------
    # INTERPRETACIÓN
    # ------------------------------------------------------

    if "revision_manual_prioritaria" in derivados:

        interpretacion = (
            "El caso fue clasificado como prioritario y "
            "además existe una discrepancia entre los métodos "
            "de inteligencia artificial. Por esta razón se "
            "recomienda que una persona revise el caso antes "
            "de tomar una decisión definitiva."
        )

    elif "validar_resultados_diagnosticos" in derivados:

        interpretacion = (
            "El caso requiere seguimiento debido a que "
            "presenta información pendiente relacionada "
            "con resultados e imágenes."
        )

    elif "caso_listo_para_cierre" in derivados:

        interpretacion = (
            "El caso no presenta documentos, resultados "
            "ni imágenes pendientes y puede continuar "
            "con su proceso de cierre."
        )

    else:

        interpretacion = (
            "Las reglas actuales no identificaron una "
            "condición que requiera una intervención "
            "prioritaria adicional."
        )


    # ------------------------------------------------------
    # ACCIONES RECOMENDADAS
    # ------------------------------------------------------

    acciones = []


    if "completar_documentacion" in derivados:

        acciones.append(
            "Completar la documentación pendiente."
        )


    if "requiere_seguimiento" in derivados:

        acciones.append(
            "Realizar seguimiento al caso."
        )


    if "validar_resultados_diagnosticos" in derivados:

        acciones.append(
            "Validar los resultados diagnósticos "
            "y las imágenes pendientes."
        )


    if "revision_manual_prioritaria" in derivados:

        acciones.append(
            "Realizar una revisión manual prioritaria."
        )


    if "caso_listo_para_cierre" in derivados:

        acciones.append(
            "Continuar con el cierre del caso."
        )


    if not acciones:

        acciones.append(
            "Continuar con el flujo normal del caso."
        )


    return {
        "estado": estado,
        "hallazgos": hallazgos,
        "interpretacion": interpretacion,
        "acciones_recomendadas": acciones,
    }



# ==========================================================
# PRUEBA DIRECTA
# ==========================================================

def main():

    documentos_pendientes = 1
    resultados_pendientes = 3
    imagenes_pendientes = 2

    resultado = analizar_caso_his(
        prioridad="Prioritaria",
        documentos_pendientes=documentos_pendientes,
        resultados_pendientes=resultados_pendientes,
        imagenes_pendientes=imagenes_pendientes,
        revision_recomendada=True,
    )


    interpretacion = generar_interpretacion(
        resultado=resultado,
        documentos_pendientes=documentos_pendientes,
        resultados_pendientes=resultados_pendientes,
        imagenes_pendientes=imagenes_pendientes,
    )


    print()
    print("=" * 70)
    print("SEMANA 13 - INGENIERÍA DEL CONOCIMIENTO - HIS_IA")
    print("=" * 70)


    print("\nESTADO DEL CASO")
    print(
        interpretacion["estado"]
    )


    print("\nHALLAZGOS")

    for hallazgo in interpretacion["hallazgos"]:

        print(
            "-",
            hallazgo
        )


    print("\nINTERPRETACIÓN")
    print(
        interpretacion["interpretacion"]
    )


    print("\nACCIONES RECOMENDADAS")

    for accion in interpretacion["acciones_recomendadas"]:

        print(
            "-",
            accion
        )


    print("\nREGLAS ACTIVADAS")

    for traza in resultado["trazas"]:

        print(
            f"{traza['regla']} -> "
            f"{traza['conclusion']}"
        )


    print("\nEXPLICACIÓN DE LA INFERENCIA")

    for traza in resultado["trazas"]:

        print(
            f"{traza['regla']}: "
            f"{traza['descripcion']}"
        )


    print()
    print("=" * 70)


if __name__ == "__main__":

    main()


# ==========================================================
# INTEGRACIÓN SEMANAS 7 + 11 + 13
# ==========================================================

def analizar_caso_integrado(
    resultado_semana7,
    resultado_semana11,
    documentos_pendientes,
    resultados_pendientes,
    imagenes_pendientes,
):
    """
    Integra los resultados de Semana 7 y Semana 11
    con el motor de conocimiento de Semana 13.

    Semana 7:
        aporta hallazgos de temperatura,
        frecuencia cardíaca y presión.

    Semana 11:
        aporta prioridad y nivel de acuerdo.

    Semana 13:
        aplica reglas, interpreta y recomienda acciones.
    """

    # ======================================================
    # NORMALIZAR RESPUESTA DE SEMANA 11
    # ======================================================

    if (
        isinstance(resultado_semana11, dict)
        and
        "resultado" in resultado_semana11
        and
        isinstance(resultado_semana11["resultado"], dict)
    ):
        semana11 = resultado_semana11["resultado"]

    else:
        semana11 = resultado_semana11


    prioridad = (
        semana11.get("resultado")
        or
        semana11.get("resultado_sugerido")
        or
        semana11.get("prioridad")
        or
        semana11.get("analisis_principal")
        or
        "Normal"
    )


    revision_recomendada = bool(
        semana11.get(
            "revision_recomendada",
            False
        )
    )


    # ======================================================
    # ANALIZAR MEDIANTE SEMANA 13
    # ======================================================

    resultado_semana13 = analizar_caso_his(
        prioridad=prioridad,
        documentos_pendientes=documentos_pendientes,
        resultados_pendientes=resultados_pendientes,
        imagenes_pendientes=imagenes_pendientes,
        revision_recomendada=revision_recomendada,
    )


    interpretacion = generar_interpretacion(
        resultado=resultado_semana13,
        documentos_pendientes=documentos_pendientes,
        resultados_pendientes=resultados_pendientes,
        imagenes_pendientes=imagenes_pendientes,
    )


    # ======================================================
    # HALLAZGOS DE SEMANA 7
    # ======================================================

    hallazgos_clinicos = []


    if isinstance(
        resultado_semana7,
        dict
    ):

        resultado_integrado = (
            resultado_semana7.get(
                "resultado_integrado",
                {}
            )
        )


        hallazgos_clinicos = list(
            resultado_integrado.get(
                "hallazgos",
                []
            )
        )


    # ======================================================
    # AGREGAR HALLAZGOS CLÍNICOS A LA INTERPRETACIÓN
    # ======================================================

    hallazgos_totales = []


    for hallazgo in hallazgos_clinicos:

        hallazgos_totales.append(
            f"Variable clínica: {hallazgo}."
        )


    hallazgos_totales.extend(
        interpretacion["hallazgos"]
    )


    # ======================================================
    # INTERPRETACIÓN GLOBAL
    # ======================================================

    if hallazgos_clinicos:

        resumen_clinico = (
            f"Semana 7 identificó "
            f"{len(hallazgos_clinicos)} "
            "variable(s) fuera de las categorías "
            "esperadas definidas en el proyecto. "
        )

    else:

        resumen_clinico = (
            "Las variables evaluadas en Semana 7 "
            "se encuentran dentro de las categorías "
            "esperadas definidas para el proyecto. "
        )


    interpretacion_global = (
        resumen_clinico
        +
        interpretacion["interpretacion"]
    )


    # ======================================================
    # RESULTADO FINAL
    # ======================================================

    return {

        "prioridad":
            prioridad,

        "revision_recomendada":
            revision_recomendada,

        "estado_caso":
            interpretacion["estado"],

        "hallazgos":
            hallazgos_totales,

        "interpretacion":
            interpretacion_global,

        "acciones_recomendadas":
            interpretacion[
                "acciones_recomendadas"
            ],

        "reglas_activadas":
            resultado_semana13[
                "trazas"
            ],

        "semana7":
            resultado_semana7,

        "semana11":
            resultado_semana11,

        "semana13":
            resultado_semana13,
    }
