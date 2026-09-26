from pathlib import Path
import sys
import uuid

from flask import (
    Flask,
    jsonify,
    render_template,
    request
)

from werkzeug.utils import secure_filename


# ==========================================================
# RUTAS DEL PROYECTO
# ==========================================================

WEB_DIR = Path(
    __file__
).resolve().parent

PROYECTO_HIS_DIR = (
    WEB_DIR.parent
)

SRC_DIR = (
    PROYECTO_HIS_DIR
    / "src"
)

UPLOADS_DIR = (
    WEB_DIR
    / "uploads"
)


# ==========================================================
# AGREGAR SRC AL PATH
# ==========================================================

if str(
    SRC_DIR
) not in sys.path:

    sys.path.insert(
        0,
        str(
            SRC_DIR
        )
    )


# ==========================================================
# IMPORTAR SISTEMA HIS_IA
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
    analizar_archivo_semana8,
    obtener_resumen_semana8
)


# ==========================================================
# CONFIGURACIÓN FLASK
# ==========================================================

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)


app.config[
    "MAX_CONTENT_LENGTH"
] = (
    15
    * 1024
    * 1024
)


UPLOADS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================================
# EXTENSIONES PERMITIDAS SEMANA 8
# ==========================================================

EXTENSIONES_PERMITIDAS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp"
}


# ==========================================================
# SISTEMA HIS
# ==========================================================

sistema = SistemaHibridoHIS()


# ==========================================================
# UTILIDADES
# ==========================================================

def respuesta_error(
    mensaje,
    codigo=400,
    detalle=None
):

    respuesta = {
        "ok":
            False,

        "error":
            str(
                mensaje
            )
    }


    if detalle is not None:

        respuesta[
            "detalle"
        ] = str(
            detalle
        )


    return (
        jsonify(
            respuesta
        ),
        codigo
    )


def extension_valida(
    nombre_archivo
):

    extension = (
        Path(
            nombre_archivo
        )
        .suffix
        .lower()
    )


    return (
        extension
        in EXTENSIONES_PERMITIDAS
    )


def guardar_archivo_semana8(
    archivo
):

    nombre_original = (
        archivo.filename
        or ""
    )


    nombre_seguro = (
        secure_filename(
            nombre_original
        )
    )


    if not nombre_seguro:

        raise ValueError(
            "El archivo no tiene un nombre válido."
        )


    extension = (
        Path(
            nombre_seguro
        )
        .suffix
        .lower()
    )


    if (
        extension
        not in EXTENSIONES_PERMITIDAS
    ):

        raise ValueError(
            (
                "Formato no permitido. "
                "Utilice PDF, PNG, JPG, "
                "JPEG o WEBP."
            )
        )


    identificador = (
        uuid.uuid4()
        .hex[:12]
    )


    nombre_guardado = (
        f"{identificador}_"
        f"{nombre_seguro}"
    )


    ruta_archivo = (
        UPLOADS_DIR
        / nombre_guardado
    )


    archivo.save(
        ruta_archivo
    )


    return {
        "nombre_original":
            nombre_original,

        "nombre_guardado":
            nombre_guardado,

        "ruta":
            ruta_archivo,

        "extension":
            extension
    }


# ==========================================================
# PÁGINA PRINCIPAL
# ==========================================================

@app.route(
    "/",
    methods=[
        "GET"
    ]
)
def inicio():

    return render_template(
        "index.html",
        version=VERSION
    )


# ==========================================================
# INFORMACIÓN DEL SISTEMA
# ==========================================================

@app.route(
    "/api/sistema",
    methods=[
        "GET"
    ]
)
def api_sistema():

    return jsonify(
        {
            "ok":
                True,

            "nombre":
                "HIS_IA",

            "version":
                VERSION,

            "semana8":
                True,

            "interpretacion_clinica":
                True
        }
    )


# ==========================================================
# SEMANAS 2 Y 3
# ANÁLISIS DE INFORMACIÓN CLÍNICA
# ==========================================================

@app.route(
    "/api/analizar",
    methods=[
        "POST"
    ]
)
def api_analizar():

    try:

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

            return respuesta_error(
                (
                    "Debe ingresar información "
                    "para realizar el análisis."
                )
            )


        resultado = (
            clasificar_texto(
                texto
            )
        )


        return jsonify(
            {
                "ok":
                    True,

                "resultado":
                    resultado
            }
        )


    except Exception as error:

        return respuesta_error(
            "No se pudo realizar el análisis.",
            500,
            error
        )


# ==========================================================
# PRIORIDAD
# ==========================================================

@app.route(
    "/api/prioridad",
    methods=[
        "POST"
    ]
)
def api_prioridad():

    try:

        datos = (
            request.get_json(
                silent=True
            )
            or {}
        )


        # ==================================================
        # INTENTAR ENTRENAR/CARGAR MODELO
        # ==================================================

        entrenar_modelo_prioridad()


        # ==================================================
        # EVALUAR
        # ==================================================

        try:

            resultado = (
                evaluar_prioridad(
                    datos
                )
            )


        except TypeError:

            resultado = (
                evaluar_prioridad(
                    **datos
                )
            )


        return jsonify(
            {
                "ok":
                    True,

                "resultado":
                    resultado
            }
        )


    except Exception as error:

        return respuesta_error(
            (
                "No se pudo evaluar "
                "la prioridad."
            ),
            500,
            error
        )


# ==========================================================
# SEMANA 4
# A*
# ==========================================================

@app.route(
    "/api/revision",
    methods=[
        "POST"
    ]
)
def api_revision():

    try:

        datos = (
            request.get_json(
                silent=True
            )
            or {}
        )


        origen = (
            datos.get(
                "origen"
            )
        )


        destino = (
            datos.get(
                "destino"
            )
        )


        if (
            not origen
            or not destino
        ):

            return respuesta_error(
                (
                    "Debe indicar origen "
                    "y destino."
                )
            )


        try:

            resultado = (
                planificar_revision(
                    origen,
                    destino
                )
            )


        except TypeError:

            resultado = (
                planificar_revision(
                    datos
                )
            )


        return jsonify(
            {
                "ok":
                    True,

                "resultado":
                    resultado
            }
        )


    except Exception as error:

        return respuesta_error(
            (
                "No fue posible calcular "
                "la ruta de revisión."
            ),
            500,
            error
        )


# ==========================================================
# SEMANA 4
# MINIMAX
# ==========================================================

@app.route(
    "/api/priorizar-pacientes",
    methods=[
        "POST"
    ]
)
def api_priorizar_pacientes():

    try:

        datos = (
            request.get_json(
                silent=True
            )
            or {}
        )


        pacientes = (
            datos.get(
                "pacientes"
            )
        )


        if pacientes is None:

            pacientes = datos


        resultado = (
            priorizar_pacientes_minimax(
                pacientes
            )
        )


        return jsonify(
            {
                "ok":
                    True,

                "resultado":
                    resultado
            }
        )


    except Exception as error:

        return respuesta_error(
            (
                "No se pudo realizar "
                "la priorización Minimax."
            ),
            500,
            error
        )


# ==========================================================
# SEMANA 7
# REPRESENTACIONES
# ==========================================================

@app.route(
    "/api/reconocimiento",
    methods=[
        "POST"
    ]
)
def api_reconocimiento():

    try:

        datos = (
            request.get_json(
                silent=True
            )
            or {}
        )


        resultado = (
            analizar_representaciones(
                datos
            )
        )


        return jsonify(
            {
                "ok":
                    True,

                "resultado":
                    resultado
            }
        )


    except Exception as error:

        return respuesta_error(
            (
                "No se pudo realizar "
                "el análisis de Semana 7."
            ),
            500,
            error
        )


# ==========================================================
# SEMANA 8
# PROCESAR PDF O IMAGEN
# ==========================================================

@app.route(
    "/api/semana8/archivo",
    methods=[
        "POST"
    ]
)
def api_semana8_archivo():

    ruta_archivo = None


    try:

        # ==================================================
        # VALIDAR ARCHIVO
        # ==================================================

        if (
            "archivo"
            not in request.files
        ):

            return respuesta_error(
                (
                    "No se recibió ningún archivo. "
                    "El campo debe llamarse 'archivo'."
                )
            )


        archivo = (
            request.files[
                "archivo"
            ]
        )


        if (
            archivo is None
            or not archivo.filename
        ):

            return respuesta_error(
                "Debe seleccionar un archivo."
            )


        if not extension_valida(
            archivo.filename
        ):

            return respuesta_error(
                (
                    "Formato no permitido. "
                    "Los formatos admitidos son "
                    "PDF, PNG, JPG, JPEG y WEBP."
                )
            )


        # ==================================================
        # GUARDAR ARCHIVO
        # ==================================================

        informacion_archivo = (
            guardar_archivo_semana8(
                archivo
            )
        )


        ruta_archivo = (
            informacion_archivo[
                "ruta"
            ]
        )


        # ==================================================
        # ANALIZAR
        # ==================================================

        analisis = (
            analizar_archivo_semana8(
                str(
                    ruta_archivo
                )
            )
        )


        # ==================================================
        # VALIDAR RESPUESTA INTERNA
        # ==================================================

        if analisis is None:

            return respuesta_error(
                (
                    "El módulo de Semana 8 "
                    "no devolvió resultados."
                ),
                500
            )


        # ==================================================
        # ANALIZAR_ARCHIVO_SEMANA8 PUEDE DEVOLVER
        #
        # {
        #     "tipo": "pdf",
        #     "resultado": {...}
        # }
        #
        # O UN RESULTADO DIRECTO.
        #
        # ESTE BLOQUE HACE EL ENDPOINT TOLERANTE
        # A AMBOS CASOS.
        # ==================================================

        if (
            isinstance(
                analisis,
                dict
            )
            and "resultado"
            in analisis
        ):

            tipo = (
                analisis.get(
                    "tipo"
                )
            )

            resultado = (
                analisis.get(
                    "resultado"
                )
            )


        else:

            extension = (
                informacion_archivo[
                    "extension"
                ]
            )


            tipo = (
                "pdf"
                if extension == ".pdf"
                else "imagen"
            )


            resultado = (
                analisis
            )


        if resultado is None:

            return respuesta_error(
                (
                    "El procesamiento terminó, "
                    "pero no se obtuvo un resultado."
                ),
                500
            )


        # ==================================================
        # IMPORTANTE
        #
        # NO SE ELIMINA interpretacion_clinica.
        #
        # Si el archivo es PDF, resultado puede contener:
        #
        # resultado[
        #     "interpretacion_clinica"
        # ]
        #
        # Ese diccionario se envía completo al frontend.
        # ==================================================

        respuesta = {

            "ok":
                True,

            "nombre_original":
                informacion_archivo[
                    "nombre_original"
                ],

            "nombre_guardado":
                informacion_archivo[
                    "nombre_guardado"
                ],

            "tipo":
                tipo,

            "resultado":
                resultado
        }


        # ==================================================
        # INFORMACIÓN AUXILIAR
        # ==================================================
        #
        # Esto facilita que app.js sepa si existe
        # interpretación sin recorrer todo el resultado.
        #
        # No reemplaza resultado["interpretacion_clinica"].
        # ==================================================

        if (
            isinstance(
                resultado,
                dict
            )
        ):

            interpretacion = (
                resultado.get(
                    "interpretacion_clinica"
                )
            )


            respuesta[
                "tiene_interpretacion_clinica"
            ] = bool(
                interpretacion
            )


        return jsonify(
            respuesta
        )


    except ValueError as error:

        return respuesta_error(
            error,
            400
        )


    except Exception as error:

        return respuesta_error(
            (
                "No fue posible procesar "
                "el archivo de Semana 8."
            ),
            500,
            error
        )


