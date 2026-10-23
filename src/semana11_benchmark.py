from pathlib import Path
from time import perf_counter
import json

import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, confusion_matrix


# ==========================================================
# SEMANA 11
# SELECCIÓN DEL MODELO ACTIVO DE PRIORIDAD - HIS_IA
# ==========================================================

RANDOM_STATE = 42

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

DATA_FILE = (
    PROJECT_ROOT
    / "proyecto_his"
    / "data"
    / "datos_his.csv"
)

ARTIFACTS_DIR = (
    PROJECT_ROOT
    / "artifacts"
)

BENCHMARK_FILE = (
    ARTIFACTS_DIR
    / "benchmark.csv"
)

MODEL_FILE = (
    ARTIFACTS_DIR
    / "modelo_prioridad.joblib"
)

METADATA_FILE = (
    ARTIFACTS_DIR
    / "modelo_prioridad_metadata.json"
)


VARIABLES = [
    "edad",
    "documentos_pendientes",
    "resultados_pendientes",
    "imagenes_pendientes",
]

OBJETIVO = "prioridad"


# ==========================================================
# DATOS
# ==========================================================

def cargar_datos():

    if not DATA_FILE.exists():

        raise FileNotFoundError(
            f"No se encontró el dataset: {DATA_FILE}"
        )

    datos = pd.read_csv(
        DATA_FILE
    )

    columnas = (
        VARIABLES
        +
        [
            OBJETIVO
        ]
    )

    faltantes = [
        columna
        for columna in columnas
        if columna not in datos.columns
    ]

    if faltantes:

        raise ValueError(
            "Faltan columnas: "
            +
            ", ".join(
                faltantes
            )
        )

    return datos[
        columnas
    ].dropna()


# ==========================================================
# MODELOS CANDIDATOS
# ==========================================================

def crear_modelos():

    return {

        "Logistic Regression":
            make_pipeline(
                StandardScaler(),
                LogisticRegression(
                    max_iter=1500,
                    random_state=RANDOM_STATE
                )
            ),

        "Random Forest":
            RandomForestClassifier(
                n_estimators=250,
                random_state=RANDOM_STATE,
                n_jobs=-1
            ),

        "MLP":
            make_pipeline(
                StandardScaler(),
                MLPClassifier(
                    hidden_layer_sizes=(64,),
                    max_iter=1500,
                    random_state=RANDOM_STATE
                )
            )
    }


# ==========================================================
# SELECCIÓN
# ==========================================================

def seleccionar_modelo(
    tabla
):

    mejor_accuracy = tabla[
        "accuracy"
    ].max()

    mejores = tabla[
        tabla[
            "accuracy"
        ] == mejor_accuracy
    ]


    nombres = set(
        mejores[
            "modelo"
        ]
    )


    # En caso de empate entre Forest y MLP,
    # para HIS_IA priorizamos interpretabilidad
    # y mantenibilidad.

    if "Random Forest" in nombres:

        return "Random Forest"


    if "Logistic Regression" in nombres:

        return "Logistic Regression"


    return (
        mejores.sort_values(
            "fit_seconds"
        )
        .iloc[0][
            "modelo"
        ]
    )


# ==========================================================
# BENCHMARK + DESPLIEGUE
# ==========================================================

