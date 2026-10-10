from pathlib import Path
from uuid import uuid4
import sys

import numpy as np
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    send_from_directory
)
from werkzeug.utils import secure_filename


# ==========================================================
# RUTAS BASE
# ==========================================================

WEB_DIR = Path(__file__).resolve().parent
PROJECT_DIR = WEB_DIR.parent
PROJECT_SRC_DIR = PROJECT_DIR / "src"
SEMESTER_ROOT = PROJECT_DIR.parent

UPLOAD_DIR = WEB_DIR / "uploads"
ARTIFACTS_DIR = SEMESTER_ROOT / "artifacts"
DATA_DIR = SEMESTER_ROOT / "data"
REPORTS_DIR = SEMESTER_ROOT / "reports"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

if str(PROJECT_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC_DIR))


# ==========================================================
# IMPORTAR HIS_IA
# ==========================================================

from his_ia import (  # noqa: E402
    VERSION,
    clasificar_texto,
    entrenar_modelo_prioridad,
    evaluar_prioridad,
    planificar_revision,
    priorizar_pacientes_minimax,
    analizar_representaciones,
    SistemaHibridoHIS,
    analizar_archivo_semana8,
    obtener_resumen_semana8,
    analizar_archivo_semana9,
    generar_reporte_semana5
)


# ==========================================================
# FLASK
# ==========================================================

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


# ==========================================================
# CONFIGURACIÓN DE ARCHIVOS
# ==========================================================

ALLOWED_WEEK8 = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp"
}

ALLOWED_WEEK9 = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff"
}


# ==========================================================
# ESTADO GLOBAL
# ==========================================================

MODELO_PRIORIDAD = None
PRECISION_PRIORIDAD = None
MATRIZ_PRIORIDAD = None
ERROR_MODELO_PRIORIDAD = None

SISTEMA_HIBRIDO = None
ERROR_SISTEMA_HIBRIDO = None


# ==========================================================
# INICIALIZAR SISTEMAS
# ==========================================================

def inicializar_sistemas():
    global MODELO_PRIORIDAD
    global PRECISION_PRIORIDAD
    global MATRIZ_PRIORIDAD
    global ERROR_MODELO_PRIORIDAD
    global SISTEMA_HIBRIDO
    global ERROR_SISTEMA_HIBRIDO

    try:
        (
            MODELO_PRIORIDAD,
            PRECISION_PRIORIDAD,
            MATRIZ_PRIORIDAD
        ) = entrenar_modelo_prioridad()

        ERROR_MODELO_PRIORIDAD = None

    except Exception as error:
        MODELO_PRIORIDAD = None
        PRECISION_PRIORIDAD = None
        MATRIZ_PRIORIDAD = None
        ERROR_MODELO_PRIORIDAD = str(error)

    try:
        SISTEMA_HIBRIDO = SistemaHibridoHIS()
        ERROR_SISTEMA_HIBRIDO = None

    except Exception as error:
        SISTEMA_HIBRIDO = None
        ERROR_SISTEMA_HIBRIDO = str(error)


inicializar_sistemas()


# ==========================================================
# UTILIDADES
# ==========================================================

def respuesta_ok(**kwargs):
    data = {"ok": True}
    data.update(kwargs)
    return jsonify(data)


def respuesta_error(mensaje, status=400, **kwargs):
    data = {
        "ok": False,
        "error": mensaje
    }
    data.update(kwargs)
    return jsonify(data), status


def extension_permitida(nombre_archivo, permitidas):
    extension = Path(nombre_archivo).suffix.lower()
    return extension in permitidas


def guardar_upload(archivo, permitidas):
    if not archivo:
        raise ValueError("No se recibió ningún archivo.")

    nombre_original = archivo.filename or ""

    if not nombre_original.strip():
        raise ValueError("El archivo no tiene nombre válido.")

    if not extension_permitida(nombre_original, permitidas):
        raise ValueError(
            "Formato no permitido para este módulo."
        )

    extension = Path(nombre_original).suffix.lower()
    nombre_seguro = secure_filename(
        Path(nombre_original).stem
    )

    nombre_final = (
        f"{nombre_seguro}_{uuid4().hex[:8]}{extension}"
    )

    ruta_destino = UPLOAD_DIR / nombre_final

    archivo.save(ruta_destino)

    return ruta_destino


def convertir_booleano(valor):
    if isinstance(valor, bool):
        return valor

    if isinstance(valor, (int, float)):
        return valor == 1

    texto = str(valor).strip().lower()

    return texto in {
        "1",
        "true",
        "si",
        "sí",
        "s",
        "on",
        "yes"
    }


def obtener_json_o_form(clave, default=None):
    if request.is_json:
        data = request.get_json(silent=True) or {}
        return data.get(clave, default)

    return request.form.get(clave, default)


def serializar(obj):
    if isinstance(obj, dict):
        return {
            str(clave): serializar(valor)
            for clave, valor in obj.items()
        }

    if isinstance(obj, (list, tuple)):
        return [serializar(item) for item in obj]

    if isinstance(obj, Path):
        return str(obj)

    if isinstance(obj, np.ndarray):
        return obj.tolist()

    if isinstance(obj, np.generic):
        return obj.item()

    return obj


def ruta_publica_desde_local(ruta):
    try:
        ruta = Path(ruta).resolve()
    except Exception:
        return None

    directorios = [
        ("uploads", UPLOAD_DIR, "/uploads/"),
        ("artifacts", ARTIFACTS_DIR, "/files/artifacts/"),
        ("data", DATA_DIR, "/files/data/"),
        ("reports", REPORTS_DIR, "/files/reports/")
    ]

    for _, base_dir, url_base in directorios:
        try:
            relativo = ruta.relative_to(base_dir.resolve())
            return url_base + str(relativo).replace("\\", "/")
        except Exception:
            continue

    return None


def enriquecer_urls(data):
    if isinstance(data, dict):
        nuevo = {}

        for clave, valor in data.items():
            valor_procesado = enriquecer_urls(valor)
            nuevo[clave] = valor_procesado

            if isinstance(valor, (str, Path)):
                url = ruta_publica_desde_local(valor)
                if url:
                    nuevo[f"{clave}_url"] = url

        return nuevo

    if isinstance(data, list):
        return [enriquecer_urls(item) for item in data]

    return data


def construir_paciente(payload):
    campos = [
        "dolor_intenso",
        "dificultad_respiratoria",
        "sangrado_activo",
        "perdida_movilidad",
        "alteracion_conciencia",
        "trauma",
        "requiere_soporte"
    ]

    paciente = {
        "motivo_consulta": payload.get(
            "motivo_consulta",
            "No especificado"
        )
    }

    for campo in campos:
        paciente[campo] = convertir_booleano(
            payload.get(campo, False)
        )

    return paciente


def obtener_resultados_semana5():
    if SISTEMA_HIBRIDO is None:
        raise RuntimeError(
            "El sistema híbrido no está disponible."
        )

    consultas = [
        "Necesito revisar el resultado de creatinina del paciente.",
        "Hay una resonancia pendiente de revisión.",
        "Se requiere consultar los antecedentes y evolución de la historia clínica.",
        "El paciente tiene medicamentos y tratamiento registrados.",
        "¿Qué información debería revisar primero?"
    ]

    resultados = []

    for consulta in consultas:
        resultados.append(
            SISTEMA_HIBRIDO.analizar_consulta(consulta)
        )

    generar_reporte_semana5(resultados)

    ruta_reporte = PROJECT_DIR / "reports" / "semana05.md"

    return {
        "consultas": resultados,
        "reporte": str(ruta_reporte)
    }


# ==========================================================
# RUTAS DE ARCHIVOS
# ==========================================================

@app.route("/uploads/<path:filename>")
def servir_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@app.route("/files/artifacts/<path:filename>")
def servir_artifacts(filename):
    return send_from_directory(ARTIFACTS_DIR, filename)


@app.route("/files/data/<path:filename>")
def servir_data(filename):
    return send_from_directory(DATA_DIR, filename)


@app.route("/files/reports/<path:filename>")
def servir_reports(filename):
    return send_from_directory(REPORTS_DIR, filename)


# ==========================================================
# INTERFAZ PRINCIPAL
# ==========================================================

@app.route("/")
def index():
    return render_template(
        "index.html",
        version=VERSION
    )


# ==========================================================
# ESTADO GENERAL
# ==========================================================

@app.route("/api/estado", methods=["GET"])
def api_estado():
    estado = {
        "version": VERSION,
        "modelo_prioridad": {
            "disponible": MODELO_PRIORIDAD is not None,
            "precision": PRECISION_PRIORIDAD,
            "matriz": (
                MATRIZ_PRIORIDAD.tolist()
                if MATRIZ_PRIORIDAD is not None
                else None
            ),
            "error": ERROR_MODELO_PRIORIDAD
        },
        "sistema_hibrido": {
            "disponible": SISTEMA_HIBRIDO is not None,
            "error": ERROR_SISTEMA_HIBRIDO
        }
    }

    try:
        resumen8 = obtener_resumen_semana8()
        estado["semana8"] = {
            "disponible": True,
            "resumen": serializar(resumen8)
        }
    except Exception as error:
        estado["semana8"] = {
            "disponible": False,
            "error": str(error)
        }

    estado["semana9"] = {
        "disponible": callable(analizar_archivo_semana9)
    }

    return respuesta_ok(estado=estado)


# ==========================================================
# SEMANA 3 - CLASIFICACIÓN DE TEXTO
# ==========================================================

@app.route("/api/clasificar", methods=["POST"])
def api_clasificar():
    texto = obtener_json_o_form("texto", "")

    if not str(texto).strip():
        return respuesta_error(
            "Debe ingresar un texto para analizar."
        )

    resultado = clasificar_texto(texto)

    return respuesta_ok(
        resultado=serializar(resultado)
    )


# ==========================================================
# SEMANA 2 - PRIORIDAD
# ==========================================================

@app.route("/api/prioridad", methods=["POST"])
def api_prioridad():
    if MODELO_PRIORIDAD is None:
        return respuesta_error(
            "El modelo de prioridad no está disponible.",
            status=500,
            detalle=ERROR_MODELO_PRIORIDAD
        )

    try:
        edad = int(
            obtener_json_o_form("edad", 0)
        )

        documentos = int(
            obtener_json_o_form(
                "documentos_pendientes",
                obtener_json_o_form("documentos", 0)
            )
        )

        resultados = int(
            obtener_json_o_form(
                "resultados_pendientes",
                obtener_json_o_form("resultados", 0)
            )
        )

        imagenes = int(
            obtener_json_o_form(
                "imagenes_pendientes",
                obtener_json_o_form("imagenes", 0)
            )
        )

        prioridad = evaluar_prioridad(
            MODELO_PRIORIDAD,
            edad,
            documentos,
            resultados,
            imagenes
        )

        return respuesta_ok(
            resultado={
                "edad": edad,
                "documentos_pendientes": documentos,
                "resultados_pendientes": resultados,
                "imagenes_pendientes": imagenes,
                "prioridad": prioridad,
                "precision_modelo": PRECISION_PRIORIDAD,
                "matriz_modelo": (
                    MATRIZ_PRIORIDAD.tolist()
                    if MATRIZ_PRIORIDAD is not None
                    else None
                )
            }
        )

    except ValueError:
        return respuesta_error(
            "Los valores deben ser numéricos."
        )


# ==========================================================
# SEMANA 4 - A*
# ==========================================================

@app.route("/api/astar", methods=["POST"])
def api_astar():
    payload = request.get_json(silent=True) or {}

    elementos = payload.get("elementos", [])

    if not isinstance(elementos, list):
        return respuesta_error(
            "Los elementos deben enviarse en una lista."
        )

    try:
        resultado = planificar_revision(elementos)

        return respuesta_ok(
            resultado=serializar(resultado)
        )

    except Exception as error:
        return respuesta_error(str(error))


# ==========================================================
# SEMANA 4 - MINIMAX
# ==========================================================

@app.route("/api/minimax", methods=["POST"])
def api_minimax():
    payload = request.get_json(silent=True) or {}

    paciente1 = construir_paciente(
        payload.get("paciente1", {})
    )

    paciente2 = construir_paciente(
        payload.get("paciente2", {})
    )

    try:
        resultado = priorizar_pacientes_minimax(
            paciente1,
            paciente2
        )

        return respuesta_ok(
            resultado=serializar(resultado)
        )

    except Exception as error:
        return respuesta_error(str(error))


# ==========================================================
# SEMANA 7 - REPRESENTACIONES
# ==========================================================

@app.route("/api/semana7", methods=["POST"])
def api_semana7():
    payload = request.get_json(silent=True) or {}

    try:
        caso = {
            "motivo_consulta": payload.get(
                "motivo_consulta",
                ""
            ),
            "temperatura": float(payload.get("temperatura")),
            "latidos": int(payload.get("latidos")),
            "presion": int(payload.get("presion"))
        }

        resultado = analizar_representaciones(caso)

        return respuesta_ok(
            resultado=serializar(resultado)
        )

    except Exception as error:
        return respuesta_error(
            f"No fue posible analizar la consulta: {error}"
        )


# ==========================================================
# SEMANA 8 - ARCHIVO
# ==========================================================

@app.route("/api/semana8/archivo", methods=["POST"])
def api_semana8_archivo():
    try:
        archivo = request.files.get("archivo")

        ruta_archivo = guardar_upload(
            archivo,
            ALLOWED_WEEK8
        )

        resultado = analizar_archivo_semana8(ruta_archivo)
        resultado = serializar(resultado)
        resultado = enriquecer_urls(resultado)

        return respuesta_ok(
            resultado=resultado
        )

    except Exception as error:
        return respuesta_error(str(error))


@app.route("/api/semana8/resumen", methods=["GET"])
def api_semana8_resumen():
    try:
        resultado = obtener_resumen_semana8()
        resultado = serializar(resultado)
        resultado = enriquecer_urls(resultado)

        return respuesta_ok(
            resultado=resultado
        )

    except Exception as error:
        return respuesta_error(str(error), status=500)


# ==========================================================
# SEMANA 9 - VISIÓN ARTIFICIAL
# ==========================================================

@app.route("/api/semana9/imagen", methods=["POST"])
def api_semana9_imagen():
    try:
        archivo = request.files.get("archivo")

        ruta_archivo = guardar_upload(
            archivo,
            ALLOWED_WEEK9
        )

        sigma = float(
            request.form.get("sigma", 2.0)
        )

        area_minima = int(
            request.form.get("area_minima", 20)
        )

        resultado = analizar_archivo_semana9(
            ruta_archivo,
            sigma=sigma,
            area_minima=area_minima
        )

        resultado = serializar(resultado)
        resultado = enriquecer_urls(resultado)

        return respuesta_ok(
            resultado=resultado
        )

    except Exception as error:
        return respuesta_error(str(error))


# ==========================================================
# ASISTENTE HIS_IA
# ==========================================================

@app.route("/api/asistente", methods=["POST"])
def api_asistente():
    if SISTEMA_HIBRIDO is None:
        return respuesta_error(
            "El sistema híbrido no está disponible.",
            status=500,
            detalle=ERROR_SISTEMA_HIBRIDO
        )

    consulta = obtener_json_o_form("consulta", "")

    if not str(consulta).strip():
        return respuesta_error(
            "Debe ingresar una consulta."
        )

    try:
        resultado = SISTEMA_HIBRIDO.analizar_consulta(
            consulta
        )

        return respuesta_ok(
            resultado=serializar(resultado)
        )

    except Exception as error:
        return respuesta_error(str(error))


# ==========================================================
# VALIDACIÓN SEMANA 5
# ==========================================================

@app.route("/api/semana5/validar", methods=["POST"])
def api_semana5_validar():
    try:
        resultado = obtener_resultados_semana5()
        resultado = serializar(resultado)
        resultado = enriquecer_urls(resultado)

        return respuesta_ok(
            resultado=resultado
        )

    except Exception as error:
        return respuesta_error(str(error), status=500)


# ==========================================================
# MAIN
# ==========================================================



# ==========================================================
# SEMANA 10
# API - CARACTERÍSTICAS DE IMAGEN
# ==========================================================

@app.route(
    "/api/semana10/imagen",
    methods=["POST"]
)
def api_semana10_imagen():

    try:

        # ==================================================
        # VALIDAR ARCHIVO
        # ==================================================

        if "archivo" not in request.files:

            return jsonify(
                {
                    "success":
                        False,

                    "error":
                        "No se recibió ninguna imagen."
                }
            ), 400


        archivo = request.files[
            "archivo"
        ]


        if not archivo.filename:

            return jsonify(
                {
                    "success":
                        False,

                    "error":
                        "La imagen no tiene nombre."
                }
            ), 400


        # ==================================================
        # VALIDAR EXTENSIÓN
        # ==================================================

        extension = (
            Path(
                archivo.filename
            )
            .suffix
            .lower()
        )


        extensiones_permitidas = {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
            ".bmp",
            ".tif",
            ".tiff"
        }


        if extension not in extensiones_permitidas:

            return jsonify(
                {
                    "success":
                        False,

                    "error":
                        (
                            "Formato no permitido. "
                            "Use PNG, JPG, JPEG, WEBP, "
                            "BMP, TIF o TIFF."
                        )
                }
            ), 400


        # ==================================================
        # PARÁMETROS
        # ==================================================

        try:

            area_minima = int(
                request.form.get(
                    "area_minima",
                    50
                )
            )

        except ValueError:

            return jsonify(
                {
                    "success":
                        False,

                    "error":
                        "El área mínima no es válida."
                }
            ), 400


        try:

            radio_lbp = int(
                request.form.get(
                    "radio_lbp",
                    2
                )
            )

        except ValueError:

            return jsonify(
                {
                    "success":
                        False,

                    "error":
                        "El radio LBP no es válido."
                }
            ), 400


        if area_minima < 1:

            return jsonify(
                {
                    "success":
                        False,

                    "error":
                        (
                            "El área mínima debe ser "
                            "mayor o igual a 1."
                        )
                }
            ), 400


        if radio_lbp < 1:

            return jsonify(
                {
                    "success":
                        False,

                    "error":
                        (
                            "El radio LBP debe ser "
                            "mayor o igual a 1."
                        )
                }
            ), 400


        # ==================================================
        # IMPORTAR MOTOR HIS_IA
        # ==================================================

        from his_ia import (
            analizar_archivo_semana10
        )


        # ==================================================
        # PREPARAR CARPETA
        # ==================================================

        carpeta_cargas = (
            Path(__file__)
            .resolve()
            .parent
            / "uploads"
            / "semana10"
        )


        carpeta_cargas.mkdir(
            parents=True,
            exist_ok=True
        )


        # ==================================================
        # NOMBRE SEGURO
        # ==================================================

        from werkzeug.utils import (
            secure_filename
        )

        from uuid import uuid4


        nombre_original = (
            secure_filename(
                archivo.filename
            )
        )


        nombre_guardado = (
            f"{uuid4().hex[:12]}_"
            f"{nombre_original}"
        )


        ruta_imagen = (
            carpeta_cargas
            /
            nombre_guardado
        )


        archivo.save(
            ruta_imagen
        )


        # ==================================================
        # EJECUTAR SEMANA 10
        # ==================================================

        respuesta = (
            analizar_archivo_semana10(
                ruta_imagen=ruta_imagen,
                area_minima=area_minima,
                radio_lbp=radio_lbp
            )
        )


        # ==================================================
        # RESPUESTA
        # ==================================================

        return jsonify(
            {
                "success":
                    True,

                "resultado":
                    respuesta,

                "upload":
                    {
                        "original_name":
                            archivo.filename,

                        "stored_name":
                            nombre_guardado
                    }
            }
        )


    except Exception as error:

        return jsonify(
            {
                "success":
                    False,

                "error":
                    str(
                        error
                    )
            }
        ), 500





# ==========================================================
# SEMANA 10
# SERVIR HISTOGRAMA GENERADO
# ==========================================================

@app.route(
    "/api/semana10/histograma",
    methods=["GET"]
)
def api_semana10_histograma():

    try:

        from flask import send_file


        # app.py se encuentra en:
        # ia_semestre/proyecto_his/web/app.py
        #
        # Los artefactos de Semana 10 se generan en:
        # ia_semestre/artifacts/

        project_root = (
            Path(__file__)
            .resolve()
            .parents[2]
        )


        ruta_histograma = (
            project_root
            / "artifacts"
            / "semana10_histograma.png"
        )


        if not ruta_histograma.exists():

            return jsonify(
                {
                    "success":
                        False,

                    "error":
                        (
                            "El histograma de Semana 10 "
                            "todavía no ha sido generado."
                        )
                }
            ), 404


        return send_file(
            ruta_histograma,
            mimetype="image/png",
            max_age=0
        )


    except Exception as error:

        return jsonify(
            {
                "success":
                    False,

                "error":
                    str(
                        error
                    )
            }
        ), 500



if __name__ == "__main__":
    print("\n" + "=" * 55)
    print(f"HIS_IA WEB v{VERSION}")
    print("=" * 55)
    print("Servidor iniciado correctamente.")
    print("Dirección:")
    print("http://127.0.0.1:5001")
    print("=" * 55 + "\n")

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )