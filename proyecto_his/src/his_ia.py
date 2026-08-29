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


# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

RANDOM_STATE = 42

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "datos_his.csv"


# =========================================================
# SEMANA 3
# CLASIFICACIÓN SIMBÓLICA DE INFORMACIÓN CLÍNICA
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
            "muestra",
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
        )
    ),
]


CUSTOM_RULES = {

    "Historia clínica": (
        "historial",
        "registro clinico",
    ),

    "Laboratorio clínico": (
        "examen",
        "prueba",
    ),

    "Imagen diagnóstica": (
        "estudio radiologico",
        "diagnostico por imagen",
    ),

    "Medicamentos": (
        "formula",
        "terapia",
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

            if normalizar_texto(palabra) in texto_normalizado:
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
# =========================================================

def entrenar_modelo():

    if not DATA_FILE.exists():

        print("\nNo se encontró el archivo de datos:")
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

        X_train, X_test, y_train, y_test = train_test_split(
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

        print("\nModelo de análisis cargado correctamente.")

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
            "\nNo fue posible cargar el modelo."
        )

        print(
            f"Detalle: {error}"
        )

        return None


def evaluar_prioridad(modelo):

    if modelo is None:

        print(
            "\nEl modelo de análisis no está disponible."
        )

        return

    print("\nIngrese los datos del registro.")

    try:

        edad = int(
            input("Edad: ")
        )

        documentos = int(
            input("Documentos pendientes: ")
        )

        resultados = int(
            input("Resultados pendientes: ")
        )

        imagenes = int(
            input("Imágenes pendientes: ")
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

    if prediccion == 1:
        resultado = "Prioritaria"
    else:
        resultado = "Normal"

    print("\n" + "=" * 50)

    print(
        f"Prioridad estimada: {resultado}"
    )

    print("=" * 50)


# =========================================================
# SEMANA 4
# ORGANIZACIÓN DE TAREAS CON A*
# =========================================================

COSTOS_PROCESAMIENTO = {

    "Historia clínica": 1,

    "Laboratorio clínico": 2,

    "Medicamentos": 2,

    "Imagen diagnóstica": 3,
}


def heuristica(pendientes):

    """
    Estima el trabajo restante.

    En esta versión se utiliza la cantidad
    de tareas que todavía están pendientes.
    """

    return len(pendientes)


def planificar_procesamiento(tareas):

    inicio = tuple(tareas)
    meta = tuple()

    frontera = []

    heapq.heappush(
        frontera,
        (
            heuristica(inicio),
            0,
            inicio,
            []
        )
    )

    visitados = {}

    while frontera:

        prioridad, costo_actual, estado, camino = (
            heapq.heappop(frontera)
        )

        if estado == meta:

            return camino, costo_actual

        if (
            estado in visitados
            and visitados[estado] <= costo_actual
        ):
            continue

        visitados[estado] = costo_actual

        for tarea in estado:

            nuevo_estado = list(estado)

            nuevo_estado.remove(
                tarea
            )

            nuevo_estado = tuple(
                nuevo_estado
            )

            costo_tarea = COSTOS_PROCESAMIENTO.get(
                tarea,
                1
            )

            nuevo_costo = (
                costo_actual
                + costo_tarea
            )

            estimacion = heuristica(
                nuevo_estado
            )

            prioridad_total = (
                nuevo_costo
                + estimacion
            )

            nuevo_camino = (
                camino
                + [tarea]
            )

            heapq.heappush(
                frontera,
                (
                    prioridad_total,
                    nuevo_costo,
                    nuevo_estado,
                    nuevo_camino
                )
            )

    return None, None


def organizar_tareas():

    print("\n" + "=" * 60)

    print("ORGANIZACIÓN DE TAREAS PENDIENTES")

    print("=" * 60)

    print("\nSeleccione los elementos pendientes:")

    print("1. Historia clínica")
    print("2. Laboratorio clínico")
    print("3. Imagen diagnóstica")
    print("4. Medicamentos")

    entrada = input(
        "\nIngrese las opciones separadas por coma: "
    )

    mapa = {

        "1": "Historia clínica",

        "2": "Laboratorio clínico",

        "3": "Imagen diagnóstica",

        "4": "Medicamentos",
    }

    tareas = []

    for opcion in entrada.split(","):

        opcion = opcion.strip()

        if (
            opcion in mapa
            and mapa[opcion] not in tareas
        ):

            tareas.append(
                mapa[opcion]
            )

    if not tareas:

        print(
            "\nNo se seleccionaron tareas válidas."
        )

        return

    camino, costo = planificar_procesamiento(
        tareas
    )

    if camino is None:

        print(
            "\nNo fue posible generar "
            "un orden de procesamiento."
        )

        return

    print("\nOrden sugerido de revisión:")

    for numero, tarea in enumerate(
        camino,
        start=1
    ):

        print(
            f"{numero}. {tarea}"
        )

    print(
        f"\nCosto total estimado: {costo}"
    )


# =========================================================
# INTERFAZ PRINCIPAL
# =========================================================

def mostrar_menu():

    print("\n" + "=" * 60)

    print("HIS_IA")

    print(
        "ASISTENTE DE INTELIGENCIA ARTIFICIAL PARA HIS"
    )

    print("=" * 60)

    print(
        "\n1. Analizar información clínica"
    )

    print(
        "2. Evaluar prioridad de revisión"
    )

    print(
        "3. Organizar tareas pendientes"
    )

    print(
        "4. Salir"
    )


# =========================================================
# PROGRAMA PRINCIPAL
# =========================================================

def main():

    print("\nIniciando HIS_IA...")

    modelo = entrenar_modelo()

    while True:

        mostrar_menu()

        opcion = input(
            "\nSeleccione una opción: "
        )

        if opcion == "1":

            texto = input(
                "\nIngrese la información clínica:\n"
            )

            principal, detectadas, puntuaciones = (
                clasificar_texto(texto)
            )

            print("\n" + "=" * 50)

            print(
                f"Categoría principal: {principal}"
            )

            if detectadas:

                print(
                    "\nInformación relacionada con:"
                )

                for categoria in detectadas:

                    print(
                        f"- {categoria}"
                    )

            print("=" * 50)

        elif opcion == "2":

            evaluar_prioridad(
                modelo
            )

        elif opcion == "3":

            organizar_tareas()

        elif opcion == "4":

            print(
                "\nCerrando HIS_IA."
            )

            break

        else:

            print(
                "\nOpción no válida. "
                "Seleccione una opción del 1 al 4."
            )


if __name__ == "__main__":
    main()