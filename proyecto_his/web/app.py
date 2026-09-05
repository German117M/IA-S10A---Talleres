from pathlib import Path
import sys

from flask import Flask, render_template, request, jsonify


# =========================================================
# CONEXIÓN CON HIS_IA
# =========================================================

WEB_DIR = Path(__file__).resolve().parent
PROJECT_DIR = WEB_DIR.parent
SRC_DIR = PROJECT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))

from his_ia import (
    clasificar_texto,
    entrenar_modelo_prioridad,
    planificar_revision,
    SistemaHibridoHIS,
)


# =========================================================
# APLICACIÓN WEB
# =========================================================

app = Flask(__name__)

modelo_prioridad = None
sistema_hibrido = None


def iniciar_modelos():
    global modelo_prioridad
    global sistema_hibrido

    try:
        modelo_prioridad = entrenar_modelo_prioridad()
    except Exception as error:
        print("Error cargando modelo de prioridad:", error)

    try:
        sistema_hibrido = SistemaHibridoHIS()
    except Exception as error:
        print("Error cargando sistema híbrido:", error)


iniciar_modelos()


# =========================================================
# PÁGINA PRINCIPAL
# =========================================================

@app.route("/")
def inicio():
    return render_template("index.html")


# =========================================================
# ANÁLISIS DE INFORMACIÓN
# =========================================================

@app.route("/api/analizar", methods=["POST"])
def analizar():

    datos = request.get_json()

    texto = datos.get("texto", "").strip()

    if not texto:
        return jsonify({
            "ok": False,
            "mensaje": "Ingrese información para analizar."
        }), 400

    principal, detectadas, puntuaciones = clasificar_texto(texto)

    return jsonify({
        "ok": True,
        "categoria": principal,
        "detectadas": detectadas,
        "puntuaciones": puntuaciones
    })


# =========================================================
# PRIORIDAD
# =========================================================

@app.route("/api/prioridad", methods=["POST"])
def prioridad():

    if modelo_prioridad is None:
        return jsonify({
            "ok": False,
            "mensaje": "El modelo de prioridad no está disponible."
        }), 500

    datos = request.get_json()

    try:
        edad = int(datos["edad"])
        documentos = int(datos["documentos"])
        resultados = int(datos["resultados"])
        imagenes = int(datos["imagenes"])

    except (ValueError, TypeError, KeyError):

        return jsonify({
            "ok": False,
            "mensaje": "Verifique los valores ingresados."
        }), 400

    import pandas as pd

    registro = pd.DataFrame([
        {
            "edad": edad,
            "documentos_pendientes": documentos,
            "resultados_pendientes": resultados,
            "imagenes_pendientes": imagenes
        }
    ])

    prediccion = modelo_prioridad.predict(registro)[0]

    resultado = (
        "Prioritaria"
        if prediccion == 1
        else "Normal"
    )

    return jsonify({
        "ok": True,
        "prioridad": resultado
    })


# =========================================================
# PLANIFICACIÓN DE REVISIÓN
# =========================================================

@app.route("/api/revision", methods=["POST"])
def revision():

    datos = request.get_json()

    elementos = datos.get("elementos", [])

    if not elementos:

        return jsonify({
            "ok": False,
            "mensaje": "Seleccione al menos un elemento."
        }), 400

    camino, costo = planificar_revision(elementos)

    return jsonify({
        "ok": True,
        "secuencia": camino,
        "costo": costo
    })


# =========================================================
# ASISTENTE HÍBRIDO
# =========================================================

@app.route("/api/asistente", methods=["POST"])
def asistente():

    if sistema_hibrido is None:

        return jsonify({
            "ok": False,
            "mensaje": "El asistente no está disponible."
        }), 500

    datos = request.get_json()

    consulta = datos.get("consulta", "").strip()

    if not consulta:

        return jsonify({
            "ok": False,
            "mensaje": "Escriba una consulta."
        }), 400

    resultado = sistema_hibrido.analizar_consulta(consulta)

    return jsonify({
        "ok": True,
        "consulta": resultado["consulta"],
        "reglas": resultado["reglas"],
        "evidencia": resultado["evidencia"],
        "similitud": round(resultado["similitud"], 3),
        "clase": resultado["clase"]
    })


# =========================================================
# EJECUCIÓN
# =========================================================

if __name__ == "__main__":

    print("\nHIS_IA WEB")
    print("Servidor iniciado correctamente.")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )