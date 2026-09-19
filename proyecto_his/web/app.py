from pathlib import Path
import sys

from flask import (
    Flask,
    jsonify,
    render_template,
    request
)


# ==========================================================
# CONFIGURACIÓN DE RUTAS
# ==========================================================

WEB_DIR = Path(
    __file__
).resolve().parent

PROJECT_DIR = (
    WEB_DIR.parent
)

SRC_DIR = (
    PROJECT_DIR / "src"
)


# Agregar la carpeta src al path de Python
if str(SRC_DIR) not in sys.path:

    sys.path.insert(
        0,
        str(SRC_DIR)
    )


# ==========================================================
# IMPORTAR FUNCIONES DE HIS_IA
# ==========================================================

from his_ia import (
    VERSION,
    SistemaHibridoHIS,
    clasificar_texto,
    entrenar_modelo_prioridad,
    evaluar_prioridad,
    planificar_revision,
    priorizar_pacientes_minimax,
    analizar_representaciones,
)


# ==========================================================
# CONFIGURACIÓN DE FLASK
# ==========================================================

app = Flask(
    __name__
)


# ==========================================================
# VARIABLES GLOBALES
# ==========================================================

modelo_prioridad = None
sistema_hibrido = None


# ==========================================================
# CARGAR MODELO DE PRIORIDAD
# ==========================================================

try:

    (
        modelo_prioridad,
        precision_modelo,
        matriz_modelo
    ) = entrenar_modelo_prioridad()

except Exception as error:

    print(
        "Error cargando modelo de prioridad:"
    )

    print(
        error
    )


# ==========================================================
# CARGAR SISTEMA HÍBRIDO
# ==========================================================

try:

    sistema_hibrido = (
        SistemaHibridoHIS()
    )

except Exception as error:

    print(
        "Error cargando sistema híbrido:"
    )

    print(
        error
    )


# ==========================================================
# PÁGINA PRINCIPAL
# ==========================================================

@app.route("/")
def index():

    return render_template(
        "index.html",
        version=VERSION
    )


# ==========================================================
# SEMANA 3
# ANALIZAR INFORMACIÓN
# ==========================================================

@app.route(
    "/api/analizar",
    methods=["POST"]
)
def api_analizar():

    datos = (
        request.get_json(
            silent=True
        )
        or {}
    )


    texto = str(
        datos.get(
            "texto",
            ""
        )
    ).strip()


    if not texto:

        return jsonify({
            "error":
                "Debe ingresar un texto."
        }), 400


    resultado = (
        clasificar_texto(
            texto
        )
    )


    return jsonify(
        resultado
    )


# ==========================================================
# SEMANA 2
# MODELO DE PRIORIDAD
# ==========================================================

@app.route(
    "/api/prioridad",
    methods=["POST"]
)
def api_prioridad():

    if modelo_prioridad is None:

        return jsonify({
            "error":
                "El modelo de prioridad "
                "no está disponible."
        }), 503


    datos = (
        request.get_json(
            silent=True
        )
        or {}
    )


    try:

        edad = int(
            datos.get(
                "edad"
            )
        )


        documentos = int(
            datos.get(
                "documentos_pendientes"
            )
        )


        resultados = int(
            datos.get(
                "resultados_pendientes"
            )
        )


        imagenes = int(
            datos.get(
                "imagenes_pendientes"
            )
        )


    except (
        TypeError,
        ValueError
    ):

        return jsonify({
            "error":
                "Los valores deben "
                "ser numéricos."
        }), 400


    if edad < 0:

        return jsonify({
            "error":
                "La edad no puede "
                "ser negativa."
        }), 400


    if documentos < 0:

        return jsonify({
            "error":
                "Los documentos pendientes "
                "no pueden ser negativos."
        }), 400


    if resultados < 0:

        return jsonify({
            "error":
                "Los resultados pendientes "
                "no pueden ser negativos."
        }), 400


    if imagenes < 0:

        return jsonify({
            "error":
                "Las imágenes pendientes "
                "no pueden ser negativas."
        }), 400


    prioridad = (
        evaluar_prioridad(
            modelo_prioridad,
            edad,
            documentos,
            resultados,
            imagenes
        )
    )


    return jsonify({
        "prioridad":
            prioridad
    })


# ==========================================================
# SEMANA 4
# ALGORITMO A*
# ==========================================================

@app.route(
    "/api/revision",
    methods=["POST"]
)
def api_revision():

    datos = (
        request.get_json(
            silent=True
        )
        or {}
    )


    elementos = datos.get(
        "elementos",
        []
    )


    if not isinstance(
        elementos,
        list
    ):

        return jsonify({
            "error":
                "Los elementos enviados "
                "no son válidos."
        }), 400


    if not elementos:

        return jsonify({
            "error":
                "Seleccione al menos "
                "un elemento."
        }), 400


    try:

        resultado = (
            planificar_revision(
                elementos
            )
        )


    except ValueError as error:

        return jsonify({
            "error":
                str(
                    error
                )
        }), 400


    except Exception as error:

        return jsonify({
            "error":
                "No fue posible organizar "
                "la revisión."
        }), 500


    return jsonify(
        resultado
    )


# ==========================================================
# SEMANA 4
# MINIMAX
# ==========================================================

@app.route(
    "/api/priorizar-pacientes",
    methods=["POST"]
)
def api_priorizar_pacientes():

    datos = (
        request.get_json(
            silent=True
        )
        or {}
    )


    paciente1 = datos.get(
        "paciente1"
    )


    paciente2 = datos.get(
        "paciente2"
    )


    if not isinstance(
        paciente1,
        dict
    ):

        return jsonify({
            "error":
                "Paciente 1 no válido."
        }), 400


    if not isinstance(
        paciente2,
        dict
    ):

        return jsonify({
            "error":
                "Paciente 2 no válido."
        }), 400


    try:

        resultado = (
            priorizar_pacientes_minimax(
                paciente1,
                paciente2
            )
        )


    except Exception as error:

        return jsonify({
            "error":
                "No fue posible comparar "
                "los pacientes."
        }), 500


    return jsonify(
        resultado
    )