# ==========================================================
# SEMANA 8
# RESUMEN DE EVIDENCIA
# ==========================================================

@app.route(
    "/api/semana8/resumen",
    methods=[
        "GET"
    ]
)
def api_semana8_resumen():

    try:

        resumen = (
            obtener_resumen_semana8()
        )


        return jsonify(
            {
                "ok":
                    True,

                "resultado":
                    resumen
            }
        )


    except Exception as error:

        return respuesta_error(
            (
                "No se pudo obtener "
                "el resumen de Semana 8."
            ),
            500,
            error
        )


# ==========================================================
# ASISTENTE IA
# ==========================================================

@app.route(
    "/api/asistente",
    methods=[
        "POST"
    ]
)
def api_asistente():

    try:

        datos = (
            request.get_json(
                silent=True
            )
            or {}
        )


        mensaje = str(
            datos.get(
                "mensaje",
                ""
            )
        ).strip()


        if not mensaje:

            return respuesta_error(
                (
                    "Debe escribir un mensaje "
                    "para el asistente."
                )
            )


        # ==================================================
        # USAR SISTEMA HIS
        # ==================================================

        respuesta = None


        # Se intenta utilizar alguno de los métodos
        # disponibles del SistemaHibridoHIS.

        if hasattr(
            sistema,
            "responder"
        ):

            respuesta = (
                sistema.responder(
                    mensaje
                )
            )


        elif hasattr(
            sistema,
            "asistente"
        ):

            respuesta = (
                sistema.asistente(
                    mensaje
                )
            )


        elif hasattr(
            sistema,
            "procesar_consulta"
        ):

            respuesta = (
                sistema.procesar_consulta(
                    mensaje
                )
            )


        else:

            # ==================================================
            # RESPUESTA DE RESPALDO
            # ==================================================

            try:

                respuesta = (
                    clasificar_texto(
                        mensaje
                    )
                )

            except Exception:

                respuesta = (
                    "El asistente recibió el mensaje, "
                    "pero no existe un método de respuesta "
                    "configurado en SistemaHibridoHIS."
                )


        return jsonify(
            {
                "ok":
                    True,

                "respuesta":
                    respuesta
            }
        )


    except Exception as error:

        return respuesta_error(
            (
                "No fue posible procesar "
                "la consulta del asistente."
            ),
            500,
            error
        )


# ==========================================================
# ERROR 404
# ==========================================================

@app.errorhandler(
    404
)
def error_404(
    error
):

    if request.path.startswith(
        "/api/"
    ):

        return respuesta_error(
            "Ruta API no encontrada.",
            404
        )


    return (
        "Página no encontrada",
        404
    )


# ==========================================================
# ERROR ARCHIVO DEMASIADO GRANDE
# ==========================================================

@app.errorhandler(
    413
)
def error_413(
    error
):

    return respuesta_error(
        (
            "El archivo supera el tamaño máximo "
            "permitido de 15 MB."
        ),
        413
    )


# ==========================================================
# ERROR INTERNO
# ==========================================================

@app.errorhandler(
    500
)
def error_500(
    error
):

    return respuesta_error(
        "Error interno del servidor.",
        500
    )


# ==========================================================
# EJECUTAR APLICACIÓN
# ==========================================================

if __name__ == "__main__":

    print(
        "\n"
        + "=" * 60
    )

    print(
        "HIS_IA WEB"
    )

    print(
        "=" * 60
    )

    print(
        f"Versión: {VERSION}"
    )

    print(
        "Servidor: http://127.0.0.1:5001"
    )

    print(
        "Semana 8: Activa"
    )

    print(
        "Interpretación clínica: Activa"
    )

    print(
        "=" * 60
        + "\n"
    )


    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )