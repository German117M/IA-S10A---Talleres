from dataclasses import dataclass
from pathlib import Path

import heapq
import re
import unicodedata

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

RANDOM_STATE = 42

ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = ROOT / "data" / "datos_his.csv"
KB_FILE = ROOT / "data" / "base_conocimiento.txt"

REPORTS_DIR = ROOT / "reports"
REPORT_SEMANA05 = REPORTS_DIR / "semana05.md"


# =========================================================
# SEMANA 3
# CLASIFICACIÓN SIMBÓLICA
# =========================================================

@dataclass(frozen=True)
class Categoria:
    nombre: str
    palabras_clave: tuple[str, ...]


CATEGORIAS = [

    Categoria(
        "Historia clínica",
        (
            "historia clinica",
            "antecedentes",
            "evolucion",
            "consulta",
            "paciente",
            "enfermedad actual",
            "motivo de consulta",
        )
    ),

    Categoria(
        "Laboratorio clínico",
        (
            "laboratorio",
            "hemograma",
            "glucosa",
            "creatinina",
            "troponina",
            "resultado",
            "resultados",
            "muestra",
            "examen",
            "prueba",
        )
    ),

    Categoria(
        "Imagen diagnóstica",
        (
            "radiografia",
            "rayos x",
            "tomografia",
            "resonancia",
            "ecografia",
            "imagen",
            "imagenes",
            "estudio radiologico",
        )
    ),

    Categoria(
        "Medicamentos",
        (
            "medicamento",
            "medicamentos",
            "dosis",
            "tratamiento",
            "prescripcion",
            "formula",
            "terapia",
        )
    ),
]


CUSTOM_RULES = {

    "Historia clínica": (
        "historial",
        "registro clinico",
        "nota medica",
    ),

    "Laboratorio clínico": (
        "analisis",
        "valor de referencia",
        "resultado de laboratorio",
    ),

    "Imagen diagnóstica": (
        "diagnostico por imagen",
        "estudio diagnostico",
        "informe radiologico",
    ),

    "Medicamentos": (
        "orden medica",
        "farmaco",
    ),
}


def normalizar_texto(texto: str) -> str:

    texto = texto.strip().lower()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    texto = re.sub(
        r"[^a-z0-9]+",
        " ",
        texto
    )

    return re.sub(
        r"\s+",
        " ",
        texto
    ).strip()


def construir_categorias():

    categorias_finales = []

    for categoria in CATEGORIAS:

        reglas_extra = CUSTOM_RULES.get(
            categoria.nombre,
            ()
        )

        categorias_finales.append(
            Categoria(
                categoria.nombre,
                categoria.palabras_clave + reglas_extra
            )
        )

    return categorias_finales


def clasificar_texto(texto: str):

    texto_normalizado = normalizar_texto(texto)

    puntuaciones = {}

    for categoria in construir_categorias():

        puntuacion = 0

        for palabra in categoria.palabras_clave:

            if (
                normalizar_texto(palabra)
                in texto_normalizado
            ):
                puntuacion += 1

        puntuaciones[categoria.nombre] = puntuacion

    detectadas = [
        categoria
        for categoria, puntos in puntuaciones.items()
        if puntos > 0
    ]

    if not detectadas:

        return (
            "Requiere análisis",
            [],
            puntuaciones
        )

    principal = max(
        puntuaciones,
        key=puntuaciones.get
    )

    return (
        principal,
        detectadas,
        puntuaciones
    )


# =========================================================
# SEMANA 2
# MACHINE LEARNING
# ESTIMACIÓN DE PRIORIDAD
# =========================================================

def entrenar_modelo_prioridad():

    if not DATA_FILE.exists():

        print(
            "\nNo se encontró el archivo de datos:"
        )

        print(DATA_FILE)

        return None

    try:

        datos = pd.read_csv(
            DATA_FILE,
            sep=None,
            engine="python"
        )

        X = datos[
            [
                "edad",
                "documentos_pendientes",
                "resultados_pendientes",
                "imagenes_pendientes",
            ]
        ]

        y = datos["prioridad"]

        (
            X_train,
            X_test,
            y_train,
            y_test
        ) = train_test_split(
            X,
            y,
            test_size=0.25,
            random_state=RANDOM_STATE,
            stratify=y,
        )

        modelo = make_pipeline(

            StandardScaler(),

            LogisticRegression(
                max_iter=1000,
                random_state=RANDOM_STATE
            )
        )

        modelo.fit(
            X_train,
            y_train
        )

        predicciones = modelo.predict(
            X_test
        )

        accuracy = accuracy_score(
            y_test,
            predicciones
        )

        matriz = confusion_matrix(
            y_test,
            predicciones
        )

        print(
            "\nModelo de prioridad cargado."
        )

        print(
            f"Precisión de validación: {accuracy:.3f}"
        )

        print(
            "Matriz de validación:"
        )

        print(matriz)

        return modelo

    except Exception as error:

        print(
            "\nNo fue posible cargar "
            "el modelo de prioridad."
        )

        print(
            f"Detalle: {error}"
        )

        return None


def evaluar_prioridad(modelo):

    if modelo is None:

        print(
            "\nEl modelo de prioridad "
            "no está disponible."
        )

        return

    print(
        "\nIngrese los datos del registro."
    )

    try:

        edad = int(
            input("Edad: ")
        )

        documentos = int(
            input(
                "Documentos pendientes: "
            )
        )

        resultados = int(
            input(
                "Resultados pendientes: "
            )
        )

        imagenes = int(
            input(
                "Imágenes pendientes: "
            )
        )

    except ValueError:

        print(
            "\nLos valores deben ser numéricos."
        )

        return

    registro = pd.DataFrame(
        [
            {
                "edad": edad,
                "documentos_pendientes": documentos,
                "resultados_pendientes": resultados,
                "imagenes_pendientes": imagenes,
            }
        ]
    )

    prediccion = modelo.predict(
        registro
    )[0]

    resultado = (
        "Prioritaria"
        if prediccion == 1
        else "Normal"
    )

    print(
        "\nPrioridad estimada:",
        resultado
    )


# =========================================================
# SEMANA 4
# BÚSQUEDA A*
# ORGANIZACIÓN DE REVISIÓN
# =========================================================

COSTOS_REVISION = {

    "Historia clínica": {
        "procesamiento": 1,
        "espera": 1,
    },

    "Resultados de laboratorio": {
        "procesamiento": 2,
        "espera": 3,
    },

    "Estudio de imagen": {
        "procesamiento": 3,
        "espera": 3,
    },

    "Medicamentos": {
        "procesamiento": 2,
        "espera": 2,
    },
}


def heuristica(pendientes):

    return sum(
        COSTOS_REVISION[elemento]["procesamiento"]
        for elemento in pendientes
    )


def costo_transicion(
    estado,
    elemento
):

    costo_base = (
        COSTOS_REVISION[elemento][
            "procesamiento"
        ]
    )

    pendientes_restantes = [
        actual
        for actual in estado
        if actual != elemento
    ]

    penalizacion = sum(
        COSTOS_REVISION[pendiente]["espera"]
        for pendiente in pendientes_restantes
    )

    return (
        costo_base
        + penalizacion
    )


def planificar_revision(elementos):

    inicio = tuple(elementos)
    meta = tuple()

    frontera = []

    contador = 0

    heapq.heappush(
        frontera,
        (
            heuristica(inicio),
            contador,
            0,
            inicio,
            []
        )
    )

    mejores_costos = {
        inicio: 0
    }

    while frontera:

        (
            _,
            _,
            costo_actual,
            estado,
            camino
        ) = heapq.heappop(
            frontera
        )

        if estado == meta:

            return (
                camino,
                costo_actual
            )

        if costo_actual > mejores_costos.get(
            estado,
            float("inf")
        ):
            continue

        for elemento in estado:

            nuevo_estado = list(
                estado
            )

            nuevo_estado.remove(
                elemento
            )

            nuevo_estado = tuple(
                nuevo_estado
            )

            costo_paso = costo_transicion(
                estado,
                elemento
            )

            nuevo_costo = (
                costo_actual
                + costo_paso
            )

            if nuevo_costo < mejores_costos.get(
                nuevo_estado,
                float("inf")
            ):

                mejores_costos[
                    nuevo_estado
                ] = nuevo_costo

                estimacion = heuristica(
                    nuevo_estado
                )

                prioridad = (
                    nuevo_costo
                    + estimacion
                )

                contador += 1

                heapq.heappush(
                    frontera,
                    (
                        prioridad,
                        contador,
                        nuevo_costo,
                        nuevo_estado,
                        camino + [elemento]
                    )
                )

    return None, None


def gestionar_revision():

    print(
        "\nGESTIÓN DE REVISIÓN DE "
        "RESULTADOS Y ESTUDIOS"
    )

    print(
        "\n1. Historia clínica"
    )

    print(
        "2. Resultados de laboratorio"
    )

    print(
        "3. Estudio de imagen"
    )

    print(
        "4. Medicamentos"
    )

    entrada = input(
        "\nIngrese las opciones "
        "separadas por coma: "
    )

    mapa = {

        "1": "Historia clínica",

        "2": "Resultados de laboratorio",

        "3": "Estudio de imagen",

        "4": "Medicamentos",
    }

    elementos = []

    for opcion in entrada.split(","):

        opcion = opcion.strip()

        if (
            opcion in mapa
            and mapa[opcion]
            not in elementos
        ):

            elementos.append(
                mapa[opcion]
            )

    if not elementos:

        print(
            "\nNo se seleccionaron "
            "elementos válidos."
        )

        return

    camino, costo = planificar_revision(
        elementos
    )

    print(
        "\nSecuencia sugerida de revisión:"
    )

    for numero, elemento in enumerate(
        camino,
        start=1
    ):

        print(
            f"{numero}. {elemento}"
        )

    print(
        f"\nCosto total estimado: {costo}"
    )


# =========================================================
# SEMANA 5
# SISTEMA EXPERTO
# =========================================================

REGLAS_EXPERTAS = [

    (
        lambda q:
        "hemograma" in q
        or "creatinina" in q
        or "glucosa" in q
        or "laboratorio" in q,

        "revisar_resultados_laboratorio"
    ),

    (
        lambda q:
        "radiografia" in q
        or "tomografia" in q
        or "resonancia" in q
        or "imagen" in q,

        "revisar_estudio_imagen"
    ),

    (
        lambda q:
        "historia" in q
        or "antecedente" in q
        or "evolucion" in q
        or "consulta" in q,

        "revisar_historia_clinica"
    ),

    (
        lambda q:
        "medicamento" in q
        or "dosis" in q
        or "tratamiento" in q
        or "prescripcion" in q,

        "revisar_medicacion"
    ),

    (
        lambda q:
        "pendiente" in q
        or "prioridad" in q
        or "urgente" in q
        or "revisar primero" in q,

        "evaluar_prioridad_revision"
    ),
]


# =========================================================
# SEMANA 5
# EJEMPLOS ETIQUETADOS
# =========================================================

TRAIN_TEXTOS = [

    # HISTORIA CLÍNICA
    "revisar antecedentes del paciente",
    "consultar historia clinica completa",
    "ver evolucion registrada",
    "revisar motivo de consulta",

    # LABORATORIO
    "resultado de hemograma disponible",
    "revisar resultado de creatinina",
    "resultado de glucosa pendiente",
    "consultar resultados de laboratorio",

    # IMÁGENES
    "radiografia disponible para revision",
    "consultar tomografia del paciente",
    "revisar resonancia registrada",
    "estudio de imagen pendiente",

    # MEDICAMENTOS
    "consultar medicamentos registrados",
    "revisar dosis del tratamiento",
    "ver prescripcion del paciente",
    "consultar tratamiento actual",

    # SEGUIMIENTO
    "hay documentos pendientes de revision",
    "determinar prioridad del registro",
    "hay resultados pendientes",
    "organizar informacion para seguimiento",
]


TRAIN_CLASES = [

    "historia_clinica",
    "historia_clinica",
    "historia_clinica",
    "historia_clinica",

    "laboratorio",
    "laboratorio",
    "laboratorio",
    "laboratorio",

    "imagen_diagnostica",
    "imagen_diagnostica",
    "imagen_diagnostica",
    "imagen_diagnostica",

    "medicamentos",
    "medicamentos",
    "medicamentos",
    "medicamentos",

    "seguimiento",
    "seguimiento",
    "seguimiento",
    "seguimiento",
]


# =========================================================
# SEMANA 5
# BASE DE CONOCIMIENTO
# =========================================================

def cargar_base_conocimiento():

    if not KB_FILE.exists():

        raise FileNotFoundError(
            "No existe "
            "proyecto_his/data/base_conocimiento.txt"
        )

    documentos = [

        linea.strip()

        for linea in KB_FILE.read_text(
            encoding="utf-8"
        ).splitlines()

        if linea.strip()
    ]

    if len(documentos) < 8:

        raise ValueError(
            "La base de conocimiento "
            "debe contener mínimo 8 entradas."
        )

    return documentos


# =========================================================
# SEMANA 5
# SISTEMA HÍBRIDO
# =========================================================

class SistemaHibridoHIS:

    def __init__(self):

        self.documentos = (
            cargar_base_conocimiento()
        )

        self.vectorizador_documentos = (
            TfidfVectorizer()
        )

        self.matriz_documentos = (
            self.vectorizador_documentos.fit_transform(
                self.documentos
            )
        )

        self.clasificador = make_pipeline(

            TfidfVectorizer(),

            LogisticRegression(
                max_iter=1000,
                random_state=RANDOM_STATE
            )
        )

        self.clasificador.fit(
            TRAIN_TEXTOS,
            TRAIN_CLASES
        )


    def analizar_consulta(
        self,
        consulta
    ):

        consulta_normalizada = (
            normalizar_texto(
                consulta
            )
        )

        reglas = [

            nombre

            for condicion, nombre
            in REGLAS_EXPERTAS

            if condicion(
                consulta_normalizada
            )
        ]

        vector_consulta = (
            self.vectorizador_documentos.transform(
                [consulta_normalizada]
            )
        )

        similitudes = cosine_similarity(
            vector_consulta,
            self.matriz_documentos
        )[0]

        mejor_indice = int(
            similitudes.argmax()
        )

        evidencia = (
            self.documentos[
                mejor_indice
            ]
        )

        similitud = float(
            similitudes[
                mejor_indice
            ]
        )

        clase = str(
            self.clasificador.predict(
                [consulta_normalizada]
            )[0]
        )

        return {

            "consulta": consulta,

            "reglas": reglas,

            "evidencia": evidencia,

            "similitud": similitud,

            "clase": clase,
        }


# =========================================================
# SEMANA 5
# MOSTRAR RESULTADO
# =========================================================

def mostrar_resultado_hibrido(
    resultado
):

    print("\n" + "=" * 60)

    print(
        "RESULTADO DEL ASISTENTE"
    )

    print("=" * 60)

    if resultado["reglas"]:

        print(
            "\nAcción sugerida:"
        )

        for regla in resultado["reglas"]:

            print(
                f"- {regla}"
            )

    else:

        print(
            "\nNo se activó una regla específica."
        )

    print(
        "\nInformación relacionada:"
    )

    print(
        resultado["evidencia"]
    )

    print(
        "\nSimilitud:",
        f"{resultado['similitud']:.3f}"
    )

    print(
        "\nCategoría:",
        resultado["clase"]
    )


# =========================================================
# SEMANA 5
# REPORTE
# =========================================================

def generar_reporte_semana05(
    resultados
):

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    lineas = [

        "# Semana 05 - Sistema híbrido HIS_IA",

        "",

        "## Descripción",

        (
            "HIS_IA integra reglas expertas, "
            "recuperación de información mediante "
            "TF-IDF y similitud coseno, clasificación "
            "de texto y procesamiento básico de "
            "lenguaje natural."
        ),

        "",

        (
            "El sistema está orientado a apoyar "
            "la organización y recuperación de "
            "información dentro de un HIS."
        ),

        "",
    ]

    for numero, resultado in enumerate(
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

            (
                f"**Consulta:** "
                f"{resultado['consulta']}"
            ),

            "",

            (
                f"**Regla activada:** "
                f"{reglas}"
            ),

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
            "El resultado es explicable porque "
            "el sistema muestra qué regla fue "
            "activada, qué información recuperó, "
            "qué similitud obtuvo y qué categoría "
            "predijo."
        ),

        "",

        "## Limitaciones",

        "",

        (
            "La calidad de las respuestas depende "
            "de las reglas definidas, de la base "
            "de conocimiento y de los ejemplos "
            "utilizados para entrenar el clasificador."
        ),

        "",

        (
            "Este prototipo académico organiza "
            "y recupera información. No interpreta "
            "resultados clínicos ni reemplaza "
            "la valoración de un profesional."
        ),
    ]

    REPORT_SEMANA05.write_text(
        "\n".join(lineas),
        encoding="utf-8"
    )