def ejecutar_benchmark():

    datos = cargar_datos()

    X = datos[
        VARIABLES
    ]

    y = datos[
        OBJETIVO
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


    modelos = crear_modelos()

    resultados = []

    matrices = {}


    for nombre, modelo in modelos.items():

        inicio = perf_counter()

        modelo.fit(
            X_train,
            y_train
        )

        tiempo = (
            perf_counter()
            -
            inicio
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

        matrices[
            nombre
        ] = matriz.tolist()


        resultados.append(
            {
                "modelo":
                    nombre,

                "accuracy":
                    float(
                        accuracy
                    ),

                "fit_seconds":
                    float(
                        tiempo
                    )
            }
        )


    tabla = pd.DataFrame(
        resultados
    )


    tabla = tabla.sort_values(
        by=[
            "accuracy",
            "fit_seconds"
        ],
        ascending=[
            False,
            True
        ]
    ).reset_index(
        drop=True
    )


    modelo_seleccionado = seleccionar_modelo(
        tabla
    )


    fila_seleccionada = tabla[
        tabla[
            "modelo"
        ] == modelo_seleccionado
    ].iloc[0]


    # ======================================================
    # ENTRENAR GANADOR CON TODOS LOS DATOS
    # ======================================================

    modelo_final = crear_modelos()[
        modelo_seleccionado
    ]

    modelo_final.fit(
        X,
        y
    )


    # ======================================================
    # GUARDAR MODELO ACTIVO
    # ======================================================

    ARTIFACTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    joblib.dump(
        modelo_final,
        MODEL_FILE
    )


    tabla.to_csv(
        BENCHMARK_FILE,
        index=False
    )


    metadata = {

        "modelo":
            modelo_seleccionado,

        "accuracy_validacion":
            float(
                fila_seleccionada[
                    "accuracy"
                ]
            ),

        "fit_seconds_validacion":
            float(
                fila_seleccionada[
                    "fit_seconds"
                ]
            ),

        "matriz_confusion":
            matrices[
                modelo_seleccionado
            ],

        "registros":
            int(
                len(
                    datos
                )
            ),

        "entrenamiento_validacion":
            int(
                len(
                    X_train
                )
            ),

        "prueba_validacion":
            int(
                len(
                    X_test
                )
            ),

        "entrenamiento_final":
            int(
                len(
                    datos
                )
            ),

        "random_state":
            RANDOM_STATE,

        "variables":
            VARIABLES,

        "objetivo":
            OBJETIVO,

        "criterio_seleccion":
            (
                "Máximo accuracy. En caso de empate se "
                "prioriza Random Forest por su equilibrio "
                "entre desempeño, explicabilidad y "
                "mantenibilidad para HIS_IA."
            )
    }


    METADATA_FILE.write_text(
        json.dumps(
            metadata,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


    return (
        datos,
        X_train,
        X_test,
        tabla
    )


# ==========================================================
# CONSOLA
# ==========================================================

def main():

    (
        datos,
        X_train,
        X_test,
        tabla
    ) = ejecutar_benchmark()


    metadata = json.loads(
        METADATA_FILE.read_text(
            encoding="utf-8"
        )
    )


    print()
    print(
        "=" * 64
    )

    print(
        "SEMANA 11 - SELECCIÓN DE MODELO PARA HIS_IA"
    )

    print(
        "=" * 64
    )


    print(
        f"Registros: {len(datos)}"
    )

    print(
        f"Entrenamiento de validación: {len(X_train)}"
    )

    print(
        f"Prueba: {len(X_test)}"
    )


    print()
    print(
        "RESULTADOS"
    )

    print(
        "-" * 64
    )


    mostrar = tabla.copy()

    mostrar[
        "accuracy"
    ] = (
        mostrar[
            "accuracy"
        ]
        *
        100
    ).map(
        lambda x:
            f"{x:.2f} %"
    )

    mostrar[
        "fit_seconds"
    ] = mostrar[
        "fit_seconds"
    ].map(
        lambda x:
            f"{x:.4f} s"
    )


    print(
        mostrar.to_string(
            index=False
        )
    )


    print()
    print(
        "=" * 64
    )

    print(
        "MODELO ACTIVADO EN HIS_IA"
    )

    print(
        metadata[
            "modelo"
        ]
    )

    print(
        (
            "Accuracy de validación: "
            f"{metadata['accuracy_validacion'] * 100:.2f} %"
        )
    )

    print()
    print(
        f"Modelo guardado: {MODEL_FILE}"
    )

    print(
        f"Metadata: {METADATA_FILE}"
    )

    print(
        f"Benchmark: {BENCHMARK_FILE}"
    )

    print(
        "=" * 64
    )

    print()


if __name__ == "__main__":
    main()
