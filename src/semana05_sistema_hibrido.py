from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline


# =========================================================
# CONFIGURACIÓN
# =========================================================

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"

KB_PATH = DATA_DIR / "base_conocimiento.txt"
REPORT_PATH = REPORTS_DIR / "semana05.md"


# =========================================================
# SISTEMA EXPERTO
# =========================================================

RULES = [

    (
        lambda q: "caliente" in q
        or "temperatura" in q
        or "ventilador" in q,

        "revisar_ventilacion"
    ),

    (
        lambda q: "internet" in q
        or "dns" in q
        or "red" in q,

        "revisar_conectividad"
    ),

    (
        lambda q: "lento" in q
        or "lentitud" in q
        or "memoria" in q,

        "revisar_rendimiento"
    ),

    (
        lambda q: "cuenta" in q
        or "sesion" in q
        or "credencial" in q,

        "revisar_acceso"
    ),

    (
        lambda q: "impresora" in q
        or "impresion" in q,

        "revisar_impresion"
    ),
]


# =========================================================
# EJEMPLOS ETIQUETADOS
# =========================================================

TRAIN_X = [

    # RED
    "se cae internet",
    "error de dns",
    "no tengo conexion de red",
    "la red esta inestable",
    "no puedo navegar",

    # HARDWARE
    "el equipo esta caliente",
    "el ventilador hace ruido",
    "el computador no enciende",
    "el disco tiene poco espacio",
    "el equipo esta muy lento",

    # ACCESO
    "no puedo iniciar sesion",
    "mi cuenta esta bloqueada",
    "error de credenciales",
    "usuario sin permisos",
    "no puedo ingresar al sistema",
]


TRAIN_Y = [

    "red",
    "red",
    "red",
    "red",
    "red",

    "hardware",
    "hardware",
    "hardware",
    "hardware",
    "hardware",

    "acceso",
    "acceso",
    "acceso",
    "acceso",
    "acceso",
]


# =========================================================
# CARGAR BASE DE CONOCIMIENTO
# =========================================================

def cargar_documentos():

    if not KB_PATH.exists():

        raise FileNotFoundError(
            "No existe data/base_conocimiento.txt"
        )

    documentos = [

        linea.strip()

        for linea in KB_PATH.read_text(
            encoding="utf-8"
        ).splitlines()

        if linea.strip()
    ]

    if len(documentos) < 8:

        raise ValueError(
            "La base de conocimiento debe tener "
            "mínimo 8 entradas."
        )

    return documentos


# =========================================================
# PREPARACIÓN DE TF-IDF
# =========================================================

DOCUMENTOS = cargar_documentos()

vectorizador = TfidfVectorizer()

matriz_documentos = vectorizador.fit_transform(
    DOCUMENTOS
)


# =========================================================
# CLASIFICADOR
# =========================================================

clasificador = make_pipeline(

    TfidfVectorizer(),

    LogisticRegression(
        max_iter=1000,
        random_state=42
    )
)

clasificador.fit(
    TRAIN_X,
    TRAIN_Y
)


# =========================================================
# RESPONDER CONSULTA
# =========================================================

def responder(consulta):

    consulta_normalizada = (
        consulta.lower().strip()
    )

    # -----------------------------------------------------
    # SISTEMA EXPERTO
    # -----------------------------------------------------

    reglas_activadas = [

        nombre

        for condicion, nombre in RULES

        if condicion(consulta_normalizada)
    ]

    # -----------------------------------------------------
    # RECUPERACIÓN DE INFORMACIÓN
    # -----------------------------------------------------

    vector_consulta = vectorizador.transform(
        [consulta_normalizada]
    )

    similitudes = cosine_similarity(
        vector_consulta,
        matriz_documentos
    )[0]

    mejor_indice = int(
        similitudes.argmax()
    )

    evidencia = DOCUMENTOS[
        mejor_indice
    ]

    similitud = float(
        similitudes[
            mejor_indice
        ]
    )

    # -----------------------------------------------------
    # CLASIFICACIÓN
    # -----------------------------------------------------

    clase = str(
        clasificador.predict(
            [consulta_normalizada]
        )[0]
    )

    return {

        "reglas": reglas_activadas,

        "evidencia": evidencia,

        "similitud": similitud,

        "clase": clase,
    }


# =========================================================
# GENERACIÓN DEL REPORTE
# =========================================================

def generar_reporte(resultados):

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    lineas = [

        "# Semana 05 - Sistema híbrido",

        "",

        "## Objetivo",

        (
            "Aplicar sistemas expertos, recuperación "
            "de información, clasificación y "
            "procesamiento de lenguaje natural."
        ),

        "",
    ]

    for numero, (
        consulta,
        resultado
    ) in enumerate(
        resultados,
        start=1
    ):

        reglas = ", ".join(
            resultado["reglas"]
        )

        if not reglas:

            reglas = "Ninguna"

        lineas += [

            f"## Consulta {numero}",

            "",

            f"**Consulta:** {consulta}",

            "",

            f"**Regla activada:** {reglas}",

            "",

            (
                f"**Evidencia recuperada:** "
                f"{resultado['evidencia']}"
            ),

            "",

            (
                f"**Similitud:** "
                f"{resultado['similitud']:.3f}"
            ),

            "",

            (
                f"**Clasificación:** "
                f"{resultado['clase']}"
            ),

            "",
        ]

    lineas += [

        "## Análisis",

        "",

        (
            "El sistema combina reglas expertas, "
            "recuperación mediante TF-IDF y similitud "
            "coseno, y clasificación automática de texto."
        ),

        "",

        (
            "La respuesta es trazable porque permite "
            "identificar la regla utilizada, la evidencia "
            "recuperada, el valor de similitud y la clase "
            "predicha."
        ),

        "",

        "## Limitaciones",

        "",

        (
            "El sistema depende de las reglas, documentos "
            "y ejemplos utilizados durante su construcción. "
            "Una base pequeña puede producir clasificaciones "
            "o recuperaciones poco precisas."
        ),
    ]

    REPORT_PATH.write_text(
        "\n".join(lineas),
        encoding="utf-8"
    )


# =========================================================
# PRUEBAS
# =========================================================

def main():

    consultas = [

        "Internet se cae y aparece error DNS",

        "El equipo está caliente y el ventilador hace ruido",

        "No puedo iniciar sesión porque mi cuenta está bloqueada",
    ]

    resultados = []

    print("\n" + "=" * 60)

    print(
        "SEMANA 05 - SISTEMA HÍBRIDO"
    )

    print("=" * 60)

    for numero, consulta in enumerate(
        consultas,
        start=1
    ):

        resultado = responder(
            consulta
        )

        resultados.append(
            (
                consulta,
                resultado
            )
        )

        print(
            f"\nConsulta {numero}:"
        )

        print(
            consulta
        )

        print(
            "\nReglas:",
            resultado["reglas"]
        )

        print(
            "Evidencia:",
            resultado["evidencia"]
        )

        print(
            "Similitud:",
            f"{resultado['similitud']:.3f}"
        )

        print(
            "Clase:",
            resultado["clase"]
        )

        print("-" * 60)

    generar_reporte(
        resultados
    )

    print(
        "\nReporte generado:"
    )

    print(
        REPORT_PATH
    )


if __name__ == "__main__":
    main()