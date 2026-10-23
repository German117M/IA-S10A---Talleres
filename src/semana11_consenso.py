from collections import Counter

import pandas as pd

from semana11_benchmark import (
    cargar_datos,
    crear_modelos,
    VARIABLES,
    OBJETIVO
)


# ==========================================================
# SEMANA 11
# VALIDACIÓN CON MÚLTIPLES MÉTODOS
# ==========================================================

_MODELOS = None


def cargar_metodos():

    global _MODELOS


    if _MODELOS is not None:

        return _MODELOS


    datos = cargar_datos()


    X = datos[
        VARIABLES
    ]


    y = datos[
        OBJETIVO
    ]


    modelos = crear_modelos()


    for modelo in modelos.values():

        modelo.fit(
            X,
            y
        )


    _MODELOS = modelos


    return _MODELOS


# ==========================================================
# TRADUCIR RESULTADO
# ==========================================================

def traducir_prioridad(
    valor
):

    if int(valor) == 1:

        return "Prioritaria"


    return "Normal"


# ==========================================================
# EVALUAR CASO
# ==========================================================

def evaluar_caso_semana11(
    edad,
    documentos,
    resultados,
    imagenes
):

    modelos = cargar_metodos()


    entrada = pd.DataFrame(
        [
            [
                edad,
                documentos,
                resultados,
                imagenes
            ]
        ],
        columns=VARIABLES
    )


    predicciones = {}


    for nombre, modelo in modelos.items():

        valor = modelo.predict(
            entrada
        )[0]


        predicciones[
            nombre
        ] = traducir_prioridad(
            valor
        )


    # ======================================================
    # DECISIÓN POR MAYORÍA
    # ======================================================

    # ======================================================
    # DECISIÓN PRINCIPAL
    # ======================================================
    #
    # Semana 11 demostró que Random Forest ofrece
    # el mejor equilibrio para HIS_IA.
    #
    # Logistic Regression y MLP no sustituyen su decisión:
    # funcionan como métodos de verificación.
    # ======================================================

    resultado_final = predicciones[
        "Random Forest"
    ]


    total_metodos = len(
        predicciones
    )


    coincidencias = sum(
        1
        for resultado in predicciones.values()
        if resultado == resultado_final
    )


    # ======================================================
    # NIVEL DE ACUERDO
    # ======================================================

    if coincidencias == total_metodos:

        nivel_acuerdo = (
            "Alto"
        )

        revision_recomendada = (
            False
        )

        explicacion = (
            "Los tres métodos de análisis llegaron "
            "al mismo resultado."
        )

    else:

        nivel_acuerdo = (
            "Medio"
        )

        revision_recomendada = (
            True
        )

        explicacion = (
            "La mayoría de los métodos coincide, "
            "pero uno obtuvo un resultado diferente. "
            "Se recomienda revisar el caso antes "
            "de tomar una decisión definitiva."
        )


    # ======================================================
    # DETALLE AMIGABLE
    # ======================================================

    detalle = {

        "Análisis principal": {
            "metodo":
                "Random Forest",

            "resultado":
                predicciones.get(
                    "Random Forest",
                    "No disponible"
                )
        },

        "Verificación estadística": {
            "metodo":
                "Logistic Regression",

            "resultado":
                predicciones.get(
                    "Logistic Regression",
                    "No disponible"
                )
        },

        "Verificación neuronal": {
            "metodo":
                "MLP",

            "resultado":
                predicciones.get(
                    "MLP",
                    "No disponible"
                )
        }
    }


    return {

        "resultado":
            resultado_final,

        "nivel_acuerdo":
            nivel_acuerdo,

        "coincidencias":
            coincidencias,

        "total_metodos":
            total_metodos,

        "texto_coincidencia":
            (
                f"{coincidencias} de "
                f"{total_metodos} análisis coinciden"
            ),

        "revision_recomendada":
            revision_recomendada,

        "explicacion":
            explicacion,

        "detalle":
            detalle,

        "predicciones_tecnicas":
            predicciones
    }




# ==========================================================
# SEMANA 11
# AUDITORÍA DE DECISIONES DE HIS_IA
# ==========================================================

def auditar_decisiones_semana11():

    from sklearn.model_selection import (
        train_test_split
    )

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
        random_state=42,
        stratify=y
    )


    modelos = crear_modelos()


    for modelo in modelos.values():

        modelo.fit(
            X_train,
            y_train
        )


    total = len(
        X_test
    )

    acuerdo_completo = 0

    revision_recomendada = 0

    aciertos_principal = 0

    casos_revision = []


    for indice in X_test.index:

        entrada = X_test.loc[
            [
                indice
            ]
        ]


        predicciones = {}


        for nombre, modelo in modelos.items():

            valor = modelo.predict(
                entrada
            )[0]

            predicciones[
                nombre
            ] = traducir_prioridad(
                valor
            )


        # Random Forest es la decisión principal.
        # Los demás métodos sirven como verificación.

        resultado_final = predicciones[
            "Random Forest"
        ]


        votos = sum(
            1
            for resultado in predicciones.values()
            if resultado == resultado_final
        )


        esperado = traducir_prioridad(
            y_test.loc[
                indice
            ]
        )


        if resultado_final == esperado:

            aciertos_principal += 1


        if votos == 3:

            acuerdo_completo += 1

        else:

            revision_recomendada += 1


            fila = X_test.loc[
                indice
            ]


            casos_revision.append(
                {
                    "caso":
                        int(
                            indice
                        ),

                    "edad":
                        int(
                            fila[
                                "edad"
                            ]
                        ),

                    "documentos_pendientes":
                        int(
                            fila[
                                "documentos_pendientes"
                            ]
                        ),

                    "resultados_pendientes":
                        int(
                            fila[
                                "resultados_pendientes"
                            ]
                        ),

                    "imagenes_pendientes":
                        int(
                            fila[
                                "imagenes_pendientes"
                            ]
                        ),

                    "resultado_sugerido":
                        resultado_final,

                    "resultado_esperado":
                        esperado,

                    "coincidencia":
                        f"{votos} de 3",

                    "analisis_principal":
                        predicciones.get(
                            "Random Forest"
                        ),

                    "verificacion_estadistica":
                        predicciones.get(
                            "Logistic Regression"
                        ),

                    "verificacion_neuronal":
                        predicciones.get(
                            "MLP"
                        )
                }
            )


    porcentaje_acuerdo = (
        acuerdo_completo
        /
        total
        *
        100
    )


    porcentaje_revision = (
        revision_recomendada
        /
        total
        *
        100
    )


    precision_principal = (
        aciertos_principal
        /
        total
        *
        100
    )


    return {

        "casos_evaluados":
            int(
                total
            ),

        "acuerdo_completo":
            int(
                acuerdo_completo
            ),

        "revision_recomendada":
            int(
                revision_recomendada
            ),

        "porcentaje_acuerdo":
            round(
                porcentaje_acuerdo,
                2
            ),

        "porcentaje_revision":
            round(
                porcentaje_revision,
                2
            ),

        "precision_modelo_principal":
            round(
                precision_principal,
                2
            ),

        "casos_revision":
            casos_revision
    }


# ==========================================================
# PRUEBA DIRECTA
# ==========================================================

def main():

    resultado = evaluar_caso_semana11(
        edad=76,
        documentos=5,
        resultados=6,
        imagenes=3
    )


    print()
    print(
        "=" * 60
    )

    print(
        "EVALUACIÓN DE PRIORIDAD HIS_IA"
    )

    print(
        "=" * 60
    )


    print()
    print(
        "RESULTADO DEL CASO"
    )

    print(
        resultado[
            "resultado"
        ]
    )


    print()
    print(
        "NIVEL DE ACUERDO"
    )

    print(
        resultado[
            "nivel_acuerdo"
        ]
    )


    print()
    print(
        "COINCIDENCIA"
    )

    print(
        resultado[
            "texto_coincidencia"
        ]
    )


    print()
    print(
        "REVISIÓN ADICIONAL"
    )

    print(
        (
            "Recomendada"
            if resultado[
                "revision_recomendada"
            ]
            else
            "No necesaria"
        )
    )


    print()
    print(
        "INTERPRETACIÓN"
    )

    print(
        resultado[
            "explicacion"
        ]
    )


    print()
    print(
        "DETALLE DE LOS ANÁLISIS"
    )

    for nombre, detalle in resultado[
        "detalle"
    ].items():

        print(
            f"- {nombre}: "
            f"{detalle['resultado']}"
        )


    print()
    print(
        "=" * 60
    )


if __name__ == "__main__":

    main()