# ==========================================================
# SEMANA 7
# REPRESENTACIONES DEL RECONOCIMIENTO
# ==========================================================

@app.route(
    "/api/reconocimiento",
    methods=["POST"]
)
def api_reconocimiento():

    datos = (
        request.get_json(
            silent=True
        )
        or {}
    )


    caso = datos.get(
        "caso"
    )


    if not isinstance(
        caso,
        dict
    ):

        return jsonify({
            "error":
                "Los datos del caso "
                "no son válidos."
        }), 400


    motivo = str(
        caso.get(
            "motivo_consulta",
            ""
        )
    ).strip()


    if not motivo:

        return jsonify({
            "error":
                "Debe ingresar el "
                "motivo de consulta."
        }), 400


    # ------------------------------------------------------
    # VALIDAR TEMPERATURA
    # ------------------------------------------------------

    try:

        temperatura = float(
            caso.get(
                "temperatura"
            )
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({
            "error":
                "La temperatura debe "
                "ser un valor numérico."
        }), 400


    # ------------------------------------------------------
    # VALIDAR LATIDOS
    # ------------------------------------------------------

    try:

        latidos = int(
            caso.get(
                "latidos"
            )
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({
            "error":
                "Los latidos deben "
                "ser un valor numérico."
        }), 400


    # ------------------------------------------------------
    # VALIDAR PRESIÓN
    # ------------------------------------------------------

    try:

        presion = int(
            caso.get(
                "presion"
            )
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({
            "error":
                "La presión debe "
                "ser un valor numérico."
        }), 400


    # ------------------------------------------------------
    # VALIDACIONES GENERALES
    # ------------------------------------------------------

    if temperatura <= 0:

        return jsonify({
            "error":
                "La temperatura ingresada "
                "no es válida."
        }), 400


    if latidos <= 0:

        return jsonify({
            "error":
                "Los latidos ingresados "
                "no son válidos."
        }), 400


    if presion <= 0:

        return jsonify({
            "error":
                "La presión ingresada "
                "no es válida."
        }), 400


    # ------------------------------------------------------
    # NORMALIZAR DATOS
    # ------------------------------------------------------

    caso["motivo_consulta"] = (
        motivo
    )


    caso["temperatura"] = (
        temperatura
    )


    caso["latidos"] = (
        latidos
    )


    caso["presion"] = (
        presion
    )


    # ------------------------------------------------------
    # ANALIZAR REPRESENTACIONES
    # ------------------------------------------------------

    try:

        resultado = (
            analizar_representaciones(
                caso
            )
        )


    except Exception as error:

        print(
            "Error en Semana 7:"
        )

        print(
            error
        )


        return jsonify({
            "error":
                "No fue posible procesar "
                "el reconocimiento del caso."
        }), 500


    return jsonify(
        resultado
    )


# ==========================================================
# SEMANA 5
# ASISTENTE HIS_IA
# ==========================================================

@app.route(
    "/api/asistente",
    methods=["POST"]
)
def api_asistente():

    if sistema_hibrido is None:

        return jsonify({
            "error":
                "El asistente HIS_IA "
                "no está disponible."
        }), 503


    datos = (
        request.get_json(
            silent=True
        )
        or {}
    )


    consulta = str(
        datos.get(
            "consulta",
            ""
        )
    ).strip()


    if not consulta:

        return jsonify({
            "error":
                "Debe ingresar "
                "una consulta."
        }), 400


    try:

        resultado = (
            sistema_hibrido
            .analizar_consulta(
                consulta
            )
        )


    except Exception as error:

        print(
            "Error en asistente:"
        )

        print(
            error
        )


        return jsonify({
            "error":
                "No fue posible procesar "
                "la consulta."
        }), 500


    return jsonify(
        resultado
    )


# ==========================================================
# INFORMACIÓN DEL SISTEMA
# ==========================================================

@app.route(
    "/api/sistema",
    methods=["GET"]
)
def api_sistema():

    return jsonify({

        "nombre":
            "HIS_IA",

        "version":
            VERSION,

        "estado":
            "Operativo",

        "modulos": [

            "Semana 2 - Machine Learning",

            "Semana 3 - Clasificación",

            "Semana 4 - A*",

            "Semana 4 - Minimax",

            "Semana 5 - Sistema híbrido",

            "Semana 7 - Representaciones"
        ]
    })


# ==========================================================
# MANEJO DE ERROR 404
# ==========================================================

@app.errorhandler(404)
def pagina_no_encontrada(
    error
):

    return jsonify({
        "error":
            "Ruta no encontrada."
    }), 404


# ==========================================================
# MANEJO DE ERROR 500
# ==========================================================

@app.errorhandler(500)
def error_interno(
    error
):

    return jsonify({
        "error":
            "Se presentó un error "
            "interno en el servidor."
    }), 500


# ==========================================================
# EJECUTAR SERVIDOR
# ==========================================================

if __name__ == "__main__":

    print()

    print(
        "=" * 55
    )

    print(
        f"HIS_IA WEB v{VERSION}"
    )

    print(
        "=" * 55
    )

    print(
        "Servidor iniciado correctamente."
    )

    print(
        "Dirección:"
    )

    print(
        "http://127.0.0.1:5001"
    )

    print(
        "=" * 55
    )

    print()


    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )