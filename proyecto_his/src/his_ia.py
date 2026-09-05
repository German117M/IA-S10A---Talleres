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


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

RANDOM_STATE = 42

ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = ROOT / "data" / "datos_his.csv"
KB_FILE = ROOT / "data" / "base_conocimiento.txt"
TRAIN_FILE = ROOT / "data" / "ejemplos_clasificacion.csv"

REPORTS_DIR = ROOT / "reports"
REPORT_SEMANA05 = REPORTS_DIR / "semana05.md"


# ============================================================
# SEMANA 3
# CLASIFICACIÓN SIMBÓLICA
# ============================================================


@dataclass(frozen=True)
class Categoria:
    nombre: str
    palabras_clave: tuple[str, ...]


CATEGORIAS = [

    Categoria(
        nombre="Historia clínica",
        palabras_clave=(
            "historia",
            "antecedente",
            "antecedentes",
            "evolucion",
            "consulta",
            "motivo de consulta",
            "nota clinica",
        ),
    ),

    Categoria(
        nombre="Laboratorio clínico",
        palabras_clave=(
            "laboratorio",
            "hemograma",
            "creatinina",
            "glucosa",
            "resultado",
            "resultados",
            "prueba",
        ),
    ),

    Categoria(
        nombre="Imagen diagnóstica",
        palabras_clave=(
            "imagen",
            "radiografia",
            "tomografia",
            "resonancia",
            "radiologia",
            "estudio",
        ),
    ),

    Categoria(
        nombre="Medicamentos",
        palabras_clave=(
            "medicamento",
            "medicamentos",
            "dosis",
            "tratamiento",
            "prescripcion",
            "medicacion",
        ),
    ),
]


CUSTOM_RULES = {

    "Historia clínica": (
        "historial clinico",
        "nota de evolucion",
    ),

    "Laboratorio clínico": (
        "resultado laboratorio",
        "prueba laboratorio",
    ),

    "Imagen diagnóstica": (
        "estudio imagen",
        "imagen diagnostica",
    ),

    "Medicamentos": (
        "tratamiento actual",
        "medicamento registrado",
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

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


def construir_categorias():

    categorias_finales = []

    for categoria in CATEGORIAS:

        adicionales = CUSTOM_RULES.get(
            categoria.nombre,
            ()
        )

        palabras = (
            categoria.palabras_clave
            + adicionales
        )

        categorias_finales.append(

            Categoria(
                nombre=categoria.nombre,
                palabras_clave=palabras
            )

        )

    return categorias_finales


def clasificar_texto(texto: str):

    texto_normalizado = normalizar_texto(
        texto
    )

    categorias = construir_categorias()

    puntuaciones = {}

    for categoria in categorias:

        puntos = 0

        for palabra in categoria.palabras_clave:

            palabra_normalizada = normalizar_texto(
                palabra
            )

            if palabra_normalizada in texto_normalizado:
                puntos += 1

        puntuaciones[
            categoria.nombre
        ] = puntos


    detectadas = [

        categoria

        for categoria, puntos
        in puntuaciones.items()

        if puntos > 0
    ]


    if detectadas:

        principal = max(
            detectadas,
            key=lambda categoria:
                puntuaciones[categoria]
        )

    else:

        principal = "Requiere análisis"


    return (
        principal,
        detectadas,
        puntuaciones
    )


# ============================================================
# SEMANA 2
# MODELO DE PRIORIDAD
# ============================================================


def entrenar_modelo_prioridad():

    if not DATA_FILE.exists():

        raise FileNotFoundError(
            f"No se encontró el archivo: {DATA_FILE}"
        )


    datos = pd.read_csv(
        DATA_FILE
    )


    columnas_requeridas = {

        "edad",

        "documentos_pendientes",

        "resultados_pendientes",

        "imagenes_pendientes",

        "prioridad",
    }


    if not columnas_requeridas.issubset(
        datos.columns
    ):

        raise ValueError(

            "El archivo datos_his.csv no contiene "
            "todas las columnas requeridas."

        )


    X = datos[
        [
            "edad",
            "documentos_pendientes",
            "resultados_pendientes",
            "imagenes_pendientes",
        ]
    ]


    y = datos[
        "prioridad"
    ]


    X_train, X_test, y_train, y_test = (
        train_test_split(

            X,
            y,

            test_size=0.25,

            random_state=RANDOM_STATE,

            stratify=y
        )
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


    print("\nModelo de prioridad cargado.")

    print(
        f"Precisión de validación: "
        f"{accuracy:.3f}"
    )

    print(
        "Matriz de validación:"
    )

    print(
        matriz
    )


    return modelo


def evaluar_prioridad(
    modelo
):

    print(
        "\nEVALUACIÓN DE PRIORIDAD"
    )


    try:

        edad = int(
            input(
                "Edad: "
            )
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
            "Los valores deben ser numéricos."
        )

        return


    registro = pd.DataFrame(
        [
            {

                "edad":
                    edad,

                "documentos_pendientes":
                    documentos,

                "resultados_pendientes":
                    resultados,

                "imagenes_pendientes":
                    imagenes,
            }
        ]
    )


    prediccion = modelo.predict(
        registro
    )[0]


    resultado = (

        "Prioritaria"

        if int(prediccion) == 1

        else "Normal"
    )


    print(
        f"\nPrioridad estimada: "
        f"{resultado}"
    )


# ============================================================
# SEMANA 4
# BÚSQUEDA A*
# ============================================================


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


def heuristica(
    pendientes
):

    return sum(

        COSTOS_REVISION[
            elemento
        ]["procesamiento"]

        for elemento in pendientes
    )


def costo_transicion(
    estado,
    seleccionado
):

    costo = (
        COSTOS_REVISION[
            seleccionado
        ]["procesamiento"]
    )


    restantes = [

        elemento

        for elemento in estado

        if elemento != seleccionado
    ]


    for elemento in restantes:

        costo += (
            COSTOS_REVISION[
                elemento
            ]["espera"]
        )


    return costo


def planificar_revision(
    elementos
):

    inicio = tuple(
        elementos
    )


    if not inicio:

        return [], 0


    frontera = []

    contador = 0


    heapq.heappush(

        frontera,

        (

            heuristica(
                inicio
            ),

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
            prioridad,
            _,
            costo_actual,
            estado,
            camino
        ) = heapq.heappop(
            frontera
        )


        if not estado:

            return (
                camino,
                costo_actual
            )


        for seleccionado in estado:

            nuevo_estado = tuple(

                elemento

                for elemento in estado

                if elemento != seleccionado
            )


            costo_paso = costo_transicion(

                estado,
                seleccionado
            )


            nuevo_costo = (

                costo_actual
                + costo_paso
            )


            if (

                nuevo_estado
                not in mejores_costos

                or

                nuevo_costo
                < mejores_costos[
                    nuevo_estado
                ]
            ):


                mejores_costos[
                    nuevo_estado
                ] = nuevo_costo


                contador += 1


                nueva_prioridad = (

                    nuevo_costo

                    + heuristica(
                        nuevo_estado
                    )
                )


                heapq.heappush(

                    frontera,

                    (

                        nueva_prioridad,

                        contador,

                        nuevo_costo,

                        nuevo_estado,

                        camino
                        + [seleccionado]
                    )
                )


    return [], 0


def gestionar_revision():

    opciones = {

        "1":
            "Historia clínica",

        "2":
            "Resultados de laboratorio",

        "3":
            "Estudio de imagen",

        "4":
            "Medicamentos",
    }


    print(
        "\nGESTIÓN DE REVISIÓN"
    )


    for numero, nombre in opciones.items():

        print(
            f"{numero}. {nombre}"
        )


    seleccion = input(

        "\nSeleccione los elementos pendientes "
        "separados por coma: "

    )


    numeros = [

        numero.strip()

        for numero
        in seleccion.split(",")

        if numero.strip()
        in opciones
    ]


    elementos = []


    for numero in numeros:

        elemento = opciones[
            numero
        ]

        if elemento not in elementos:

            elementos.append(
                elemento
            )


    if not elementos:

        print(
            "No se seleccionaron elementos válidos."
        )

        return


    camino, costo = planificar_revision(
        elementos
    )


    print(
        "\nSecuencia sugerida:"
    )


    for numero, elemento in enumerate(
        camino,
        start=1
    ):

        print(
            f"{numero}. {elemento}"
        )


    print(
        f"\nCosto total estimado: "
        f"{costo}"
    )


# ============================================================
# SEMANA 5
# SISTEMA EXPERTO
# ============================================================


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

            "prioridad" in q

            or "urgente" in q

            or "revisar primero" in q

            or "orden de revision" in q,

        "evaluar_prioridad_revision"
    ),
]


# ============================================================
# CARGA DE BASE DE CONOCIMIENTO
# ============================================================


def cargar_base_conocimiento():

    if not KB_FILE.exists():

        raise FileNotFoundError(

            f"No se encontró la base de conocimiento: "
            f"{KB_FILE}"
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

            "La base de conocimiento debe "
            "contener al menos 8 entradas."
        )


    return documentos


# ============================================================
# CARGA DE EJEMPLOS DE CLASIFICACIÓN
# ============================================================


def cargar_datos_clasificacion():

    if not TRAIN_FILE.exists():

        raise FileNotFoundError(

            f"No se encontró el archivo de entrenamiento: "
            f"{TRAIN_FILE}"
        )


    datos = pd.read_csv(
        TRAIN_FILE
    )


    columnas_requeridas = {

        "texto",
        "clase"
    }


    if not columnas_requeridas.issubset(
        datos.columns
    ):

        raise ValueError(

            "El archivo ejemplos_clasificacion.csv "
            "debe contener las columnas "
            "'texto' y 'clase'."
        )


    datos = datos.dropna(
        subset=[
            "texto",
            "clase"
        ]
    )


    textos = (

        datos["texto"]

        .astype(str)

        .tolist()
    )


    clases = (

        datos["clase"]

        .astype(str)

        .tolist()
    )


    if len(textos) < 15:

        raise ValueError(

            "Se requieren al menos "
            "15 ejemplos de clasificación."
        )


    print(

        f"Ejemplos de clasificación cargados: "
        f"{len(textos)}"
    )


    print(

        f"Base de conocimiento cargada: "
        f"{len(cargar_base_conocimiento())} entradas"
    )


    return (
        textos,
        clases
    )


# ============================================================
# SISTEMA HÍBRIDO HIS
# ============================================================


class SistemaHibridoHIS:

    def __init__(self):

        # ----------------------------------------------------
        # BASE DE CONOCIMIENTO
        # ----------------------------------------------------

        self.documentos = (
            cargar_base_conocimiento()
        )


        # Guardamos una versión normalizada
        # para mejorar las comparaciones TF-IDF.

        self.documentos_normalizados = [

            normalizar_texto(
                documento
            )

            for documento
            in self.documentos
        ]


        # ----------------------------------------------------
        # RECUPERACIÓN TF-IDF
        # ----------------------------------------------------

        self.vectorizador_documentos = (
            TfidfVectorizer()
        )


        self.matriz_documentos = (

            self.vectorizador_documentos
            .fit_transform(
                self.documentos_normalizados
            )
        )


        # ----------------------------------------------------
        # CLASIFICADOR DE TEXTO
        # ----------------------------------------------------

        self.clasificador = make_pipeline(

            TfidfVectorizer(),

            LogisticRegression(

                max_iter=1000,

                random_state=RANDOM_STATE
            )
        )


        textos_entrenamiento, clases_entrenamiento = (

            cargar_datos_clasificacion()
        )


        # Normalizamos también los ejemplos
        # utilizados para entrenar.

        textos_entrenamiento_normalizados = [

            normalizar_texto(
                texto
            )

            for texto
            in textos_entrenamiento
        ]


        self.clasificador.fit(

            textos_entrenamiento_normalizados,

            clases_entrenamiento
        )


    # ========================================================
    # ANALIZAR CONSULTA
    # ========================================================

    def analizar_consulta(
        self,
        consulta
    ):

        consulta_normalizada = (
            normalizar_texto(
                consulta
            )
        )


        # ----------------------------------------------------
        # REGLAS EXPERTAS
        # ----------------------------------------------------

        reglas = [

            nombre

            for condicion, nombre
            in REGLAS_EXPERTAS

            if condicion(
                consulta_normalizada
            )
        ]


        # ----------------------------------------------------
        # TF-IDF
        # ----------------------------------------------------

        vector_consulta = (

            self.vectorizador_documentos
            .transform(
                [
                    consulta_normalizada
                ]
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


        # ----------------------------------------------------
        # CLASIFICACIÓN
        # ----------------------------------------------------

        clase = str(

            self.clasificador.predict(
                [
                    consulta_normalizada
                ]
            )[0]
        )


        return {

            "consulta":
                consulta,

            "reglas":
                reglas,

            "evidencia":
                evidencia,

            "similitud":
                similitud,

            "clase":
                clase,
        }


# ============================================================
# MOSTRAR RESULTADO HÍBRIDO
# ============================================================


def mostrar_resultado_hibrido(
    resultado
):

    print(
        "\nRESULTADO HIS_IA"
    )


    print(
        "\nConsulta:"
    )

    print(
        resultado[
            "consulta"
        ]
    )


    print(
        "\nAcción sugerida:"
    )


    if resultado[
        "reglas"
    ]:

        for regla in resultado[
            "reglas"
        ]:

            print(
                f"- {regla}"
            )

    else:

        print(
            "- Sin regla específica"
        )


    print(
        "\nInformación relacionada:"
    )

    print(
        resultado[
            "evidencia"
        ]
    )


    print(

        "\nSimilitud: "
        f"{resultado['similitud']:.3f}"
    )


    print(

        "Categoría: "
        f"{resultado['clase']}"
    )


# ============================================================
# REPORTE SEMANA 5
# ============================================================


def generar_reporte_semana05(
    resultados
):

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    contenido = []

    contenido.append(
        "# Semana 05 - Sistema híbrido HIS_IA"
    )

    contenido.append(
        ""
    )


    contenido.append(
        "## Descripción"
    )

    contenido.append(
        ""
    )


    contenido.append(

        "HIS_IA integra reglas expertas, "
        "recuperación de información mediante TF-IDF, "
        "similitud coseno y clasificación automática "
        "de texto."
    )


    contenido.append(
        ""
    )


    contenido.append(
        f"Base de conocimiento utilizada: "
        f"{len(cargar_base_conocimiento())} entradas."
    )


    textos, clases = (
        cargar_datos_clasificacion()
    )


    contenido.append(
        f"Ejemplos de clasificación utilizados: "
        f"{len(textos)}."
    )


    contenido.append(
        ""
    )


    contenido.append(
        "## Pruebas"
    )


    for indice, resultado in enumerate(
        resultados,
        start=1
    ):

        contenido.append(
            ""
        )

        contenido.append(
            f"### Consulta {indice}"
        )

        contenido.append(
            ""
        )

        contenido.append(
            f"**Consulta:** "
            f"{resultado['consulta']}"
        )

        contenido.append(
            ""
        )


        if resultado[
            "reglas"
        ]:

            reglas = ", ".join(
                resultado[
                    "reglas"
                ]
            )

        else:

            reglas = (
                "Sin regla específica"
            )


        contenido.append(
            f"**Regla activada:** "
            f"{reglas}"
        )

        contenido.append(
            ""
        )


        contenido.append(
            f"**Evidencia recuperada:** "
            f"{resultado['evidencia']}"
        )

        contenido.append(
            ""
        )


        contenido.append(
            f"**Similitud:** "
            f"{resultado['similitud']:.3f}"
        )

        contenido.append(
            ""
        )


        contenido.append(
            f"**Clasificación:** "
            f"{resultado['clase']}"
        )

        contenido.append(
            ""
        )


    contenido.append(
        "## Análisis"
    )

    contenido.append(
        ""
    )


    contenido.append(

        "El sistema híbrido combina conocimiento "
        "definido mediante reglas con recuperación "
        "documental y clasificación automática. "
        "Esto permite ofrecer respuestas trazables."
    )


    contenido.append(
        ""
    )


    contenido.append(
        "## Limitaciones"
    )

    contenido.append(
        ""
    )


    contenido.append(

        "- La base de conocimiento es académica."
    )


    contenido.append(

        "- El conjunto de datos es sintético."
    )


    contenido.append(

        "- HIS_IA no realiza diagnósticos médicos."
    )


    contenido.append(

        "- El sistema no reemplaza la valoración "
        "de profesionales de salud."
    )


    REPORT_SEMANA05.write_text(

        "\n".join(
            contenido
        ),

        encoding="utf-8"
    )


    print(

        f"\nReporte generado en:\n"
        f"{REPORT_SEMANA05}"
    )


# ============================================================
# CONSULTA INTERACTIVA
# ============================================================


def consultar_asistente(
    sistema_hibrido
):

    consulta = input(

        "\nEscriba su consulta: "

    ).strip()


    if not consulta:

        print(
            "La consulta no puede estar vacía."
        )

        return


    resultado = (
        sistema_hibrido
        .analizar_consulta(
            consulta
        )
    )


    mostrar_resultado_hibrido(
        resultado
    )


# ============================================================
# PRUEBAS AUTOMÁTICAS SEMANA 5
# ============================================================


def ejecutar_pruebas_semana05(
    sistema_hibrido
):

    consultas = [

        (
            "Tengo pendiente revisar el resultado "
            "de creatinina del paciente"
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

        (
            "Necesito revisar los medicamentos "
            "registrados del paciente"
        ),

        (
            "Necesito determinar qué información "
            "debo revisar primero"
        ),
    ]


    resultados = []


    print(
        "\nVALIDACIÓN DEL SISTEMA HÍBRIDO"
    )


    for consulta in consultas:

        resultado = (
            sistema_hibrido
            .analizar_consulta(
                consulta
            )
        )


        resultados.append(
            resultado
        )


        mostrar_resultado_hibrido(
            resultado
        )


    generar_reporte_semana05(
        resultados
    )


# ============================================================
# MENÚ
# ============================================================


def mostrar_menu():

    print(
        "\n"
        + "=" * 55
    )

    print(
        "HIS_IA - ASISTENTE INTELIGENTE"
    )

    print(
        "=" * 55
    )

    print(
        "1. Analizar información clínica"
    )

    print(
        "2. Evaluar prioridad de revisión"
    )

    print(
        "3. Gestionar revisión de resultados y estudios"
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


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================


def main():

    try:

        modelo_prioridad = (
            entrenar_modelo_prioridad()
        )

    except Exception as error:

        print(
            "\nError cargando "
            "el modelo de prioridad:"
        )

        print(
            error
        )

        return


    try:

        sistema_hibrido = (
            SistemaHibridoHIS()
        )

        print(
            "\nSistema híbrido cargado correctamente."
        )

    except Exception as error:

        print(
            "\nError cargando "
            "el sistema híbrido:"
        )

        print(
            error
        )

        sistema_hibrido = None


    while True:

        mostrar_menu()


        opcion = input(
            "\nSeleccione una opción: "
        ).strip()


        if opcion == "1":

            texto = input(

                "\nIngrese la información "
                "que desea analizar:\n"
            )


            principal, detectadas, puntuaciones = (
                clasificar_texto(
                    texto
                )
            )


            print(
                f"\nCategoría principal: "
                f"{principal}"
            )


            print(
                "\nCategorías detectadas:"
            )


            if detectadas:

                for categoria in detectadas:

                    print(
                        f"- {categoria}"
                    )

            else:

                print(
                    "- Ninguna"
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
                    "\nEl asistente no está disponible."
                )

            else:

                consultar_asistente(
                    sistema_hibrido
                )


        elif opcion == "5":

            if sistema_hibrido is None:

                print(
                    "\nEl sistema híbrido "
                    "no está disponible."
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


# ============================================================
# EJECUCIÓN
# ============================================================


if __name__ == "__main__":

    main()