from collections import defaultdict


# ==========================================================
# SEMANA 14
# REDES SEMÁNTICAS - HIS_IA
# ==========================================================


class RedSemantica:

    def __init__(self):
        self.aristas = defaultdict(list)


    # ======================================================
    # NORMALIZAR TEXTO
    # ======================================================

    @staticmethod
    def normalizar(texto):

        return (
            str(texto)
            .strip()
            .lower()
            .replace(" ", "_")
        )


    # ======================================================
    # AGREGAR TRIPLE
    # ======================================================

    def agregar(
        self,
        sujeto,
        relacion,
        objeto
    ):

        sujeto = self.normalizar(
            sujeto
        )

        relacion = self.normalizar(
            relacion
        )

        objeto = self.normalizar(
            objeto
        )


        relacion_objeto = (
            relacion,
            objeto
        )


        if relacion_objeto not in self.aristas[sujeto]:

            self.aristas[sujeto].append(
                relacion_objeto
            )


    # ======================================================
    # OBTENER TODOS LOS TRIPLES
    # ======================================================

    def obtener_triples(self):

        triples = []


        for sujeto, relaciones in self.aristas.items():

            for relacion, objeto in relaciones:

                triples.append(
                    (
                        sujeto,
                        relacion,
                        objeto
                    )
                )


        return triples


    # ======================================================
    # CONSULTAR RELACIÓN DIRECTA
    # ======================================================

    def consultar(
        self,
        sujeto,
        relacion
    ):

        sujeto = self.normalizar(
            sujeto
        )

        relacion = self.normalizar(
            relacion
        )


        resultados = []


        for relacion_actual, objeto in self.aristas.get(
            sujeto,
            []
        ):

            if relacion_actual == relacion:

                resultados.append(
                    objeto
                )


        return resultados


    # ======================================================
    # CONSULTA JERÁRQUICA ES_UN
    # ======================================================

    def es_un(
        self,
        origen,
        categoria
    ):

        origen = self.normalizar(
            origen
        )

        categoria = self.normalizar(
            categoria
        )


        pendientes = [
            origen
        ]

        visitados = set()


        while pendientes:

            actual = pendientes.pop()


            if actual == categoria:

                return True


            if actual in visitados:

                continue


            visitados.add(
                actual
            )


            for relacion, destino in self.aristas.get(
                actual,
                []
            ):

                if relacion == "es_un":

                    pendientes.append(
                        destino
                    )


        return False


# ==========================================================
# LINGÜÍSTICA
# CONVERTIR ORACIONES SIMPLES EN TRIPLES
# ==========================================================

def interpretar_oracion(
    oracion
):

    texto = (
        str(oracion)
        .strip()
        .lower()
    )


    reemplazos = {

        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
    }


    for original, nuevo in reemplazos.items():

        texto = texto.replace(
            original,
            nuevo
        )


    # ------------------------------------------------------
    # PATRÓN:
    # La orden de laboratorio se envía al LIS
    # ------------------------------------------------------

    if (
        "orden de laboratorio" in texto
        and
        "envia" in texto
        and
        "lis" in texto
    ):

        return (
            "orden_laboratorio",
            "se_envia_a",
            "lis"
        )


    # ------------------------------------------------------
    # PATRÓN:
    # La orden de radiología se envía al RIS
    # ------------------------------------------------------

    if (
        "orden de radiologia" in texto
        and
        "envia" in texto
        and
        "ris" in texto
    ):

        return (
            "orden_radiologia",
            "se_envia_a",
            "ris"
        )


    # ------------------------------------------------------
    # PATRÓN:
    # LIS genera resultado de laboratorio
    # ------------------------------------------------------

    if (
        "lis" in texto
        and
        "genera" in texto
        and
        "resultado" in texto
    ):

        return (
            "lis",
            "genera",
            "resultado_laboratorio"
        )


    # ------------------------------------------------------
    # PATRÓN:
    # RIS genera imagen
    # ------------------------------------------------------

    if (
        "ris" in texto
        and
        "genera" in texto
        and
        "imagen" in texto
    ):

        return (
            "ris",
            "genera",
            "imagen"
        )


    # ------------------------------------------------------
    # PATRÓN:
    # RIS genera informe radiológico
    # ------------------------------------------------------

    if (
        "ris" in texto
        and
        "genera" in texto
        and
        "informe" in texto
    ):

        return (
            "ris",
            "genera",
            "informe_radiologico"
        )


    # ------------------------------------------------------
    # PATRÓN:
    # El resultado retorna al HIS
    # ------------------------------------------------------

    if (
        "resultado" in texto
        and
        "retorna" in texto
        and
        "his" in texto
    ):

        return (
            "resultado_laboratorio",
            "retorna_a",
            "his"
        )


    # ------------------------------------------------------
    # PATRÓN:
    # La imagen se almacena en PACS
    # ------------------------------------------------------

    if (
        "imagen" in texto
        and
        "almacena" in texto
        and
        "pacs" in texto
    ):

        return (
            "imagen",
            "se_almacena_en",
            "pacs"
        )


    raise ValueError(
        "La oración no coincide con los patrones "
        "semánticos admitidos por HIS_IA."
    )


# ==========================================================
# AGREGAR ORACIÓN A LA RED
# ==========================================================

def agregar_oracion(
    red,
    oracion
):

    sujeto, relacion, objeto = (
        interpretar_oracion(
            oracion
        )
    )


    red.agregar(
        sujeto,
        relacion,
        objeto
    )


    return {
        "oracion":
            oracion,

        "sujeto":
            sujeto,

        "relacion":
            relacion,

        "objeto":
            objeto,

        "triple": (
            sujeto,
            relacion,
            objeto
        )
    }



# ==========================================================
# BUSCAR CAMINO ENTRE CONCEPTOS
# ==========================================================

def buscar_camino(
    red,
    origen,
    destino
):

    origen = red.normalizar(
        origen
    )

    destino = red.normalizar(
        destino
    )


    pendientes = [
        (
            origen,
            []
        )
    ]

    visitados = set()


    while pendientes:

        actual, camino = pendientes.pop(
            0
        )


        if actual == destino:

            return camino


        if actual in visitados:

            continue


        visitados.add(
            actual
        )


        for relacion, siguiente in red.aristas.get(
            actual,
            []
        ):

            paso = {
                "desde":
                    actual,

                "relacion":
                    relacion,

                "hasta":
                    siguiente,
            }


            pendientes.append(
                (
                    siguiente,
                    camino + [
                        paso
                    ]
                )
            )


    return []


# ==========================================================
# CONSULTAR PROPIEDADES HEREDADAS
# ==========================================================

def consultar_propiedad_heredada(
    red,
    concepto,
    relacion
):

    concepto = red.normalizar(
        concepto
    )

    relacion = red.normalizar(
        relacion
    )


    resultados = set()

    pendientes = [
        concepto
    ]

    visitados = set()


    while pendientes:

        actual = pendientes.pop()


        if actual in visitados:

            continue


        visitados.add(
            actual
        )


        for rel, destino in red.aristas.get(
            actual,
            []
        ):

            if rel == relacion:

                resultados.add(
                    destino
                )


            if rel == "es_un":

                pendientes.append(
                    destino
                )


    return sorted(
        resultados
    )



# ==========================================================
# RED DEL DOMINIO HIS_IA
# ==========================================================

def crear_red_his_ia():

    red = RedSemantica()


    # ------------------------------------------------------
    # JERARQUÍAS
    # ------------------------------------------------------

    red.agregar(
        "orden_laboratorio",
        "es_un",
        "orden_diagnostica"
    )

    red.agregar(
        "orden_radiologia",
        "es_un",
        "orden_diagnostica"
    )

    red.agregar(
        "resultado_laboratorio",
        "es_un",
        "resultado_diagnostico"
    )

    red.agregar(
        "informe_radiologico",
        "es_un",
        "resultado_diagnostico"
    )


    # ------------------------------------------------------
    # RELACIONES HIS - LIS - RIS
    # ------------------------------------------------------

    red.agregar(
        "paciente",
        "tiene",
        "orden_diagnostica"
    )

    red.agregar(
        "orden_diagnostica",
        "se_registra_en",
        "his"
    )

    red.agregar(
        "orden_laboratorio",
        "se_envia_a",
        "lis"
    )

    red.agregar(
        "orden_radiologia",
        "se_envia_a",
        "ris"
    )

    red.agregar(
        "lis",
        "genera",
        "resultado_laboratorio"
    )

    red.agregar(
        "ris",
        "genera",
        "imagen"
    )

    red.agregar(
        "ris",
        "genera",
        "informe_radiologico"
    )

    red.agregar(
        "resultado_laboratorio",
        "retorna_a",
        "his"
    )

    red.agregar(
        "informe_radiologico",
        "retorna_a",
        "his"
    )

    red.agregar(
        "imagen",
        "se_almacena_en",
        "pacs"
    )


    return red


# ==========================================================
# PRUEBA MANUAL
# ==========================================================

def main():

    red = crear_red_his_ia()


    print()
    print("=" * 70)
    print("SEMANA 14 - RED SEMÁNTICA HIS_IA")
    print("=" * 70)


    print(
        "\n¿Orden de laboratorio es una orden diagnóstica?"
    )

    print(
        red.es_un(
            "orden_laboratorio",
            "orden_diagnostica"
        )
    )


    print(
        "\n¿Orden de radiología es una orden diagnóstica?"
    )

    print(
        red.es_un(
            "orden_radiologia",
            "orden_diagnostica"
        )
    )


    print(
        "\n¿Dónde se envía una orden de laboratorio?"
    )

    print(
        red.consultar(
            "orden_laboratorio",
            "se_envia_a"
        )
    )


    print(
        "\n¿Qué genera LIS?"
    )

    print(
        red.consultar(
            "lis",
            "genera"
        )
    )


    print(
        "\n¿Qué genera RIS?"
    )

    print(
        red.consultar(
            "ris",
            "genera"
        )
    )


    print(
        "\nTRIPLES REGISTRADOS"
    )


    for triple in red.obtener_triples():

        print(
            triple
        )


    print()
    print("=" * 70)


if __name__ == "__main__":

    main()
