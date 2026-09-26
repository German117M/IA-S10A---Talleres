from pathlib import Path
import heapq
import itertools
import re
import sys
import unicodedata

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==========================================================
# CONFIGURACIÓN GENERAL
# ==========================================================

VERSION = "1.4"
RANDOM_STATE = 42

ROOT = Path(__file__).resolve().parent.parent

# /ia_semestre/
PROJECT_ROOT = ROOT.parent

DATA_FILE = ROOT / "data" / "datos_his.csv"
KB_FILE = ROOT / "data" / "base_conocimiento.txt"
TRAIN_FILE = ROOT / "data" / "ejemplos_clasificacion.csv"

REPORTS_DIR = ROOT / "reports"
REPORT_SEMANA05 = REPORTS_DIR / "semana05.md"


# ==========================================================
# SEMANA 8
# CARGAR MÓDULO EXTERNO
# ==========================================================

SEMANA8_SRC = PROJECT_ROOT / "src"

if str(SEMANA8_SRC) not in sys.path:
    sys.path.insert(
        0,
        str(SEMANA8_SRC)
    )


try:
    from semana08_red_ontologia import (
        SistemaReconocimientoSemana8
    )

    SEMANA8_DISPONIBLE = True
    SEMANA8_ERROR = None

except Exception as error:

    SistemaReconocimientoSemana8 = None

    SEMANA8_DISPONIBLE = False

    SEMANA8_ERROR = str(
        error
    )


_SISTEMA_SEMANA8 = None


# ==========================================================
# UTILIDADES
# ==========================================================

def normalizar_texto(texto):
    texto = str(
        texto
    ).lower().strip()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(
            caracter
        ) != "Mn"
    )

    texto = re.sub(
        r"[^a-z0-9\s]",
        " ",
        texto
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


def valor_booleano(valor):
    if isinstance(
        valor,
        bool
    ):
        return valor

    if isinstance(
        valor,
        int
    ):
        return valor == 1

    texto = normalizar_texto(
        str(
            valor
        )
    )

    return texto in {
        "si",
        "s",
        "1",
        "true",
        "verdadero",
        "activo"
    }


def solicitar_criterio(nombre):
    while True:

        respuesta = input(
            f"{nombre} (s/n): "
        ).strip().lower()

        if respuesta in {
            "s",
            "si",
            "sí"
        }:
            return True

        if respuesta in {
            "n",
            "no"
        }:
            return False

        print(
            "Respuesta no válida. Ingrese s o n."
        )


# ==========================================================
# SEMANA 2
# MACHINE LEARNING
# ==========================================================

VARIABLES_PRIORIDAD = [
    "edad",
    "documentos_pendientes",
    "resultados_pendientes",
    "imagenes_pendientes",
]


def cargar_datos_prioridad():
    if not DATA_FILE.exists():

        raise FileNotFoundError(
            f"No se encontró el archivo: {DATA_FILE}"
        )

    datos = pd.read_csv(
        DATA_FILE
    )

    columnas_requeridas = (
        VARIABLES_PRIORIDAD
        + ["prioridad"]
    )

    faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in datos.columns
    ]

    if faltantes:

        raise ValueError(
            "Faltan columnas en datos_his.csv: "
            + ", ".join(
                faltantes
            )
        )

    return datos[
        columnas_requeridas
    ].dropna()


def entrenar_modelo_prioridad():
    datos = cargar_datos_prioridad()

    X = datos[
        VARIABLES_PRIORIDAD
    ]

    y = datos[
        "prioridad"
    ]

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
        stratify=y
    )

    modelo = Pipeline(
        [
            (
                "scaler",
                StandardScaler()
            ),
            (
                "modelo",
                LogisticRegression(
                    max_iter=1000,
                    random_state=RANDOM_STATE
                )
            )
        ]
    )

    modelo.fit(
        X_train,
        y_train
    )

    predicciones = modelo.predict(
        X_test
    )

    precision = accuracy_score(
        y_test,
        predicciones
    )

    matriz = confusion_matrix(
        y_test,
        predicciones
    )

    print(
        "Modelo de prioridad cargado."
    )

    print(
        f"Precisión de validación: {precision:.3f}"
    )

    print(
        "Matriz de validación:"
    )

    print(
        matriz
    )

    return (
        modelo,
        precision,
        matriz
    )


def evaluar_prioridad(
    modelo,
    edad,
    documentos,
    resultados,
    imagenes
):
    entrada = pd.DataFrame(
        [
            [
                edad,
                documentos,
                resultados,
                imagenes
            ]
        ],
        columns=VARIABLES_PRIORIDAD
    )

    prediccion = modelo.predict(
        entrada
    )[0]

    if int(
        prediccion
    ) == 1:

        return "Prioritaria"

    return "Normal"


# ==========================================================
# SEMANA 3
# CLASIFICACIÓN
# ==========================================================

PALABRAS_CLAVE = {

    "Historia clínica": [
        "historia",
        "antecedente",
        "antecedentes",
        "evolucion",
        "consulta",
        "diagnostico",
        "paciente"
    ],

    "Laboratorio clínico": [
        "laboratorio",
        "hemograma",
        "creatinina",
        "glucosa",
        "troponina",
        "resultado",
        "resultados",
        "muestra"
    ],

    "Imagen diagnóstica": [
        "radiografia",
        "tomografia",
        "resonancia",
        "ecografia",
        "imagen",
        "imagenes",
        "estudio"
    ],

    "Medicamentos": [
        "medicamento",
        "medicamentos",
        "dosis",
        "tratamiento",
        "prescripcion",
        "farmaco"
    ]
}


def clasificar_texto(texto):

    texto_normalizado = normalizar_texto(
        texto
    )

    resultados = {}

    for categoria, palabras in (
        PALABRAS_CLAVE.items()
    ):

        coincidencias = sum(
            1
            for palabra in palabras
            if palabra in texto_normalizado
        )

        resultados[
            categoria
        ] = coincidencias

    categorias_detectadas = [
        categoria
        for categoria, cantidad
        in resultados.items()
        if cantidad > 0
    ]

    if not categorias_detectadas:

        return {
            "principal":
                "No identificada",

            "categorias":
                [],

            "texto_normalizado":
                texto_normalizado
        }

    principal = max(
        resultados,
        key=resultados.get
    )

    return {
        "principal":
            principal,

        "categorias":
            categorias_detectadas,

        "texto_normalizado":
            texto_normalizado
    }


# ==========================================================
# SEMANA 4
# A*
# ==========================================================

COSTOS_REVISION = {

    "Historia clínica": {
        "procesamiento": 1,
        "espera": 1
    },

    "Resultados de laboratorio": {
        "procesamiento": 2,
        "espera": 3
    },

    "Estudio de imagen": {
        "procesamiento": 3,
        "espera": 3
    },

    "Medicamentos": {
        "procesamiento": 2,
        "espera": 2
    }
}


def heuristica_revision(
    pendientes
):
    return sum(
        COSTOS_REVISION[
            elemento
        ]["procesamiento"]

        for elemento
        in pendientes
    )


def costo_transicion(
    seleccionado,
    restantes
):

    procesamiento = (
        COSTOS_REVISION[
            seleccionado
        ]["procesamiento"]
    )

    espera = sum(
        COSTOS_REVISION[
            elemento
        ]["espera"]

        for elemento
        in restantes
    )

    return (
        procesamiento
        + espera
    )


def planificar_revision(
    elementos
):

    elementos = list(
        dict.fromkeys(
            elementos
        )
    )

    invalidos = [
        elemento
        for elemento in elementos
        if elemento not in COSTOS_REVISION
    ]

    if invalidos:

        raise ValueError(
            "Elementos no reconocidos: "
            + ", ".join(
                invalidos
            )
        )

    if not elementos:

        return {
            "orden": [],
            "costo_total": 0
        }

    estado_inicial = tuple(
        elementos
    )

    contador = itertools.count()

    cola = []

    heapq.heappush(
        cola,
        (
            heuristica_revision(
                estado_inicial
            ),
            0,
            next(
                contador
            ),
            estado_inicial,
            []
        )
    )

    mejor_costo = {
        estado_inicial: 0
    }

    while cola:

        (
            _,
            costo_actual,
            _,
            pendientes,
            camino
        ) = heapq.heappop(
            cola
        )

        if not pendientes:

            return {
                "orden":
                    camino,

                "costo_total":
                    costo_actual
            }

        for seleccionado in pendientes:

            restantes = tuple(
                elemento
                for elemento in pendientes
                if elemento != seleccionado
            )

            nuevo_costo = (
                costo_actual
                + costo_transicion(
                    seleccionado,
                    restantes
                )
            )

            if (
                restantes not in mejor_costo
                or nuevo_costo
                < mejor_costo[
                    restantes
                ]
            ):

                mejor_costo[
                    restantes
                ] = nuevo_costo

                f = (
                    nuevo_costo
                    + heuristica_revision(
                        restantes
                    )
                )

                heapq.heappush(
                    cola,
                    (
                        f,
                        nuevo_costo,
                        next(
                            contador
                        ),
                        restantes,
                        camino
                        + [seleccionado]
                    )
                )

    raise RuntimeError(
        "No fue posible encontrar una secuencia."
    )


# ==========================================================
# SEMANA 4
# MINIMAX
# ==========================================================

CRITERIOS_PRIORIZACION = {

    "dolor_intenso": {
        "gravedad": 1,
        "impacto": 4
    },

    "dificultad_respiratoria": {
        "gravedad": 10,
        "impacto": 6
    },

    "sangrado_activo": {
        "gravedad": 8,
        "impacto": 4
    },

    "perdida_movilidad": {
        "gravedad": 2,
        "impacto": 7
    },

    "alteracion_conciencia": {
        "gravedad": 10,
        "impacto": 7
    },

    "trauma": {
        "gravedad": 3,
        "impacto": 6
    },

    "requiere_soporte": {
        "gravedad": 9,
        "impacto": 8
    }
}


def calcular_dimension_paciente(
    paciente,
    dimension
):

    total = 0

    for criterio, pesos in (
        CRITERIOS_PRIORIZACION.items()
    ):

        if valor_booleano(
            paciente.get(
                criterio,
                False
            )
        ):

            total += pesos[
                dimension
            ]

    return total


def minimax(
    nodo,
    maximizando=True
):

    if isinstance(
        nodo,
        (int, float)
    ):

        return nodo

    valores = [
        minimax(
            hijo,
            not maximizando
        )

        for hijo
        in nodo
    ]

    if maximizando:

        return max(
            valores
        )

    return min(
        valores
    )


def evaluar_paciente_minimax(
    paciente
):

    gravedad = (
        calcular_dimension_paciente(
            paciente,
            "gravedad"
        )
    )

    impacto = (
        calcular_dimension_paciente(
            paciente,
            "impacto"
        )
    )

    valor_minimax = minimax(
        [
            gravedad,
            impacto
        ],
        False
    )

    return {
        "motivo_consulta":
            paciente.get(
                "motivo_consulta",
                "No especificado"
            ),

        "gravedad":
            gravedad,

        "impacto":
            impacto,

        "valor_minimax":
            valor_minimax
    }


def priorizar_pacientes_minimax(
    paciente1,
    paciente2
):

    evaluacion1 = (
        evaluar_paciente_minimax(
            paciente1
        )
    )

    evaluacion2 = (
        evaluar_paciente_minimax(
            paciente2
        )
    )

    arbol = [
        [
            evaluacion1[
                "gravedad"
            ],
            evaluacion1[
                "impacto"
            ]
        ],
        [
            evaluacion2[
                "gravedad"
            ],
            evaluacion2[
                "impacto"
            ]
        ]
    ]

    valor_paciente1 = minimax(
        arbol[0],
        False
    )

    valor_paciente2 = minimax(
        arbol[1],
        False
    )

    valor_global = minimax(
        arbol,
        True
    )

    if (
        valor_paciente1
        > valor_paciente2
    ):

        prioritario = (
            "Paciente 1"
        )

    elif (
        valor_paciente2
        > valor_paciente1
    ):

        prioritario = (
            "Paciente 2"
        )

    else:

        prioritario = (
            "Prioridad equivalente"
        )

    return {
        "paciente_prioritario":
            prioritario,

        "valor_minimax":
            valor_global,

        "paciente1":
            evaluacion1,

        "paciente2":
            evaluacion2
    }


# ==========================================================
# SEMANA 5
# SISTEMA HÍBRIDO
# ==========================================================

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
    )
]


def cargar_base_conocimiento():

    if not KB_FILE.exists():

        raise FileNotFoundError(
            f"No se encontró: {KB_FILE}"
        )

    documentos = [
        linea.strip()

        for linea in (
            KB_FILE
            .read_text(
                encoding="utf-8"
            )
            .splitlines()
        )

        if linea.strip()
    ]

    if len(
        documentos
    ) < 8:

        raise ValueError(
            "La base de conocimiento debe "
            "contener mínimo 8 entradas."
        )

    return documentos


def cargar_datos_clasificacion():

    if not TRAIN_FILE.exists():

        raise FileNotFoundError(
            f"No se encontró: {TRAIN_FILE}"
        )

    datos = pd.read_csv(
        TRAIN_FILE
    )

    requeridas = {
        "texto",
        "clase"
    }

    if not requeridas.issubset(
        datos.columns
    ):

        raise ValueError(
            "ejemplos_clasificacion.csv debe "
            "contener texto y clase."
        )

    datos = datos[
        [
            "texto",
            "clase"
        ]
    ].dropna()

    textos = (
        datos[
            "texto"
        ]
        .astype(
            str
        )
        .tolist()
    )

    clases = (
        datos[
            "clase"
        ]
        .astype(
            str
        )
        .tolist()
    )

    print(
        "Ejemplos de clasificación cargados: "
        f"{len(textos)}"
    )

    return (
        textos,
        clases
    )


class SistemaHibridoHIS:

    def __init__(self):

        self.documentos = (
            cargar_base_conocimiento()
        )

        documentos_normalizados = [
            normalizar_texto(
                documento
            )

            for documento
            in self.documentos
        ]

        self.vectorizador_documentos = (
            TfidfVectorizer()
        )

        self.matriz_documentos = (
            self.vectorizador_documentos
            .fit_transform(
                documentos_normalizados
            )
        )

        textos, clases = (
            cargar_datos_clasificacion()
        )

        textos_normalizados = [
            normalizar_texto(
                texto
            )

            for texto
            in textos
        ]

        self.clasificador = Pipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer()
                ),
                (
                    "modelo",
                    LogisticRegression(
                        max_iter=1000,
                        random_state=RANDOM_STATE
                    )
                )
            ]
        )

        self.clasificador.fit(
            textos_normalizados,
            clases
        )

        print(
            "Sistema híbrido HIS_IA cargado."
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
            self.vectorizador_documentos
            .transform(
                [
                    consulta_normalizada
                ]
            )
        )

        similitudes = (
            cosine_similarity(
                vector_consulta,
                self.matriz_documentos
            )[0]
        )

        mejor_indice = int(
            similitudes.argmax()
        )

        evidencia = self.documentos[
            mejor_indice
        ]

        similitud = float(
            similitudes[
                mejor_indice
            ]
        )

        clase = str(
            self.clasificador
            .predict(
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
                clase
        }


# ==========================================================
# VALIDACIÓN SEMANA 5
# ==========================================================

def generar_reporte_semana5(
    resultados
):

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    lineas = [

        "# Semana 5 - Sistema híbrido HIS_IA",
        "",
        "## Validación de funcionamiento",
        "",
        (
            "Se realizaron consultas de prueba sobre "
            "laboratorio, imágenes, historia clínica, "
            "medicamentos y prioridad de revisión."
        ),
        ""
    ]

    for indice, resultado in enumerate(
        resultados,
        start=1
    ):

        reglas = (
            ", ".join(
                resultado[
                    "reglas"
                ]
            )

            if resultado[
                "reglas"
            ]

            else (
                "Sin regla específica"
            )
        )

        lineas.extend(
            [
                f"### Consulta {indice}",
                "",
                (
                    f"**Consulta:** "
                    f"{resultado['consulta']}"
                ),
                "",
                (
                    f"**Categoría:** "
                    f"{resultado['clase']}"
                ),
                "",
                (
                    f"**Acciones sugeridas:** "
                    f"{reglas}"
                ),
                "",
                (
                    "**Información relacionada:** "
                    f"{resultado['evidencia']}"
                ),
                "",
                (
                    "**Similitud:** "
                    f"{resultado['similitud']:.3f}"
                ),
                ""
            ]
        )

    REPORT_SEMANA05.write_text(
        "\n".join(
            lineas
        ),
        encoding="utf-8"
    )


def validar_funcionamiento_semana5(
    sistema_hibrido
):

    consultas = [

        (
            "Necesito revisar el resultado "
            "de creatinina del paciente."
        ),

        (
            "Hay una resonancia pendiente "
            "de revisión."
        ),

        (
            "Se requiere consultar los antecedentes "
            "y evolución de la historia clínica."
        ),

        (
            "El paciente tiene medicamentos "
            "y tratamiento registrados."
        ),

        (
            "¿Qué información debería "
            "revisar primero?"
        )
    ]

    resultados = []

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

        print(
            "\n"
            + "=" * 60
        )

        print(
            f"Consulta: {consulta}"
        )

        print(
            "\nResultado HIS_IA"
        )

        print(
            "Categoría:",
            resultado[
                "clase"
            ]
        )

        acciones = (
            ", ".join(
                resultado[
                    "reglas"
                ]
            )

            if resultado[
                "reglas"
            ]

            else (
                "Sin regla específica"
            )
        )

        print(
            "Acciones sugeridas:",
            acciones
        )

        print(
            "Información relacionada:",
            resultado[
                "evidencia"
            ]
        )

        print(
            "Similitud:",
            round(
                resultado[
                    "similitud"
                ],
                3
            )
        )

    generar_reporte_semana5(
        resultados
    )

    print(
        "\nReporte generado en:"
    )

    print(
        REPORT_SEMANA05
    )


# ==========================================================
# SEMANA 7
# REFERENCIAS
# ==========================================================

REFERENCIAS_SEMANA7 = {

    "temperatura": {
        "min": 36,
        "max": 37.5,
        "unidad": "°C",
        "descripcion": "Normal"
    },

    "latidos": {
        "min": 72,
        "max": 84,
        "unidad": "lpm",
        "descripcion": "Normal"
    },

    "presion": {
        "min": 120,
        "max": 129,
        "unidad": "mmHg",
        "descripcion": "Normal"
    }
}


# ==========================================================
# SEMANA 7
# CLASIFICACIONES
# ==========================================================

def clasificar_temperatura(
    temperatura
):

    temperatura = float(
        temperatura
    )

    if temperatura < 35:

        return "Hipotermia"

    elif (
        36
        <= temperatura
        < 37.5
    ):

        return "Normal"

    elif (
        37.5
        <= temperatura
        < 39.5
    ):

        return "Fiebre"

    elif (
        39.5
        <= temperatura
        < 41
    ):

        return "Fiebre alta"

    elif temperatura >= 41:

        return "Hipertermia"

    return (
        "No clasificada según "
        "los rangos definidos"
    )


def clasificar_latidos(
    latidos
):

    latidos = int(
        latidos
    )

    if latidos <= 62:

        return "Excelente"

    elif (
        64
        <= latidos
        <= 70
    ):

        return "Bueno"

    elif (
        72
        <= latidos
        <= 84
    ):

        return "Normal"

    elif latidos >= 86:

        return "Inadecuado"

    return (
        "No clasificado según "
        "los rangos definidos"
    )


def clasificar_presion(
    presion
):

    presion = int(
        presion
    )

    if presion < 120:

        return "Óptima"

    elif (
        120
        <= presion
        <= 129
    ):

        return "Normal"

    elif (
        130
        <= presion
        <= 139
    ):

        return "Presión fronteriza"

    elif (
        140
        <= presion
        <= 159
    ):

        return "Hipertensión nivel 1"

    elif (
        160
        <= presion
        <= 179
    ):

        return "Hipertensión nivel 2"

    elif presion > 180:

        return "Hipertensión nivel 3"

    return (
        "No clasificada según "
        "los rangos definidos"
    )


# ==========================================================
# SEMANA 7
# REPRESENTACIÓN NUMÉRICA
# ==========================================================

def representacion_numerica(
    caso
):

    temperatura = float(
        caso.get(
            "temperatura"
        )
    )

    latidos = int(
        caso.get(
            "latidos"
        )
    )

    presion = int(
        caso.get(
            "presion"
        )
    )

    vector = np.array(
        [
            temperatura,
            latidos,
            presion
        ],
        dtype=float
    )

    return {
        "vector":
            vector.tolist(),

        "temperatura":
            temperatura,

        "latidos":
            latidos,

        "presion":
            presion,

        "referencias":
            REFERENCIAS_SEMANA7
    }


# ==========================================================
# SEMANA 7
# REPRESENTACIÓN SIMBÓLICA
# ==========================================================

def representacion_simbolica(
    caso
):

    temperatura = float(
        caso.get(
            "temperatura"
        )
    )

    latidos = int(
        caso.get(
            "latidos"
        )
    )

    presion = int(
        caso.get(
            "presion"
        )
    )

    estado_temperatura = (
        clasificar_temperatura(
            temperatura
        )
    )

    estado_latidos = (
        clasificar_latidos(
            latidos
        )
    )

    estado_presion = (
        clasificar_presion(
            presion
        )
    )

    hechos = {
        "temperatura":
            estado_temperatura,

        "latidos":
            estado_latidos,

        "presion":
            estado_presion
    }

    conclusiones = [
        (
            "Temperatura: "
            + estado_temperatura
        ),
        (
            "Frecuencia cardíaca: "
            + estado_latidos
        ),
        (
            "Presión arterial: "
            + estado_presion
        )
    ]

    return {
        "hechos":
            hechos,

        "conclusiones":
            conclusiones
    }


# ==========================================================
# SEMANA 7
# RESULTADO INTEGRADO
# ==========================================================

def generar_resultado_integrado(
    simbolica
):

    hechos = simbolica[
        "hechos"
    ]

    temperatura = hechos[
        "temperatura"
    ]

    latidos = hechos[
        "latidos"
    ]

    presion = hechos[
        "presion"
    ]

    temperatura_esperada = {
        "Normal"
    }

    latidos_esperados = {
        "Excelente",
        "Bueno",
        "Normal"
    }

    presion_esperada = {
        "Óptima",
        "Normal"
    }

    variables_en_categoria_esperada = 0

    hallazgos = []

    detalles = []


    if temperatura in temperatura_esperada:

        variables_en_categoria_esperada += 1

        detalles.append(
            (
                "Temperatura: "
                + temperatura
                + " - categoría esperada."
            )
        )

    else:

        hallazgos.append(
            "Temperatura: "
            + temperatura
        )

        detalles.append(
            (
                "Temperatura: "
                + temperatura
                + " - clasificación diferente "
                "de la categoría esperada."
            )
        )


    if latidos in latidos_esperados:

        variables_en_categoria_esperada += 1

        detalles.append(
            (
                "Frecuencia cardíaca: "
                + latidos
                + " - categoría esperada."
            )
        )

    else:

        hallazgos.append(
            (
                "Frecuencia cardíaca: "
                + latidos
            )
        )

        detalles.append(
            (
                "Frecuencia cardíaca: "
                + latidos
                + " - clasificación diferente "
                "de las categorías esperadas."
            )
        )


    if presion in presion_esperada:

        variables_en_categoria_esperada += 1

        detalles.append(
            (
                "Presión arterial: "
                + presion
                + " - categoría esperada."
            )
        )

    else:

        hallazgos.append(
            (
                "Presión arterial: "
                + presion
            )
        )

        detalles.append(
            (
                "Presión arterial: "
                + presion
                + " - clasificación diferente "
                "de las categorías esperadas."
            )
        )


    variables_evaluadas = 3

    variables_con_hallazgos = len(
        hallazgos
    )


    if variables_con_hallazgos == 0:

        conclusion = (
            "Las tres variables evaluadas se encuentran "
            "dentro de las categorías esperadas definidas "
            "para el proyecto."
        )

    elif variables_con_hallazgos == 1:

        conclusion = (
            "Se identificó 1 variable con una clasificación "
            "diferente de las categorías esperadas definidas "
            "para el proyecto."
        )

    else:

        conclusion = (
            f"Se identificaron {variables_con_hallazgos} "
            "variables con clasificaciones diferentes de "
            "las categorías esperadas definidas para "
            "el proyecto."
        )


    return {
        "variables_evaluadas":
            variables_evaluadas,

        "variables_en_categoria_esperada":
            variables_en_categoria_esperada,

        "variables_con_hallazgos":
            variables_con_hallazgos,

        "hallazgos":
            hallazgos,

        "detalles":
            detalles,

        "conclusion":
            conclusion
    }


# ==========================================================
# SEMANA 7
# AUTÓMATA
# ==========================================================

def automata_consulta_paciente(
    caso
):

    secuencia = ""

    if caso.get(
        "temperatura"
    ) is not None:

        secuencia += "T"

    if caso.get(
        "latidos"
    ) is not None:

        secuencia += "L"

    if caso.get(
        "presion"
    ) is not None:

        secuencia += "P"

    estado = "q0"

    transiciones = {

        (
            "q0",
            "T"
        ):
            "q1",

        (
            "q1",
            "L"
        ):
            "q2",

        (
            "q2",
            "P"
        ):
            "q3"
    }

    recorrido = [
        estado
    ]

    for simbolo in secuencia:

        transicion = (
            estado,
            simbolo
        )

        if transicion not in transiciones:

            return {
                "secuencia":
                    secuencia,

                "estado_final":
                    estado,

                "aceptada":
                    False,

                "recorrido":
                    recorrido,

                "mensaje":
                    "La secuencia de datos no es válida."
            }

        estado = transiciones[
            transicion
        ]

        recorrido.append(
            estado
        )

    aceptada = (
        estado == "q3"
    )

    if aceptada:

        mensaje = (
            "Consulta completa: temperatura, "
            "latidos y presión fueron procesados."
        )

    else:

        mensaje = (
            "La consulta está incompleta."
        )

    return {
        "secuencia":
            secuencia,

        "estado_final":
            estado,

        "aceptada":
            aceptada,

        "recorrido":
            recorrido,

        "mensaje":
            mensaje
    }


# ==========================================================
# SEMANA 7
# INTEGRACIÓN
# ==========================================================

def analizar_representaciones(
    caso
):

    numerica = (
        representacion_numerica(
            caso
        )
    )

    simbolica = (
        representacion_simbolica(
            caso
        )
    )

    automata = (
        automata_consulta_paciente(
            caso
        )
    )

    resultado_integrado = (
        generar_resultado_integrado(
            simbolica
        )
    )

    return {
        "motivo_consulta":
            caso.get(
                "motivo_consulta",
                "No especificado"
            ),

        "representacion_numerica":
            numerica,

        "representacion_simbolica":
            simbolica,

        "automata":
            automata,

        "resultado_integrado":
            resultado_integrado
    }


# ==========================================================
# SEMANA 8
# INTEGRACIÓN HIS_IA
# ==========================================================

def obtener_sistema_semana8():
    global _SISTEMA_SEMANA8

    if not SEMANA8_DISPONIBLE:

        raise RuntimeError(
            (
                "Semana 8 no está disponible. "
                f"Detalle: {SEMANA8_ERROR}"
            )
        )

    if _SISTEMA_SEMANA8 is None:

        _SISTEMA_SEMANA8 = (
            SistemaReconocimientoSemana8()
        )

        _SISTEMA_SEMANA8.inicializar()

    return _SISTEMA_SEMANA8


def analizar_archivo_semana8(
    ruta_archivo
):

    ruta = Path(
        ruta_archivo
    )

    if not ruta.exists():

        raise FileNotFoundError(
            f"No existe el archivo: {ruta}"
        )

    extension = (
        ruta.suffix.lower()
    )

    sistema = (
        obtener_sistema_semana8()
    )

    if extension == ".pdf":

        resultado = (
            sistema.procesar_pdf(
                ruta
            )
        )

        return {
            "tipo":
                "pdf",

            "resultado":
                resultado
        }

    if extension in {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp"
    }:

        resultado = (
            sistema.procesar_imagen(
                ruta
            )
        )

        return {
            "tipo":
                "imagen",

            "resultado":
                resultado
        }

    raise ValueError(
        (
            "Formato no permitido. "
            "Use PDF, PNG, JPG, JPEG o WEBP."
        )
    )


def obtener_resumen_semana8():

    sistema = (
        obtener_sistema_semana8()
    )

    return {
        "evidencia":
            sistema.base.resumen(),

        "ontologia":
            sistema.ontologia.resumen(),

        "accuracy":
            sistema.mlp.accuracy
    }


# ==========================================================
# CONSOLA A*
# ==========================================================

def gestionar_astar():

    print(
        "\nORGANIZAR REVISIÓN CON A*"
    )

    elementos = []

    for elemento in COSTOS_REVISION:

        if solicitar_criterio(
            f"Incluir {elemento}"
        ):

            elementos.append(
                elemento
            )

    if not elementos:

        print(
            "No se seleccionaron elementos."
        )

        return

    resultado = planificar_revision(
        elementos
    )

    print(
        "\nOrden sugerido:"
    )

    for indice, elemento in enumerate(
        resultado[
            "orden"
        ],
        start=1
    ):

        print(
            f"{indice}. {elemento}"
        )

    print(
        "Costo total:",
        resultado[
            "costo_total"
        ]
    )


# ==========================================================
# CONSOLA MINIMAX
# ==========================================================

def ingresar_paciente_minimax(
    numero
):

    print(
        f"\nPACIENTE {numero}"
    )

    motivo = input(
        "Motivo de consulta: "
    ).strip()

    return {

        "motivo_consulta":
            motivo,

        "dolor_intenso":
            solicitar_criterio(
                "Dolor intenso"
            ),

        "dificultad_respiratoria":
            solicitar_criterio(
                "Dificultad respiratoria"
            ),

        "sangrado_activo":
            solicitar_criterio(
                "Sangrado activo"
            ),

        "perdida_movilidad":
            solicitar_criterio(
                "Pérdida de movilidad"
            ),

        "alteracion_conciencia":
            solicitar_criterio(
                "Alteración de conciencia"
            ),

        "trauma":
            solicitar_criterio(
                "Trauma"
            ),

        "requiere_soporte":
            solicitar_criterio(
                "Requiere soporte"
            )
    }


def gestionar_minimax():

    paciente1 = (
        ingresar_paciente_minimax(
            1
        )
    )

    paciente2 = (
        ingresar_paciente_minimax(
            2
        )
    )

    resultado = (
        priorizar_pacientes_minimax(
            paciente1,
            paciente2
        )
    )

    print(
        "\nRESULTADO MINIMAX"
    )

    print(
        "Paciente prioritario:",
        resultado[
            "paciente_prioritario"
        ]
    )

    print(
        "\nPaciente 1:"
    )

    print(
        "Gravedad:",
        resultado[
            "paciente1"
        ]["gravedad"]
    )

    print(
        "Impacto:",
        resultado[
            "paciente1"
        ]["impacto"]
    )

    print(
        "Valor Minimax:",
        resultado[
            "paciente1"
        ]["valor_minimax"]
    )

    print(
        "\nPaciente 2:"
    )

    print(
        "Gravedad:",
        resultado[
            "paciente2"
        ]["gravedad"]
    )

    print(
        "Impacto:",
        resultado[
            "paciente2"
        ]["impacto"]
    )

    print(
        "Valor Minimax:",
        resultado[
            "paciente2"
        ]["valor_minimax"]
    )


# ==========================================================
# CONSOLA SEMANA 7
# ==========================================================

def ingresar_caso_reconocimiento():

    print(
        "\nRECONOCIMIENTO DEL CASO"
    )

    print(
        "=" * 45
    )

    motivo = input(
        "Motivo de consulta: "
    ).strip()


    while True:

        try:

            temperatura = float(
                input(
                    "Temperatura del paciente °C: "
                )
            )

            break

        except ValueError:

            print(
                "Ingrese una temperatura válida."
            )


    while True:

        try:

            latidos = int(
                input(
                    "Latidos por minuto: "
                )
            )

            break

        except ValueError:

            print(
                "Ingrese una cantidad de latidos válida."
            )


    while True:

        try:

            presion = int(
                input(
                    "Presión arterial: "
                )
            )

            break

        except ValueError:

            print(
                "Ingrese un valor de presión válido."
            )


    return {
        "motivo_consulta":
            motivo,

        "temperatura":
            temperatura,

        "latidos":
            latidos,

        "presion":
            presion
    }


def gestionar_reconocimiento():

    caso = (
        ingresar_caso_reconocimiento()
    )

    resultado = (
        analizar_representaciones(
            caso
        )
    )

    print(
        "\n"
        + "=" * 55
    )

    print(
        "RESULTADO SEMANA 7"
    )

    print(
        "=" * 55
    )

    print(
        "\nMotivo:",
        resultado[
            "motivo_consulta"
        ]
    )


    numerica = resultado[
        "representacion_numerica"
    ]

    referencias = numerica[
        "referencias"
    ]

    print(
        "\n1. REPRESENTACIÓN NUMÉRICA"
    )

    print(
        "Vector del paciente:",
        numerica[
            "vector"
        ]
    )

    print(
        "\nValores del paciente:"
    )

    print(
        "Temperatura:",
        numerica[
            "temperatura"
        ],
        "°C"
    )

    print(
        "Latidos:",
        numerica[
            "latidos"
        ],
        "lpm"
    )

    print(
        "Presión:",
        numerica[
            "presion"
        ],
        "mmHg"
    )

    print(
        "\nReferencias:"
    )

    print(
        "Temperatura normal:",
        referencias[
            "temperatura"
        ]["min"],
        "-",
        referencias[
            "temperatura"
        ]["max"],
        referencias[
            "temperatura"
        ]["unidad"]
    )

    print(
        "Frecuencia cardíaca normal:",
        referencias[
            "latidos"
        ]["min"],
        "-",
        referencias[
            "latidos"
        ]["max"],
        referencias[
            "latidos"
        ]["unidad"]
    )

    print(
        "Presión arterial normal:",
        referencias[
            "presion"
        ]["min"],
        "-",
        referencias[
            "presion"
        ]["max"],
        referencias[
            "presion"
        ]["unidad"]
    )


    simbolica = resultado[
        "representacion_simbolica"
    ]

    print(
        "\n2. REPRESENTACIÓN SIMBÓLICA"
    )

    print(
        "Temperatura:",
        simbolica[
            "hechos"
        ]["temperatura"]
    )

    print(
        "Frecuencia cardíaca:",
        simbolica[
            "hechos"
        ]["latidos"]
    )

    print(
        "Presión arterial:",
        simbolica[
            "hechos"
        ]["presion"]
    )


    automata = resultado[
        "automata"
    ]

    print(
        "\n3. AUTÓMATA"
    )

    print(
        "Secuencia:",
        automata[
            "secuencia"
        ]
    )

    print(
        "Estado final:",
        automata[
            "estado_final"
        ]
    )

    print(
        "Consulta procesada:",
        (
            "Sí"
            if automata[
                "aceptada"
            ]
            else "No"
        )
    )

    print(
        "Recorrido:",
        " -> ".join(
            automata[
                "recorrido"
            ]
        )
    )

    print(
        "Resultado:",
        automata[
            "mensaje"
        ]
    )


    integrado = resultado[
        "resultado_integrado"
    ]

    print(
        "\n4. RESULTADO INTEGRADO"
    )

    print(
        "Variables evaluadas:",
        integrado[
            "variables_evaluadas"
        ]
    )

    print(
        "Variables en categoría esperada:",
        integrado[
            "variables_en_categoria_esperada"
        ]
    )

    print(
        "Variables con hallazgos:",
        integrado[
            "variables_con_hallazgos"
        ]
    )

    print(
        "\nDetalle:"
    )

    for detalle in integrado[
        "detalles"
    ]:

        print(
            "-",
            detalle
        )

    print(
        "\nConclusión:"
    )

    print(
        integrado[
            "conclusion"
        ]
    )


# ==========================================================
# CONSOLA SEMANA 8
# ==========================================================

def gestionar_semana8():

    if not SEMANA8_DISPONIBLE:

        print(
            "\nSEMANA 8 NO DISPONIBLE"
        )

        print(
            "Detalle:",
            SEMANA8_ERROR
        )

        return


    try:

        sistema = (
            obtener_sistema_semana8()
        )

    except Exception as error:

        print(
            "\nNo fue posible iniciar Semana 8:"
        )

        print(
            error
        )

        return


    while True:

        print(
            "\n"
            + "=" * 60
        )

        print(
            "SEMANA 8 - RECONOCIMIENTO DOCUMENTAL"
        )

        print(
            "=" * 60
        )

        print(
            "1. Probar MLP con imagen del dataset"
        )

        print(
            "2. Analizar imagen propia"
        )

        print(
            "3. Analizar PDF médico"
        )

        print(
            "4. Ver evidencia SQLite y ontología"
        )

        print(
            "5. Volver al menú principal"
        )


        opcion = input(
            "\nSeleccione una opción: "
        ).strip()


        # ==================================================
        # 1. DATASET
        # ==================================================

        if opcion == "1":

            try:

                indice = int(
                    input(
                        (
                            "Índice del dataset "
                            "(ejemplo 15): "
                        )
                    ).strip()
                    or "15"
                )

                resultado = (
                    sistema.probar_dataset(
                        indice
                    )
                )

                print(
                    "\nRESULTADO MLP"
                )

                print(
                    "Índice:",
                    resultado[
                        "indice"
                    ]
                )

                print(
                    "Clase real:",
                    resultado[
                        "real"
                    ]
                )

                print(
                    "Predicción:",
                    resultado[
                        "prediccion"
                    ]
                )

                print(
                    "Coincide:",
                    (
                        "Sí"
                        if resultado[
                            "coincide"
                        ]
                        else "No"
                    )
                )

                if (
                    resultado[
                        "accuracy_modelo"
                    ]
                    is not None
                ):

                    print(
                        "Accuracy:",
                        round(
                            float(
                                resultado[
                                    "accuracy_modelo"
                                ]
                            ),
                            4
                        )
                    )

            except Exception as error:

                print(
                    "Error:",
                    error
                )


        # ==================================================
        # 2. IMAGEN
        # ==================================================

        elif opcion == "2":

            ruta = input(
                (
                    "Ruta de la imagen "
                    "PNG/JPG/JPEG/WEBP: "
                )
            ).strip()

            ruta = (
                ruta
                .strip('"')
                .strip("'")
            )

            try:

                respuesta = (
                    analizar_archivo_semana8(
                        ruta
                    )
                )

                resultado = respuesta[
                    "resultado"
                ]

                print(
                    "\nRESULTADO DE IMAGEN"
                )

                print(
                    "Archivo:",
                    resultado[
                        "archivo"
                    ]
                )

                print(
                    "Predicción:",
                    resultado[
                        "prediccion"
                    ]
                )

                if (
                    resultado[
                        "confianza"
                    ]
                    is not None
                ):

                    print(
                        "Confianza:",
                        (
                            f"{resultado['confianza'] * 100:.2f}%"
                        )
                    )

                if (
                    resultado[
                        "accuracy_modelo"
                    ]
                    is not None
                ):

                    print(
                        "Accuracy del modelo:",
                        (
                            f"{resultado['accuracy_modelo'] * 100:.2f}%"
                        )
                    )

                print(
                    "SQLite ID:",
                    resultado[
                        "reconocimiento_id"
                    ]
                )

                print(
                    "Evidencia registrada:",
                    "Sí"
                )

                print(
                    "Ontología actualizada:",
                    "Sí"
                )

            except Exception as error:

                print(
                    "Error:",
                    error
                )


        # ==================================================
        # 3. PDF
        # ==================================================

        elif opcion == "3":

            ruta = input(
                "Ruta del PDF médico: "
            ).strip()

            ruta = (
                ruta
                .strip('"')
                .strip("'")
            )

            try:

                respuesta = (
                    analizar_archivo_semana8(
                        ruta
                    )
                )

                resultado = respuesta[
                    "resultado"
                ]

                print(
                    "\nRESULTADO DEL DOCUMENTO"
                )

                print(
                    "Archivo:",
                    resultado[
                        "archivo"
                    ]
                )

                print(
                    "Páginas:",
                    resultado[
                        "numero_paginas"
                    ]
                )

                print(
                    "Tipo:",
                    resultado[
                        "tipo_documento"
                    ]
                )


                if resultado[
                    "requiere_ocr"
                ]:

                    print(
                        (
                            "El PDF no contiene suficiente "
                            "texto digital."
                        )
                    )

                    print(
                        "Estado: requiere OCR."
                    )

                else:

                    paciente = resultado[
                        "paciente"
                    ]

                    print(
                        "\nPaciente:",
                        (
                            paciente.get(
                                "nombre"
                            )
                            or "No detectado"
                        )
                    )

                    print(
                        "Identificación:",
                        (
                            paciente.get(
                                "identificacion"
                            )
                            or "No detectada"
                        )
                    )

                    print(
                        "Fecha:",
                        (
                            paciente.get(
                                "fecha"
                            )
                            or "No detectada"
                        )
                    )

                    print(
                        "\nExámenes detectados:",
                        len(
                            resultado[
                                "examenes"
                            ]
                        )
                    )

                    for examen in resultado[
                        "examenes"
                    ]:

                        print(
                            "-"
                        )

                        print(
                            "  Examen:",
                            examen[
                                "examen"
                            ]
                        )

                        print(
                            "  Resultado:",
                            examen[
                                "resultado"
                            ]
                        )

                        print(
                            "  Unidad:",
                            (
                                examen[
                                    "unidad"
                                ]
                                or "No detectada"
                            )
                        )

                        print(
                            "  Referencia:",
                            (
                                examen[
                                    "referencia"
                                ]
                                or "No detectada"
                            )
                        )

                        print(
                            "  Página:",
                            examen[
                                "pagina"
                            ]
                        )

                print(
                    "\nSQLite ID:",
                    resultado[
                        "documento_id"
                    ]
                )

                print(
                    "Evidencia registrada:",
                    "Sí"
                )

                print(
                    "Ontología actualizada:",
                    "Sí"
                )

            except Exception as error:

                print(
                    "Error:",
                    error
                )


        # ==================================================
        # 4. EVIDENCIA
        # ==================================================

        elif opcion == "4":

            try:

                resumen = (
                    obtener_resumen_semana8()
                )

                print(
                    "\nEVIDENCIA SQLITE"
                )

                print(
                    resumen[
                        "evidencia"
                    ]
                )

                print(
                    "\nONTOLOGÍA"
                )

                print(
                    resumen[
                        "ontologia"
                    ]
                )

                if (
                    resumen[
                        "accuracy"
                    ]
                    is not None
                ):

                    print(
                        "\nAccuracy MLP:",
                        (
                            f"{resumen['accuracy'] * 100:.2f}%"
                        )
                    )

            except Exception as error:

                print(
                    "Error:",
                    error
                )


        # ==================================================
        # 5. VOLVER
        # ==================================================

        elif opcion == "5":

            break


        else:

            print(
                "Opción no válida."
            )


# ==========================================================
# MENÚ PRINCIPAL
# ==========================================================

def mostrar_menu():

    print(
        "\n"
        + "=" * 60
    )

    print(
        f"HIS_IA v{VERSION}"
    )

    print(
        "=" * 60
    )

    print(
        "1. Analizar información clínica"
    )

    print(
        "2. Evaluar prioridad de revisión"
    )

    print(
        "3. Organizar revisión con A*"
    )

    print(
        "4. Priorizar pacientes con Minimax"
    )

    print(
        "5. Reconocimiento del caso - Semana 7"
    )

    print(
        "6. Reconocimiento documental - Semana 8"
    )

    print(
        "7. Consultar asistente HIS_IA"
    )

    print(
        "8. Validar funcionamiento Semana 5"
    )

    print(
        "9. Salir"
    )


# ==========================================================
# MAIN
# ==========================================================

def main():

    print(
        f"\nIniciando HIS_IA v{VERSION}\n"
    )

    modelo_prioridad, _, _ = (
        entrenar_modelo_prioridad()
    )


    try:

        sistema_hibrido = (
            SistemaHibridoHIS()
        )

    except Exception as error:

        print(
            "No fue posible iniciar "
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


        # ==================================================
        # 1
        # ==================================================

        if opcion == "1":

            texto = input(
                "\nIngrese información clínica: "
            )

            resultado = (
                clasificar_texto(
                    texto
                )
            )

            print(
                "\nCategoría principal:",
                resultado[
                    "principal"
                ]
            )

            print(
                "Categorías detectadas:",
                resultado[
                    "categorias"
                ]
            )


        # ==================================================
        # 2
        # ==================================================

        elif opcion == "2":

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

                prioridad = (
                    evaluar_prioridad(
                        modelo_prioridad,
                        edad,
                        documentos,
                        resultados,
                        imagenes
                    )
                )

                print(
                    "\nPrioridad:",
                    prioridad
                )

            except ValueError:

                print(
                    "Ingrese valores numéricos válidos."
                )


        # ==================================================
        # 3
        # ==================================================

        elif opcion == "3":

            gestionar_astar()


        # ==================================================
        # 4
        # ==================================================

        elif opcion == "4":

            gestionar_minimax()


        # ==================================================
        # 5
        # ==================================================

        elif opcion == "5":

            gestionar_reconocimiento()


        # ==================================================
        # 6
        # ==================================================

        elif opcion == "6":

            gestionar_semana8()


        # ==================================================
        # 7
        # ==================================================

        elif opcion == "7":

            if sistema_hibrido:

                consulta = input(
                    "\nIngrese su consulta: "
                ).strip()

                if consulta:

                    resultado = (
                        sistema_hibrido
                        .analizar_consulta(
                            consulta
                        )
                    )

                    print(
                        "\nResultado HIS_IA"
                    )

                    print(
                        "Categoría:",
                        resultado[
                            "clase"
                        ]
                    )

                    acciones = (
                        ", ".join(
                            resultado[
                                "reglas"
                            ]
                        )

                        if resultado[
                            "reglas"
                        ]

                        else (
                            "Sin regla específica"
                        )
                    )

                    print(
                        "Acciones sugeridas:",
                        acciones
                    )

                    print(
                        "Información relacionada:",
                        resultado[
                            "evidencia"
                        ]
                    )

                    print(
                        "Similitud:",
                        round(
                            resultado[
                                "similitud"
                            ],
                            3
                        )
                    )

            else:

                print(
                    "Sistema híbrido no disponible."
                )


        # ==================================================
        # 8
        # ==================================================

        elif opcion == "8":

            if sistema_hibrido:

                validar_funcionamiento_semana5(
                    sistema_hibrido
                )

            else:

                print(
                    "Sistema híbrido no disponible."
                )


        # ==================================================
        # 9
        # ==================================================

        elif opcion == "9":

            print(
                "\nHIS_IA finalizado."
            )

            break


        else:

            print(
                "Opción no válida."
            )


# ==========================================================
# EJECUCIÓN
# ==========================================================

if __name__ == "__main__":
    main()