# =========================================================
# SEMANA 5
# CONSULTA INTERACTIVA
# =========================================================

def consultar_asistente(
    sistema_hibrido
):

    print(
        "\nCONSULTA DE INFORMACIÓN CLÍNICA"
    )

    consulta = input(
        "\nEscriba su consulta:\n"
    )

    if not consulta.strip():

        print(
            "\nLa consulta está vacía."
        )

        return

    resultado = (
        sistema_hibrido.analizar_consulta(
            consulta
        )
    )

    mostrar_resultado_hibrido(
        resultado
    )


# =========================================================
# SEMANA 5
# PRUEBAS REPRODUCIBLES
# =========================================================

def ejecutar_pruebas_semana05(
    sistema_hibrido
):

    consultas = [

        (
            "Tengo pendiente revisar "
            "el resultado de creatinina "
            "del paciente"
        ),

        (
            "Hay una radiografía disponible "
            "para revisión"
        ),

        (
            "Necesito consultar los antecedentes "
            "y la evolución registrada "
            "en la historia clínica"
        ),
    ]

    resultados = []

    print("\n" + "=" * 60)

    print(
        "VALIDACIÓN DEL ASISTENTE HIS_IA"
    )

    print("=" * 60)

    for numero, consulta in enumerate(
        consultas,
        start=1
    ):

        resultado = (
            sistema_hibrido.analizar_consulta(
                consulta
            )
        )

        resultados.append(
            resultado
        )

        print(
            f"\nConsulta {numero}: "
            f"{consulta}"
        )

        mostrar_resultado_hibrido(
            resultado
        )

    generar_reporte_semana05(
        resultados
    )

    print(
        "\nReporte generado:"
    )

    print(
        REPORT_SEMANA05
    )


# =========================================================
# INTERFAZ PRINCIPAL
# =========================================================

def mostrar_menu():

    print("\n" + "=" * 60)

    print("HIS_IA")

    print(
        "ASISTENTE DE INTELIGENCIA "
        "ARTIFICIAL PARA HIS"
    )

    print("=" * 60)

    print(
        "\n1. Analizar información clínica"
    )

    print(
        "2. Evaluar prioridad de revisión"
    )

    print(
        "3. Gestionar revisión de "
        "resultados y estudios"
    )

    print(
        "4. Consultar asistente clínico"
    )

    print(
        "5. Validar funcionamiento"
    )

    print(
        "6. Salir"
    )


# =========================================================
# PROGRAMA PRINCIPAL
# =========================================================

def main():

    print(
        "\nIniciando HIS_IA..."
    )

    modelo_prioridad = (
        entrenar_modelo_prioridad()
    )

    try:

        sistema_hibrido = (
            SistemaHibridoHIS()
        )

        print(
            "Base de conocimiento cargada."
        )

    except Exception as error:

        sistema_hibrido = None

        print(
            "\nNo fue posible cargar "
            "el sistema híbrido."
        )

        print(
            f"Detalle: {error}"
        )

    while True:

        mostrar_menu()

        opcion = input(
            "\nSeleccione una opción: "
        )

        if opcion == "1":

            texto = input(
                "\nIngrese la información clínica:\n"
            )

            (
                principal,
                detectadas,
                _
            ) = clasificar_texto(
                texto
            )

            print(
                "\nCategoría principal:",
                principal
            )

            if detectadas:

                print(
                    "\nInformación relacionada:"
                )

                for categoria in detectadas:

                    print(
                        f"- {categoria}"
                    )

        elif opcion == "2":

            evaluar_prioridad(
                modelo_prioridad
            )

        elif opcion == "3":

            gestionar_revision()

        elif opcion == "4":

            if sistema_hibrido is None:

                print(
                    "\nEl asistente no "
                    "está disponible."
                )

            else:

                consultar_asistente(
                    sistema_hibrido
                )

        elif opcion == "5":

            if sistema_hibrido is None:

                print(
                    "\nEl asistente no "
                    "está disponible."
                )

            else:

                ejecutar_pruebas_semana05(
                    sistema_hibrido
                )

        elif opcion == "6":

            print(
                "\nCerrando HIS_IA."
            )

            break

        else:

            print(
                "\nOpción no válida."
            )


if __name__ == "__main__":
    main()