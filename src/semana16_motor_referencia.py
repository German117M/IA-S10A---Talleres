"""
Semana 16 - Motor de referencia HIS_IA.

Recupera conocimiento VALIDADO de Semana 15.
No genera respuestas nuevas.
"""

import re
import unicodedata

from semana15_base_conocimiento import (
    conectar,
    RUTA_DB,
)


# ==========================================================
# PALABRAS POCO ÚTILES PARA LA COMPARACIÓN
# ==========================================================

PALABRAS_VACIAS = {
    "a",
    "al",
    "como",
    "con",
    "cual",
    "de",
    "del",
    "el",
    "en",
    "es",
    "la",
    "las",
    "lo",
    "los",
    "para",
    "por",
    "que",
    "se",
    "una",
    "un",
    "y",
}


# ==========================================================
# NORMALIZAR TEXTO
# ==========================================================

def normalizar(texto: str) -> set[str]:
    """
    Convierte texto a minúsculas,
    elimina tildes y separa palabras.
    """

    descompuesto = unicodedata.normalize(
        "NFD",
        str(texto).casefold()
    )

    sin_tildes = "".join(
        caracter
        for caracter in descompuesto
        if unicodedata.category(caracter) != "Mn"
    )

    palabras = set(
        re.findall(
            r"[a-z0-9]+",
            sin_tildes
        )
    )

    return {
        palabra
        for palabra in palabras
        if palabra not in PALABRAS_VACIAS
    }


# ==========================================================
# OBTENER REFERENCIAS VALIDADAS
# ==========================================================

def obtener_referencias_validadas(
    ruta=RUTA_DB
):
    """
    Obtiene únicamente artículos VALIDADO
    de la base de conocimiento de Semana 15.
    """

    consulta = """
        SELECT
            a.id,
            a.titulo,
            a.contenido,
            a.fuente,
            a.fecha_revision,
            a.estado,

            d.nombre AS dominio,

            ap.nombre AS aplicacion,

            e.nombre AS responsable,

            h.nombre AS herramienta

        FROM articulo a

        JOIN dominio d
            ON d.id = a.dominio_id

        JOIN experto e
            ON e.id = a.experto_id

        LEFT JOIN aplicacion ap
            ON ap.id = a.aplicacion_id

        LEFT JOIN herramienta h
            ON h.id = a.herramienta_id

        WHERE
            a.estado = 'VALIDADO'

        ORDER BY
            a.id
    """

    with conectar(ruta) as conexion:

        filas = conexion.execute(
            consulta
        ).fetchall()

        return [
            dict(fila)
            for fila in filas
        ]


# ==========================================================
# CONSTRUIR PALABRAS CLAVE DE UNA REFERENCIA
# ==========================================================

def obtener_claves_referencia(
    referencia
):
    """
    Genera las palabras comparables utilizando
    información ya almacenada en Semana 15.
    """

    partes = [
        referencia.get("titulo", ""),
        referencia.get("contenido", ""),
        referencia.get("dominio", ""),
        referencia.get("aplicacion", "") or "",
    ]

    return normalizar(
        " ".join(partes)
    )


# ==========================================================
# CONSULTAR MOTOR DE REFERENCIA
# ==========================================================

def consultar(
    pregunta: str,
    ruta=RUTA_DB
):
    """
    Selecciona la referencia VALIDADA
    con mayor cantidad de coincidencias.
    """

    palabras = normalizar(
        pregunta
    )


    # ------------------------------------------------------
    # SIN DATOS
    # ------------------------------------------------------

    if not palabras:

        return {
            "estado": "SIN_DATOS",
            "mensaje": "Escribe una consulta.",
            "referencia": None,
            "palabras_consulta": [],
        }


    candidatos = []


    # ------------------------------------------------------
    # BUSCAR REFERENCIAS
    # ------------------------------------------------------

    referencias = (
        obtener_referencias_validadas(
            ruta
        )
    )


    for referencia in referencias:

        claves = obtener_claves_referencia(
            referencia
        )

        coincidencias = (
            palabras.intersection(
                claves
            )
        )


        if coincidencias:

            candidatos.append(
                (
                    len(coincidencias),
                    referencia["id"],
                    referencia,
                    coincidencias,
                )
            )


    # ------------------------------------------------------
    # SIN REFERENCIA
    # ------------------------------------------------------

    if not candidatos:

        return {
            "estado": "SIN_REFERENCIA",

            "mensaje": (
                "No hay evidencia validada "
                "para responder esta consulta. "
                "Se recomienda revisión humana."
            ),

            "referencia": None,

            "palabras_consulta":
                sorted(palabras),
        }


    # ------------------------------------------------------
    # ORDENAR CANDIDATOS
    # Mayor puntuación primero.
    # En empate, menor ID.
    # ------------------------------------------------------

    candidatos.sort(
        key=lambda item: (
            -item[0],
            item[1]
        )
    )


    puntuacion, _, mejor, coincidencias = (
        candidatos[0]
    )


    # ------------------------------------------------------
    # RESPUESTA TRAZABLE
    # ------------------------------------------------------

    return {

        "estado":
            "ENCONTRADA",

        "mensaje":
            mejor["contenido"],

        "palabras_consulta":
            sorted(palabras),

        "referencia": {

            "id":
                f"ART-{mejor['id']:03d}",

            "articulo_id":
                mejor["id"],

            "titulo":
                mejor["titulo"],

            "dominio":
                mejor["dominio"],

            "aplicacion":
                mejor["aplicacion"],

            "responsable":
                mejor["responsable"],

            "herramienta":
                mejor["herramienta"],

            "fuente":
                mejor["fuente"],

            "fecha_revision":
                mejor["fecha_revision"],

            "estado":
                mejor["estado"],

            "coincidencias":
                puntuacion,

            "terminos_coincidentes":
                sorted(coincidencias),
        }
    }


# ==========================================================
# DEMOSTRACIÓN
# ==========================================================

def main():

    from semana15_base_conocimiento import (
        inicializar_base
    )

    inicializar_base()

    preguntas = [
        "¿Cómo se crea una orden de laboratorio?",
        "¿Cómo retornan los resultados LIS al HIS?",
        "¿Dónde se almacenan las imágenes RIS?",
        "¿Dónde parqueo mi bicicleta?",
        "",
    ]


    print()
    print("=" * 70)
    print("SEMANA 16 - MOTOR DE REFERENCIA HIS_IA")
    print("=" * 70)


    for pregunta in preguntas:

        resultado = consultar(
            pregunta
        )

        print()
        print("Pregunta:", pregunta)
        print("Estado:", resultado["estado"])
        print("Respuesta:", resultado["mensaje"])

        if resultado["referencia"]:

            ref = resultado["referencia"]

            print(
                "Referencia:",
                ref["id"]
            )

            print(
                "Título:",
                ref["titulo"]
            )

            print(
                "Fuente:",
                ref["fuente"]
            )

            print(
                "Coincidencias:",
                ref["coincidencias"]
            )

            print(
                "Términos:",
                ", ".join(
                    ref["terminos_coincidentes"]
                )
            )

        print("-" * 70)


if __name__ == "__main__":

    main()
