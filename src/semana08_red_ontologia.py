from pathlib import Path
from datetime import datetime
import pickle
import re
import sqlite3
import unicodedata

import fitz
import networkx as nx
import numpy as np
from PIL import Image

from sklearn.datasets import load_digits
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier


# ==========================================================
# CONFIGURACIÓN GENERAL
# ==========================================================

RANDOM_STATE = 42

ROOT = Path(__file__).resolve().parent.parent

ARTIFACTS = ROOT / "artifacts"
REPORTS = ROOT / "reports"
UPLOADS = ROOT / "proyecto_his" / "web" / "uploads"

MODEL_FILE = ARTIFACTS / "modelo_mlp.pkl"
DB_FILE = ARTIFACTS / "imagenes.db"
ONTOLOGY_FILE = ARTIFACTS / "ontologia.graphml"
REPORT_FILE = REPORTS / "semana08.md"


for carpeta in (
    ARTIFACTS,
    REPORTS,
    UPLOADS
):
    carpeta.mkdir(
        parents=True,
        exist_ok=True
    )


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
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


def limpiar_nombre_nodo(valor):

    valor = normalizar_texto(
        valor
    )

    valor = re.sub(
        r"[^a-z0-9]+",
        "_",
        valor
    )

    return (
        valor.strip("_")
        or "sin_dato"
    )


def fecha_actual():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# ==========================================================
# SEMANA 8
# 1. RED NEURONAL MLP
# ==========================================================

class ReconocedorDigitosMLP:

    def __init__(
        self,
        model_file=MODEL_FILE
    ):

        self.model_file = Path(
            model_file
        )

        self.modelo = None
        self.accuracy = None


    # ======================================================
    # ENTRENAR MODELO
    # ======================================================

    def entrenar(self):

        X, y = load_digits(
            return_X_y=True
        )

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


        self.modelo = MLPClassifier(
            hidden_layer_sizes=(64,),
            max_iter=400,
            random_state=RANDOM_STATE
        )


        self.modelo.fit(
            X_train,
            y_train
        )


        predicciones = (
            self.modelo.predict(
                X_test
            )
        )


        self.accuracy = float(
            accuracy_score(
                y_test,
                predicciones
            )
        )


        self.guardar_modelo()


        return {

            "accuracy":
                self.accuracy,

            "total_entrenamiento":
                int(
                    len(
                        X_train
                    )
                ),

            "total_prueba":
                int(
                    len(
                        X_test
                    )
                )
        }


    # ======================================================
    # GUARDAR MODELO
    # ======================================================

    def guardar_modelo(self):

        if self.modelo is None:

            raise RuntimeError(
                "No existe un modelo entrenado para guardar."
            )


        with self.model_file.open(
            "wb"
        ) as archivo:

            pickle.dump(
                {
                    "modelo":
                        self.modelo,

                    "accuracy":
                        self.accuracy
                },
                archivo
            )


    # ======================================================
    # CARGAR MODELO
    # ======================================================

    def cargar_modelo(self):

        if not self.model_file.exists():

            return self.entrenar()


        with self.model_file.open(
            "rb"
        ) as archivo:

            paquete = pickle.load(
                archivo
            )


        if (
            isinstance(
                paquete,
                dict
            )
            and "modelo" in paquete
        ):

            self.modelo = paquete[
                "modelo"
            ]

            self.accuracy = paquete.get(
                "accuracy"
            )

        else:

            self.modelo = paquete
            self.accuracy = None


        return {

            "accuracy":
                self.accuracy,

            "cargado_desde_archivo":
                True
        }


    def asegurar_modelo(self):

        if self.modelo is None:

            return self.cargar_modelo()


        return {

            "accuracy":
                self.accuracy,

            "cargado":
                True
        }


    # ======================================================
    # PREPROCESAR IMAGEN
    # ======================================================

    def preprocesar_imagen(
        self,
        ruta_imagen
    ):

        ruta_imagen = Path(
            ruta_imagen
        )


        if not ruta_imagen.exists():

            raise FileNotFoundError(
                f"No existe la imagen: {ruta_imagen}"
            )


        imagen = Image.open(
            ruta_imagen
        ).convert(
            "L"
        )


        arreglo = np.asarray(
            imagen,
            dtype=np.uint8
        )


        # El dataset load_digits utiliza
        # fondo oscuro y número claro.
        # Si la imagen tiene fondo blanco,
        # se invierte.

        if float(
            arreglo.mean()
        ) > 127:

            arreglo = (
                255
                - arreglo
            )


        # ==================================================
        # RECORTAR CONTENIDO
        # ==================================================

        mascara = (
            arreglo > 25
        )


        coordenadas = np.argwhere(
            mascara
        )


        if coordenadas.size:

            (
                y_min,
                x_min
            ) = coordenadas.min(
                axis=0
            )

            (
                y_max,
                x_max
            ) = coordenadas.max(
                axis=0
            )


            arreglo = arreglo[
                y_min:y_max + 1,
                x_min:x_max + 1
            ]


        # ==================================================
        # CENTRAR IMAGEN
        # ==================================================

        alto, ancho = (
            arreglo.shape
        )


        lado = max(
            alto,
            ancho
        )


        margen = max(
            2,
            int(
                lado * 0.20
            )
        )


        lienzo = np.zeros(
            (
                lado + 2 * margen,
                lado + 2 * margen
            ),
            dtype=np.uint8
        )


        y_inicio = (
            lienzo.shape[0]
            - alto
        ) // 2


        x_inicio = (
            lienzo.shape[1]
            - ancho
        ) // 2


        lienzo[
            y_inicio:y_inicio + alto,
            x_inicio:x_inicio + ancho
        ] = arreglo


        # ==================================================
        # REDIMENSIONAR A 8 X 8
        # ==================================================

        imagen_8x8 = (
            Image
            .fromarray(
                lienzo
            )
            .resize(
                (8, 8),
                Image.Resampling.LANCZOS
            )
        )


        matriz = np.asarray(
            imagen_8x8,
            dtype=float
        )


        matriz = np.clip(
            matriz,
            0,
            255
        )


        if matriz.max() > 0:

            matriz = (
                matriz
                / matriz.max()
            ) * 16.0


        return {

            "vector":
                matriz.reshape(
                    1,
                    -1
                ),

            "matriz_8x8":
                np.round(
                    matriz,
                    2
                ).tolist()
        }


    # ======================================================
    # PREDECIR IMAGEN
    # ======================================================

    def predecir_imagen(
        self,
        ruta_imagen
    ):

        self.asegurar_modelo()


        procesada = (
            self.preprocesar_imagen(
                ruta_imagen
            )
        )


        prediccion = int(
            self.modelo.predict(
                procesada[
                    "vector"
                ]
            )[0]
        )


        probabilidades = None
        confianza = None


        if hasattr(
            self.modelo,
            "predict_proba"
        ):

            probabilidades_array = (
                self.modelo.predict_proba(
                    procesada[
                        "vector"
                    ]
                )[0]
            )


            probabilidades = [
                float(
                    valor
                )

                for valor
                in probabilidades_array
            ]


            confianza = float(
                np.max(
                    probabilidades_array
                )
            )


        return {

            "archivo":
                Path(
                    ruta_imagen
                ).name,

            "prediccion":
                prediccion,

            "accuracy_modelo":
                self.accuracy,

            "confianza":
                confianza,

            "probabilidades":
                probabilidades,

            "matriz_8x8":
                procesada[
                    "matriz_8x8"
                ]
        }


    # ======================================================
    # PRUEBA CON DATASET
    # ======================================================

    def predecir_ejemplo_dataset(
        self,
        indice=15
    ):

        self.asegurar_modelo()


        X, y = load_digits(
            return_X_y=True
        )


        if (
            indice < 0
            or indice >= len(
                X
            )
        ):

            raise ValueError(
                f"El índice debe estar entre 0 y {len(X) - 1}."
            )


        prediccion = int(
            self.modelo.predict(
                [
                    X[
                        indice
                    ]
                ]
            )[0]
        )


        real = int(
            y[
                indice
            ]
        )


        return {

            "indice":
                int(
                    indice
                ),

            "real":
                real,

            "prediccion":
                prediccion,

            "coincide":
                prediccion
                == real,

            "accuracy_modelo":
                self.accuracy,

            "matriz_8x8":
                X[
                    indice
                ].reshape(
                    8,
                    8
                ).tolist()
        }


# ==========================================================
# SEMANA 8
# 2. PROCESADOR DE DOCUMENTOS MÉDICOS
# ==========================================================

class ProcesadorDocumentoMedico:

    EXAMENES = {

        "Glucosa": [
            "glucosa"
        ],

        "Creatinina": [
            "creatinina"
        ],

        "Hemoglobina": [
            "hemoglobina"
        ],

        "Hematocrito": [
            "hematocrito"
        ],

        "Leucocitos": [
            "leucocitos",
            "leucocito"
        ],

        "Plaquetas": [
            "plaquetas",
            "plaqueta"
        ],

        "Colesterol total": [
            "colesterol total",
            "colesterol"
        ],

        "Triglicéridos": [
            "trigliceridos",
            "triglicéridos"
        ],

        "TSH": [
            "tsh"
        ],

        "T4": [
            "t4",
            "tiroxina"
        ],

        "PCR": [
            "proteina c reactiva",
            "proteína c reactiva",
            "pcr"
        ],

        "Troponina": [
            "troponina"
        ]
    }


    UNIDADES = [

        "mg/dL",
        "g/dL",
        "mmol/L",
        "µmol/L",
        "umol/L",
        "U/L",
        "mUI/L",
        "µUI/mL",
        "uUI/mL",
        "ng/mL",
        "pg/mL",
        "10^3/uL",
        "10^6/uL",
        "%"
    ]


    # ======================================================
    # EXTRAER TEXTO DEL PDF
    # ======================================================

    def extraer_texto_pdf(
        self,
        ruta_pdf
    ):

        ruta_pdf = Path(
            ruta_pdf
        )


        if not ruta_pdf.exists():

            raise FileNotFoundError(
                f"No existe el PDF: {ruta_pdf}"
            )


        paginas = []


        with fitz.open(
            ruta_pdf
        ) as documento:

            for numero, pagina in enumerate(
                documento,
                start=1
            ):

                paginas.append(
                    {
                        "pagina":
                            numero,

                        "texto":
                            pagina.get_text(
                                "text"
                            ).strip()
                    }
                )


        return paginas


    # ======================================================
    # DETECTAR TIPO DE DOCUMENTO
    # ======================================================

    def detectar_tipo_documento(
        self,
        texto
    ):

        normalizado = normalizar_texto(
            texto
        )


        indicadores = [

            "hemoglobina",
            "hematocrito",
            "glucosa",
            "creatinina",
            "leucocitos",
            "plaquetas",
            "resultado",
            "valor de referencia",
            "rango de referencia",
            "laboratorio"
        ]


        coincidencias = sum(
            1
            for indicador
            in indicadores
            if indicador
            in normalizado
        )


        if coincidencias >= 2:

            return (
                "Resultado de laboratorio"
            )


        return (
            "Documento médico no clasificado"
        )


    # ======================================================
    # BUSCAR PRIMER RESULTADO
    # ======================================================

    def _buscar_primero(
        self,
        texto,
        patrones
    ):

        for patron in patrones:

            coincidencia = re.search(
                patron,
                texto,
                flags=(
                    re.IGNORECASE
                    | re.MULTILINE
                )
            )


            if coincidencia:

                return (
                    coincidencia
                    .group(1)
                    .strip()
                )


        return None


    # ======================================================
    # DATOS DEL PACIENTE
    # ======================================================

    def extraer_datos_paciente(
        self,
        texto
    ):

        nombre = (
            self._buscar_primero(
                texto,
                [
                    (
                        r"(?:paciente|nombre"
                        r"(?:\s+del\s+paciente)?)"
                        r"\s*[:\-]\s*([^\n\r]+)"
                    )
                ]
            )
        )


        identificacion = (
            self._buscar_primero(
                texto,
                [
                    (
                        r"(?:documento|"
                        r"identificaci[oó]n|"
                        r"c[eé]dula|"
                        r"cc|"
                        r"c\.c\.)"
                        r"\s*[:\-]?\s*"
                        r"(?:"
                        r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ.]+\s+"
                        r")*"
                        r"([0-9][0-9.\-\s]{4,24})"
                    )
                ]
            )
        )


        if identificacion:

            identificacion = (
                re.sub(
                    r"\D",
                    "",
                    identificacion
                )
                or None
            )


        fecha = (
            self._buscar_primero(
                texto,
                [
                    (
                        r"(?:fecha"
                        r"(?:\s+de\s+"
                        r"(?:toma|resultado|reporte))?)"
                        r"\s*[:\-]?\s*"
                        r"(\d{1,2}[/-]\d{1,2}"
                        r"[/-]\d{2,4})"
                    ),

                    (
                        r"(?:fecha"
                        r"(?:\s+de\s+"
                        r"(?:toma|resultado|reporte))?)"
                        r"\s*[:\-]?\s*"
                        r"(\d{4}-\d{2}-\d{2})"
                    )
                ]
            )
        )


        return {

            "nombre":
                nombre,

            "identificacion":
                identificacion,

            "fecha":
                fecha
        }


    # ======================================================
    # EXTRAER UNIDAD
    # ======================================================

    def _extraer_unidad(
        self,
        bloque
    ):

        for unidad in self.UNIDADES:

            coincidencia = re.search(
                re.escape(
                    unidad
                ),
                bloque,
                flags=re.IGNORECASE
            )


            if coincidencia:

                return coincidencia.group(
                    0
                )


        return None


    # ======================================================
    # EXTRAER RANGO DE REFERENCIA
    # ======================================================

    def _extraer_referencia(
        self,
        bloque
    ):

        patron = (
            r"(-?\d+(?:[.,]\d+)?)"
            r"\s*(?:-|–|a)\s*"
            r"(-?\d+(?:[.,]\d+)?)"
        )


        coincidencia = re.search(
            patron,
            bloque,
            flags=re.IGNORECASE
        )


        if not coincidencia:

            return None


        inicio = (
            coincidencia
            .group(1)
            .replace(
                ",",
                "."
            )
        )


        fin = (
            coincidencia
            .group(2)
            .replace(
                ",",
                "."
            )
        )


        return (
            f"{inicio} - {fin}"
        )


    # ======================================================
    # EXTRAER RESULTADO
    # ======================================================

    def _extraer_resultado_linea(
        self,
        bloque,
        referencia=None
    ):

        # Prioridad:
        # Resultado: 95

        coincidencia_resultado = re.search(
            (
                r"resultado"
                r"\s*[:\-]?\s*"
                r"(-?\d+(?:[.,]\d+)?)"
            ),
            bloque,
            flags=re.IGNORECASE
        )


        if coincidencia_resultado:

            return (
                coincidencia_resultado
                .group(1)
                .replace(
                    ",",
                    "."
                )
            )


        bloque_trabajo = bloque


        if referencia:

            for valor in referencia.split(
                " - "
            ):

                bloque_trabajo = re.sub(
                    re.escape(
                        valor
                    ),
                    " ",
                    bloque_trabajo,
                    count=1
                )


        numeros = re.findall(
            (
                r"(?<![A-Za-z0-9])"
                r"(-?\d+(?:[.,]\d+)?)"
                r"(?![A-Za-z0-9])"
            ),
            bloque_trabajo
        )


        if not numeros:

            return None


        return (
            numeros[
                0
            ].replace(
                ",",
                "."
            )
        )


    # ======================================================
    # VALIDAR SI APARECE OTRO EXAMEN
    # ======================================================

    def _linea_contiene_otro_examen(
        self,
        linea,
        examen_actual
    ):

        linea_normalizada = (
            normalizar_texto(
                linea
            )
        )


        for examen, aliases in (
            self.EXAMENES.items()
        ):

            if examen == examen_actual:

                continue


            if any(
                normalizar_texto(
                    alias
                )
                in linea_normalizada

                for alias
                in aliases
            ):

                return True


        return False


    # ======================================================
    # EXTRAER EXÁMENES
    # ======================================================

    def extraer_examenes(
        self,
        paginas
    ):

        resultados = []

        vistos = set()


        for pagina in paginas:

            numero_pagina = pagina[
                "pagina"
            ]


            lineas = pagina[
                "texto"
            ].splitlines()


            for indice, linea in enumerate(
                lineas
            ):

                linea_normalizada = (
                    normalizar_texto(
                        linea
                    )
                )


                for examen, aliases in (
                    self.EXAMENES.items()
                ):

                    encontrado = any(
                        normalizar_texto(
                            alias
                        )
                        in linea_normalizada

                        for alias
                        in aliases
                    )


                    if not encontrado:

                        continue


                    # ==========================================
                    # CREAR BLOQUE
                    # ==========================================
                    #
                    # Se leen hasta 3 líneas posteriores
                    # mientras no aparezca otro examen.
                    # ==========================================

                    bloque_lineas = [
                        linea
                    ]


                    for desplazamiento in range(
                        1,
                        4
                    ):

                        posicion = (
                            indice
                            + desplazamiento
                        )


                        if posicion >= len(
                            lineas
                        ):

                            break


                        siguiente = lineas[
                            posicion
                        ]


                        if self._linea_contiene_otro_examen(
                            siguiente,
                            examen
                        ):

                            break


                        bloque_lineas.append(
                            siguiente
                        )


                    bloque = " ".join(
                        bloque_lineas
                    )


                    unidad = (
                        self._extraer_unidad(
                            bloque
                        )
                    )


                    referencia = (
                        self._extraer_referencia(
                            bloque
                        )
                    )


                    resultado = (
                        self._extraer_resultado_linea(
                            bloque,
                            referencia
                        )
                    )


                    if resultado is None:

                        continue


                    clave = (

                        examen,
                        resultado,
                        unidad,
                        referencia,
                        numero_pagina
                    )


                    if clave in vistos:

                        continue


                    vistos.add(
                        clave
                    )


                    resultados.append(
                        {
                            "examen":
                                examen,

                            "resultado":
                                resultado,

                            "unidad":
                                unidad,

                            "referencia":
                                referencia,

                            "pagina":
                                numero_pagina
                        }
                    )


        return resultados


    # ======================================================
    # PROCESAR PDF
    # ======================================================

    def procesar_pdf(
        self,
        ruta_pdf
    ):

        paginas = (
            self.extraer_texto_pdf(
                ruta_pdf
            )
        )


        texto_total = "\n".join(
            pagina[
                "texto"
            ]

            for pagina
            in paginas
        )


        # ==================================================
        # PDF SIN TEXTO DIGITAL
        # ==================================================

        if len(
            texto_total.strip()
        ) < 30:

            return {

                "archivo":
                    Path(
                        ruta_pdf
                    ).name,

                "tipo_archivo":
                    "PDF",

                "numero_paginas":
                    len(
                        paginas
                    ),

                "tipo_documento":
                    (
                        "PDF sin texto "
                        "digital suficiente"
                    ),

                "paciente":
                    {
                        "nombre":
                            None,

                        "identificacion":
                            None,

                        "fecha":
                            None
                    },

                "examenes":
                    [],

                "requiere_ocr":
                    True,

                "texto_extraido":
                    texto_total
            }


        return {

            "archivo":
                Path(
                    ruta_pdf
                ).name,

            "tipo_archivo":
                "PDF",

            "numero_paginas":
                len(
                    paginas
                ),

            "tipo_documento":
                self.detectar_tipo_documento(
                    texto_total
                ),

            "paciente":
                self.extraer_datos_paciente(
                    texto_total
                ),

            "examenes":
                self.extraer_examenes(
                    paginas
                ),

            "requiere_ocr":
                False,

            "texto_extraido":
                texto_total
        }


# ==========================================================
# SEMANA 8
# 3. MOTOR DE INTERPRETACIÓN CLÍNICA ORIENTATIVA
# ==========================================================

class MotorInterpretacionClinica:

    def __init__(self):

        self.advertencia = (
            "Interpretación automática orientativa. "
            "Los hallazgos generados por HIS_IA no constituyen "
            "un diagnóstico médico y deben ser correlacionados "
            "con la historia clínica, síntomas, antecedentes "
            "y criterio de un profesional de la salud."
        )


    # ======================================================
    # CONVERTIR A NÚMERO
    # ======================================================

    def _convertir_numero(
        self,
        valor
    ):

        if valor is None:

            return None


        try:

            texto = str(
                valor
            ).strip().replace(
                ",",
                "."
            )


            coincidencia = re.search(
                r"-?\d+(?:\.\d+)?",
                texto
            )


            if not coincidencia:

                return None


            return float(
                coincidencia.group(
                    0
                )
            )


        except (
            TypeError,
            ValueError
        ):

            return None


    # ======================================================
    # PROCESAR REFERENCIA
    # ======================================================

    def _procesar_referencia(
        self,
        referencia
    ):

        if not referencia:

            return {

                "minimo":
                    None,

                "maximo":
                    None
            }


        texto = str(
            referencia
        ).replace(
            ",",
            "."
        )


        coincidencia = re.search(
            (
                r"(-?\d+(?:\.\d+)?)"
                r"\s*(?:-|–|a)\s*"
                r"(-?\d+(?:\.\d+)?)"
            ),
            texto,
            flags=re.IGNORECASE
        )


        if not coincidencia:

            return {

                "minimo":
                    None,

                "maximo":
                    None
            }


        return {

            "minimo":
                self._convertir_numero(
                    coincidencia.group(
                        1
                    )
                ),

            "maximo":
                self._convertir_numero(
                    coincidencia.group(
                        2
                    )
                )
        }


    # ======================================================
    # EVALUAR RESULTADO
    # ======================================================

    def evaluar_resultado(
        self,
        examen
    ):

        resultado_numerico = (
            self._convertir_numero(
                examen.get(
                    "resultado"
                )
            )
        )


        rango = (
            self._procesar_referencia(
                examen.get(
                    "referencia"
                )
            )
        )


        minimo = rango[
            "minimo"
        ]


        maximo = rango[
            "maximo"
        ]


        estado = (
            "NO EVALUABLE"
        )


        diferencia = None


        if (
            resultado_numerico is not None
            and minimo is not None
            and maximo is not None
        ):

            if resultado_numerico < minimo:

                estado = "BAJO"

                diferencia = (
                    resultado_numerico
                    - minimo
                )


            elif resultado_numerico > maximo:

                estado = "ALTO"

                diferencia = (
                    resultado_numerico
                    - maximo
                )


            else:

                estado = (
                    "DENTRO DE REFERENCIA"
                )

                diferencia = 0.0


        return {

            "examen":
                examen.get(
                    "examen",
                    "Examen no identificado"
                ),

            "resultado":
                examen.get(
                    "resultado"
                ),

            "resultado_numerico":
                resultado_numerico,

            "unidad":
                examen.get(
                    "unidad"
                ),

            "referencia":
                examen.get(
                    "referencia"
                ),

            "minimo_referencia":
                minimo,

            "maximo_referencia":
                maximo,

            "estado":
                estado,

            "diferencia":
                diferencia,

            "pagina":
                examen.get(
                    "pagina"
                )
        }


    # ======================================================
    # BUSCAR EXAMEN
    # ======================================================

    def _buscar_examen(
        self,
        resultados,
        nombre
    ):

        buscado = normalizar_texto(
            nombre
        )


        for resultado in resultados:

            if normalizar_texto(
                resultado.get(
                    "examen",
                    ""
                )
            ) == buscado:

                return resultado


        return None


    # ======================================================
    # CREAR CONDICIÓN
    # ======================================================

    def _crear_condicion(
        self,
        nombre,
        descripcion,
        examenes_relacionados,
        nivel="orientativo"
    ):

        return {

            "condicion":
                nombre,

            "descripcion":
                descripcion,

            "examenes_relacionados":
                examenes_relacionados,

            "nivel":
                nivel
        }


    # ======================================================
    # REGLAS CLÍNICAS
    # ======================================================

    def aplicar_reglas_clinicas(
        self,
        resultados
    ):

        condiciones = []


        glucosa = self._buscar_examen(
            resultados,
            "Glucosa"
        )


        creatinina = self._buscar_examen(
            resultados,
            "Creatinina"
        )


        hemoglobina = self._buscar_examen(
            resultados,
            "Hemoglobina"
        )


        hematocrito = self._buscar_examen(
            resultados,
            "Hematocrito"
        )


        leucocitos = self._buscar_examen(
            resultados,
            "Leucocitos"
        )


        plaquetas = self._buscar_examen(
            resultados,
            "Plaquetas"
        )


        colesterol = self._buscar_examen(
            resultados,
            "Colesterol total"
        )


        trigliceridos = self._buscar_examen(
            resultados,
            "Triglicéridos"
        )


        tsh = self._buscar_examen(
            resultados,
            "TSH"
        )


        t4 = self._buscar_examen(
            resultados,
            "T4"
        )


        pcr = self._buscar_examen(
            resultados,
            "PCR"
        )


        troponina = self._buscar_examen(
            resultados,
            "Troponina"
        )


        # ==================================================
        # GLUCOSA
        # ==================================================

        if (
            glucosa
            and glucosa[
                "estado"
            ] == "ALTO"
        ):

            condiciones.append(
                self._crear_condicion(

                    (
                        "Hallazgo compatible "
                        "con hiperglucemia"
                    ),

                    (
                        "La glucosa se encuentra por encima "
                        "del rango de referencia del documento. "
                        "El hallazgo puede relacionarse con una "
                        "alteración del metabolismo de la glucosa, "
                        "pero por sí solo no establece un "
                        "diagnóstico de diabetes."
                    ),

                    [
                        "Glucosa"
                    ]
                )
            )


        elif (
            glucosa
            and glucosa[
                "estado"
            ] == "BAJO"
        ):

            condiciones.append(
                self._crear_condicion(

                    (
                        "Hallazgo compatible "
                        "con hipoglucemia"
                    ),

                    (
                        "La glucosa está por debajo "
                        "del rango de referencia "
                        "del documento."
                    ),

                    [
                        "Glucosa"
                    ]
                )
            )


        # ==================================================
        # CREATININA
        # ==================================================

        if (
            creatinina
            and creatinina[
                "estado"
            ] == "ALTO"
        ):

            condiciones.append(
                self._crear_condicion(

                    (
                        "Posible alteración "
                        "de la función renal"
                    ),

                    (
                        "La creatinina está por encima del "
                        "rango de referencia. Este hallazgo "
                        "puede asociarse con alteraciones "
                        "de la función renal y requiere "
                        "correlación clínica."
                    ),

                    [
                        "Creatinina"
                    ]
                )
            )


        # ==================================================
        # HEMOGLOBINA + HEMATOCRITO
        # ==================================================

        if (
            hemoglobina
            and hematocrito
        ):

            if (
                hemoglobina[
                    "estado"
                ] == "BAJO"
                and hematocrito[
                    "estado"
                ] == "BAJO"
            ):

                condiciones.append(
                    self._crear_condicion(

                        (
                            "Patrón compatible "
                            "con anemia"
                        ),

                        (
                            "La hemoglobina y el hematocrito "
                            "están por debajo de sus rangos "
                            "de referencia. La combinación "
                            "puede ser compatible con un patrón "
                            "anémico y requiere valoración clínica."
                        ),

                        [
                            "Hemoglobina",
                            "Hematocrito"
                        ]
                    )
                )


            elif (
                hemoglobina[
                    "estado"
                ] == "ALTO"
                and hematocrito[
                    "estado"
                ] == "ALTO"
            ):

                condiciones.append(
                    self._crear_condicion(

                        (
                            "Elevación conjunta de "
                            "hemoglobina y hematocrito"
                        ),

                        (
                            "La hemoglobina y el hematocrito "
                            "están por encima de los rangos "
                            "proporcionados y requieren "
                            "correlación clínica."
                        ),

                        [
                            "Hemoglobina",
                            "Hematocrito"
                        ]
                    )
                )


        # ==================================================
        # PLAQUETAS
        # ==================================================

        if (
            plaquetas
            and plaquetas[
                "estado"
            ] == "BAJO"
        ):

            condiciones.append(
                self._crear_condicion(

                    "Trombocitopenia",

                    (
                        "El recuento de plaquetas está "
                        "por debajo del rango de referencia."
                    ),

                    [
                        "Plaquetas"
                    ]
                )
            )


        elif (
            plaquetas
            and plaquetas[
                "estado"
            ] == "ALTO"
        ):

            condiciones.append(
                self._crear_condicion(

                    "Trombocitosis",

                    (
                        "El recuento de plaquetas está "
                        "por encima del rango de referencia."
                    ),

                    [
                        "Plaquetas"
                    ]
                )
            )


        # ==================================================
        # LEUCOCITOS
        # ==================================================

        if (
            leucocitos
            and leucocitos[
                "estado"
            ] == "ALTO"
        ):

            condiciones.append(
                self._crear_condicion(

                    "Leucocitosis",

                    (
                        "El recuento de leucocitos está por "
                        "encima del rango de referencia. "
                        "Este hallazgo puede aparecer en "
                        "distintos procesos y requiere "
                        "correlación con el contexto clínico."
                    ),

                    [
                        "Leucocitos"
                    ]
                )
            )


        elif (
            leucocitos
            and leucocitos[
                "estado"
            ] == "BAJO"
        ):

            condiciones.append(
                self._crear_condicion(

                    "Leucopenia",

                    (
                        "El recuento de leucocitos está "
                        "por debajo del rango de referencia."
                    ),

                    [
                        "Leucocitos"
                    ]
                )
            )


        # ==================================================
        # COLESTEROL
        # ==================================================

        if (
            colesterol
            and colesterol[
                "estado"
            ] == "ALTO"
        ):

            condiciones.append(
                self._crear_condicion(

                    (
                        "Elevación del "
                        "colesterol total"
                    ),

                    (
                        "El colesterol total está "
                        "por encima del rango "
                        "de referencia."
                    ),

                    [
                        "Colesterol total"
                    ]
                )
            )


        # ==================================================
        # TRIGLICÉRIDOS
        # ==================================================

        if (
            trigliceridos
            and trigliceridos[
                "estado"
            ] == "ALTO"
        ):

            condiciones.append(
                self._crear_condicion(

                    "Hipertrigliceridemia",

                    (
                        "Los triglicéridos están "
                        "por encima del rango "
                        "de referencia."
                    ),

                    [
                        "Triglicéridos"
                    ]
                )
            )


        # ==================================================
        # PERFIL LIPÍDICO
        # ==================================================

        if (
            colesterol
            and trigliceridos
        ):

            if (
                colesterol[
                    "estado"
                ] == "ALTO"
                and trigliceridos[
                    "estado"
                ] == "ALTO"
            ):

                condiciones.append(
                    self._crear_condicion(

                        (
                            "Patrón compatible con "
                            "alteración del perfil lipídico"
                        ),

                        (
                            "El colesterol total y los "
                            "triglicéridos están elevados "
                            "respecto a los rangos "
                            "proporcionados."
                        ),

                        [
                            "Colesterol total",
                            "Triglicéridos"
                        ]
                    )
                )


        # ==================================================
        # PERFIL TIROIDEO
        # ==================================================

        if (
            tsh
            and t4
        ):

            if (
                tsh[
                    "estado"
                ] == "ALTO"
                and t4[
                    "estado"
                ] == "BAJO"
            ):

                condiciones.append(
                    self._crear_condicion(

                        (
                            "Patrón tiroideo compatible "
                            "con hipofunción"
                        ),

                        (
                            "La combinación de TSH elevada "
                            "y T4 baja puede ser compatible "
                            "con un patrón de hipofunción "
                            "tiroidea. Requiere correlación clínica."
                        ),

                        [
                            "TSH",
                            "T4"
                        ]
                    )
                )


            elif (
                tsh[
                    "estado"
                ] == "BAJO"
                and t4[
                    "estado"
                ] == "ALTO"
            ):

                condiciones.append(
                    self._crear_condicion(

                        (
                            "Patrón tiroideo compatible "
                            "con hiperfunción"
                        ),

                        (
                            "La combinación de TSH baja "
                            "y T4 elevada puede ser compatible "
                            "con un patrón de hiperfunción "
                            "tiroidea. Requiere correlación clínica."
                        ),

                        [
                            "TSH",
                            "T4"
                        ]
                    )
                )


        # ==================================================
        # PCR
        # ==================================================

        if (
            pcr
            and pcr[
                "estado"
            ] == "ALTO"
        ):

            condiciones.append(
                self._crear_condicion(

                    (
                        "Elevación de proteína "
                        "C reactiva"
                    ),

                    (
                        "La proteína C reactiva está elevada. "
                        "El hallazgo puede ser compatible "
                        "con una respuesta inflamatoria, "
                        "pero no identifica la causa "
                        "por sí solo."
                    ),

                    [
                        "PCR"
                    ]
                )
            )


        # ==================================================
        # TROPONINA
        # ==================================================

        if (
            troponina
            and troponina[
                "estado"
            ] == "ALTO"
        ):

            condiciones.append(
                self._crear_condicion(

                    (
                        "Troponina por encima "
                        "del rango de referencia"
                    ),

                    (
                        "La troponina está elevada respecto "
                        "al rango proporcionado. Este hallazgo "
                        "puede asociarse con lesión miocárdica "
                        "y requiere valoración médica y "
                        "correlación clínica."
                    ),

                    [
                        "Troponina"
                    ],

                    nivel=(
                        "revisión prioritaria"
                    )
                )
            )


        return condiciones


    # ======================================================
    # GENERAR CONCLUSIÓN
    # ======================================================

    def generar_conclusion(
        self,
        total,
        normales,
        altos,
        bajos,
        no_evaluables,
        condiciones
    ):

        if total == 0:

            return (
                "No se encontraron resultados de laboratorio "
                "suficientes para realizar una interpretación "
                "automática."
            )


        if (
            altos == 0
            and bajos == 0
            and no_evaluables == 0
        ):

            return (
                "Los resultados evaluados se encuentran "
                "dentro de los rangos de referencia "
                "proporcionados en el documento. "
                "No se identificaron patrones alterados "
                "con los parámetros analizados."
            )


        if (
            altos == 0
            and bajos == 0
            and no_evaluables > 0
        ):

            return (
                "Los resultados que pudieron compararse "
                "se encuentran dentro de sus rangos de "
                "referencia. Algunos resultados no pudieron "
                "evaluarse automáticamente."
            )


        if condiciones:

            nombres = [
                condicion[
                    "condicion"
                ]

                for condicion
                in condiciones
            ]


            return (
                "Se identificaron resultados fuera de los "
                "rangos de referencia y se generaron las "
                "siguientes hipótesis orientativas: "
                + "; ".join(
                    nombres
                )
                + ". Estas asociaciones no constituyen "
                "un diagnóstico médico."
            )


        return (
            "Se identificaron resultados fuera de los "
            "rangos de referencia, pero con la información "
            "disponible no se generó una condición específica "
            "asociada. Los hallazgos requieren "
            "correlación clínica."
        )


    # ======================================================
    # EVALUAR TODOS LOS EXÁMENES
    # ======================================================

    def evaluar_examenes(
        self,
        examenes
    ):

        resultados = [
            self.evaluar_resultado(
                examen
            )

            for examen
            in examenes
        ]


        normales = sum(
            1
            for resultado
            in resultados

            if resultado[
                "estado"
            ] == "DENTRO DE REFERENCIA"
        )


        altos = sum(
            1
            for resultado
            in resultados

            if resultado[
                "estado"
            ] == "ALTO"
        )


        bajos = sum(
            1
            for resultado
            in resultados

            if resultado[
                "estado"
            ] == "BAJO"
        )


        no_evaluables = sum(
            1
            for resultado
            in resultados

            if resultado[
                "estado"
            ] == "NO EVALUABLE"
        )


        hallazgos = [

            {
                "examen":
                    resultado[
                        "examen"
                    ],

                "resultado":
                    resultado[
                        "resultado"
                    ],

                "unidad":
                    resultado[
                        "unidad"
                    ],

                "referencia":
                    resultado[
                        "referencia"
                    ],

                "estado":
                    resultado[
                        "estado"
                    ]
            }

            for resultado
            in resultados

            if resultado[
                "estado"
            ] in {
                "ALTO",
                "BAJO"
            }
        ]


        condiciones = (
            self.aplicar_reglas_clinicas(
                resultados
            )
        )


        conclusion = (
            self.generar_conclusion(

                total=len(
                    resultados
                ),

                normales=normales,

                altos=altos,

                bajos=bajos,

                no_evaluables=no_evaluables,

                condiciones=condiciones
            )
        )


        return {

            "resultados_evaluados":
                len(
                    resultados
                ),

            "normales":
                normales,

            "altos":
                altos,

            "bajos":
                bajos,

            "no_evaluables":
                no_evaluables,

            "resultados":
                resultados,

            "hallazgos":
                hallazgos,

            "posibles_condiciones":
                condiciones,

            "conclusion":
                conclusion,

            "advertencia":
                self.advertencia
        }


# ==========================================================
# SEMANA 8
# 4. SQLITE
# ==========================================================

class BaseEvidencias:

    def __init__(
        self,
        db_file=DB_FILE
    ):

        self.db_file = Path(
            db_file
        )

        self.crear_estructura()


    def conectar(self):

        return sqlite3.connect(
            self.db_file
        )


    # ======================================================
    # CREAR TABLAS
    # ======================================================

    def crear_estructura(self):

        with self.conectar() as conexion:

            conexion.execute(
                """
                CREATE TABLE IF NOT EXISTS documentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_archivo TEXT NOT NULL,
                    tipo_archivo TEXT NOT NULL,
                    tipo_documento TEXT,
                    numero_paginas INTEGER,
                    paciente TEXT,
                    identificacion TEXT,
                    fecha_documento TEXT,
                    fecha_carga TEXT NOT NULL,
                    estado TEXT NOT NULL,
                    ruta_archivo TEXT
                )
                """
            )


            conexion.execute(
                """
                CREATE TABLE IF NOT EXISTS resultados_extraidos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    documento_id INTEGER NOT NULL,
                    examen TEXT NOT NULL,
                    resultado TEXT,
                    unidad TEXT,
                    referencia TEXT,
                    pagina INTEGER,
                    FOREIGN KEY(documento_id)
                    REFERENCES documentos(id)
                )
                """
            )


            conexion.execute(
                """
                CREATE TABLE IF NOT EXISTS reconocimientos_imagen (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_archivo TEXT NOT NULL,
                    prediccion INTEGER,
                    confianza REAL,
                    accuracy_modelo REAL,
                    fecha_procesamiento TEXT NOT NULL,
                    estado TEXT NOT NULL,
                    ruta_archivo TEXT
                )
                """
            )


            # ==================================================
            # NUEVA TABLA
            # INTERPRETACIONES
            # ==================================================

            conexion.execute(
                """
                CREATE TABLE IF NOT EXISTS interpretaciones_clinicas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    documento_id INTEGER NOT NULL,
                    resultados_evaluados INTEGER,
                    normales INTEGER,
                    altos INTEGER,
                    bajos INTEGER,
                    no_evaluables INTEGER,
                    conclusion TEXT,
                    advertencia TEXT,
                    fecha_interpretacion TEXT NOT NULL,
                    FOREIGN KEY(documento_id)
                    REFERENCES documentos(id)
                )
                """
            )


            # ==================================================
            # NUEVA TABLA
            # CONDICIONES
            # ==================================================

            conexion.execute(
                """
                CREATE TABLE IF NOT EXISTS condiciones_clinicas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    documento_id INTEGER NOT NULL,
                    condicion TEXT NOT NULL,
                    descripcion TEXT,
                    examenes_relacionados TEXT,
                    nivel TEXT,
                    FOREIGN KEY(documento_id)
                    REFERENCES documentos(id)
                )
                """
            )


            conexion.commit()


    # ======================================================
    # REGISTRAR DOCUMENTO
    # ======================================================

    def registrar_documento(
        self,
        ruta_archivo,
        resultado_pdf
    ):

        paciente = (
            resultado_pdf.get(
                "paciente",
                {}
            )
            or {}
        )


        with self.conectar() as conexion:

            cursor = conexion.execute(
                """
                INSERT INTO documentos (
                    nombre_archivo,
                    tipo_archivo,
                    tipo_documento,
                    numero_paginas,
                    paciente,
                    identificacion,
                    fecha_documento,
                    fecha_carga,
                    estado,
                    ruta_archivo
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    resultado_pdf.get(
                        "archivo"
                    ),

                    resultado_pdf.get(
                        "tipo_archivo",
                        "PDF"
                    ),

                    resultado_pdf.get(
                        "tipo_documento"
                    ),

                    resultado_pdf.get(
                        "numero_paginas"
                    ),

                    paciente.get(
                        "nombre"
                    ),

                    paciente.get(
                        "identificacion"
                    ),

                    paciente.get(
                        "fecha"
                    ),

                    fecha_actual(),

                    (
                        "requiere_ocr"

                        if resultado_pdf.get(
                            "requiere_ocr"
                        )

                        else "procesado"
                    ),

                    str(
                        Path(
                            ruta_archivo
                        ).resolve()
                    )
                )
            )


            documento_id = int(
                cursor.lastrowid
            )


            # ==================================================
            # RESULTADOS EXTRAÍDOS
            # ==================================================

            for examen in (
                resultado_pdf.get(
                    "examenes",
                    []
                )
                or []
            ):

                conexion.execute(
                    """
                    INSERT INTO resultados_extraidos (
                        documento_id,
                        examen,
                        resultado,
                        unidad,
                        referencia,
                        pagina
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        documento_id,

                        examen.get(
                            "examen"
                        ),

                        examen.get(
                            "resultado"
                        ),

                        examen.get(
                            "unidad"
                        ),

                        examen.get(
                            "referencia"
                        ),

                        examen.get(
                            "pagina"
                        )
                    )
                )


            # ==================================================
            # INTERPRETACIÓN CLÍNICA
            # ==================================================

            interpretacion = (
                resultado_pdf.get(
                    "interpretacion_clinica"
                )
            )


            if interpretacion:

                conexion.execute(
                    """
                    INSERT INTO interpretaciones_clinicas (
                        documento_id,
                        resultados_evaluados,
                        normales,
                        altos,
                        bajos,
                        no_evaluables,
                        conclusion,
                        advertencia,
                        fecha_interpretacion
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        documento_id,

                        interpretacion.get(
                            "resultados_evaluados",
                            0
                        ),

                        interpretacion.get(
                            "normales",
                            0
                        ),

                        interpretacion.get(
                            "altos",
                            0
                        ),

                        interpretacion.get(
                            "bajos",
                            0
                        ),

                        interpretacion.get(
                            "no_evaluables",
                            0
                        ),

                        interpretacion.get(
                            "conclusion"
                        ),

                        interpretacion.get(
                            "advertencia"
                        ),

                        fecha_actual()
                    )
                )


                # ==============================================
                # CONDICIONES
                # ==============================================

                for condicion in (
                    interpretacion.get(
                        "posibles_condiciones",
                        []
                    )
                    or []
                ):

                    conexion.execute(
                        """
                        INSERT INTO condiciones_clinicas (
                            documento_id,
                            condicion,
                            descripcion,
                            examenes_relacionados,
                            nivel
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            documento_id,

                            condicion.get(
                                "condicion"
                            ),

                            condicion.get(
                                "descripcion"
                            ),

                            ", ".join(
                                condicion.get(
                                    "examenes_relacionados",
                                    []
                                )
                                or []
                            ),

                            condicion.get(
                                "nivel"
                            )
                        )
                    )


            conexion.commit()


        return documento_id


    # ======================================================
    # REGISTRAR IMAGEN
    # ======================================================

    def registrar_imagen(
        self,
        ruta_archivo,
        resultado
    ):

        with self.conectar() as conexion:

            cursor = conexion.execute(
                """
                INSERT INTO reconocimientos_imagen (
                    nombre_archivo,
                    prediccion,
                    confianza,
                    accuracy_modelo,
                    fecha_procesamiento,
                    estado,
                    ruta_archivo
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    Path(
                        ruta_archivo
                    ).name,

                    resultado.get(
                        "prediccion"
                    ),

                    resultado.get(
                        "confianza"
                    ),

                    resultado.get(
                        "accuracy_modelo"
                    ),

                    fecha_actual(),

                    "procesado",

                    str(
                        Path(
                            ruta_archivo
                        ).resolve()
                    )
                )
            )


            conexion.commit()


            return int(
                cursor.lastrowid
            )


    # ======================================================
    # RESUMEN SQLITE
    # ======================================================

    def resumen(self):

        with self.conectar() as conexion:

            documentos = (
                conexion.execute(
                    (
                        "SELECT COUNT(*) "
                        "FROM documentos"
                    )
                )
                .fetchone()[0]
            )


            resultados = (
                conexion.execute(
                    (
                        "SELECT COUNT(*) "
                        "FROM resultados_extraidos"
                    )
                )
                .fetchone()[0]
            )


            imagenes = (
                conexion.execute(
                    (
                        "SELECT COUNT(*) "
                        "FROM reconocimientos_imagen"
                    )
                )
                .fetchone()[0]
            )


            interpretaciones = (
                conexion.execute(
                    (
                        "SELECT COUNT(*) "
                        "FROM interpretaciones_clinicas"
                    )
                )
                .fetchone()[0]
            )


            condiciones = (
                conexion.execute(
                    (
                        "SELECT COUNT(*) "
                        "FROM condiciones_clinicas"
                    )
                )
                .fetchone()[0]
            )


        return {

            "documentos":
                int(
                    documentos
                ),

            "resultados_extraidos":
                int(
                    resultados
                ),

            "imagenes_reconocidas":
                int(
                    imagenes
                ),

            "interpretaciones_clinicas":
                int(
                    interpretaciones
                ),

            "condiciones_clinicas":
                int(
                    condiciones
                )
        }


# ==========================================================
# SEMANA 8
# 5. ONTOLOGÍA
# ==========================================================

class OntologiaHIS:

    def __init__(
        self,
        ontology_file=ONTOLOGY_FILE
    ):

        self.ontology_file = Path(
            ontology_file
        )


        # ==================================================
        # CARGAR ONTOLOGÍA EXISTENTE
        # ==================================================

        if self.ontology_file.exists():

            try:

                self.grafo = nx.DiGraph(
                    nx.read_graphml(
                        self.ontology_file
                    )
                )

            except Exception:

                self.grafo = nx.DiGraph()

        else:

            self.grafo = nx.DiGraph()


        self.crear_base()


    # ======================================================
    # CREAR BASE
    # ======================================================

    def crear_base(self):

        relaciones = [

            (
                "documento_medico",
                "paciente",
                "pertenece_a"
            ),

            (
                "documento_medico",
                "examen",
                "contiene"
            ),

            (
                "examen",
                "resultado",
                "tiene_resultado"
            ),

            (
                "resultado",
                "unidad",
                "tiene_unidad"
            ),

            (
                "resultado",
                "rango_referencia",
                "tiene_referencia"
            ),

            (
                "resultado",
                "clasificacion_resultado",
                "se_clasifica_como"
            ),

            (
                "clasificacion_resultado",
                "condicion_clinica",
                "puede_sugerir"
            ),

            (
                "documento_medico",
                "interpretacion_clinica",
                "genera_interpretacion"
            ),

            (
                "interpretacion_clinica",
                "condicion_clinica",
                "incluye_hipotesis"
            ),

            (
                "modelo_mlp",
                "prediccion",
                "produce"
            ),

            (
                "prediccion",
                "digito",
                "asigna_clase"
            ),

            (
                "imagen",
                "prediccion",
                "genera"
            ),

            (
                "digito",
                "dato_clinico",
                "puede_formar_parte_de"
            ),

            (
                "dato_clinico",
                "temperatura",
                "puede_representar"
            ),

            (
                "dato_clinico",
                "frecuencia_cardiaca",
                "puede_representar"
            ),

            (
                "dato_clinico",
                "presion_arterial",
                "puede_representar"
            )
        ]


        for (
            origen,
            destino,
            relacion
        ) in relaciones:

            self.grafo.add_edge(
                origen,
                destino,
                rel=relacion
            )


    # ======================================================
    # REGISTRAR DOCUMENTO
    # ======================================================

    def registrar_documento(
        self,
        documento_id,
        resultado_pdf
    ):

        nodo_documento = (
            f"documento_{documento_id}"
        )


        self.grafo.add_node(
            nodo_documento,
            tipo="documento_medico",
            archivo=str(
                resultado_pdf.get(
                    "archivo",
                    ""
                )
            )
        )


        self.grafo.add_edge(
            nodo_documento,
            "documento_medico",
            rel="es_instancia_de"
        )


        paciente = (
            resultado_pdf.get(
                "paciente",
                {}
            )
            or {}
        )


        nombre = paciente.get(
            "nombre"
        )


        if nombre:

            nodo_paciente = (
                "paciente_"
                + limpiar_nombre_nodo(
                    nombre
                )
            )


            self.grafo.add_node(
                nodo_paciente,
                tipo="paciente",
                nombre=str(
                    nombre
                )
            )


            self.grafo.add_edge(
                nodo_documento,
                nodo_paciente,
                rel="pertenece_a"
            )


        # ==================================================
        # RESULTADOS INTERPRETADOS
        # ==================================================

        interpretacion = (
            resultado_pdf.get(
                "interpretacion_clinica"
            )
            or {}
        )


        evaluados_por_examen = {

            normalizar_texto(
                item.get(
                    "examen",
                    ""
                )
            ):
                item

            for item
            in (
                interpretacion.get(
                    "resultados",
                    []
                )
                or []
            )
        }


        nodos_resultado_por_examen = {}


        # ==================================================
        # EXÁMENES
        # ==================================================

        for indice, examen in enumerate(
            (
                resultado_pdf.get(
                    "examenes",
                    []
                )
                or []
            ),
            start=1
        ):

            nombre_examen = (
                limpiar_nombre_nodo(
                    examen.get(
                        "examen",
                        ""
                    )
                )
            )


            nodo_examen = (
                f"examen_"
                f"{documento_id}_"
                f"{indice}_"
                f"{nombre_examen}"
            )


            nodo_resultado = (
                f"resultado_"
                f"{documento_id}_"
                f"{indice}"
            )


            self.grafo.add_node(
                nodo_examen,
                tipo="examen",
                nombre=str(
                    examen.get(
                        "examen",
                        ""
                    )
                )
            )


            self.grafo.add_node(
                nodo_resultado,
                tipo="resultado",
                valor=str(
                    examen.get(
                        "resultado",
                        ""
                    )
                )
            )


            self.grafo.add_edge(
                nodo_documento,
                nodo_examen,
                rel="contiene"
            )


            self.grafo.add_edge(
                nodo_examen,
                nodo_resultado,
                rel="tiene_resultado"
            )


            clave_examen = (
                normalizar_texto(
                    examen.get(
                        "examen",
                        ""
                    )
                )
            )


            nodos_resultado_por_examen[
                clave_examen
            ] = nodo_resultado


            # ==============================================
            # UNIDAD
            # ==============================================

            if examen.get(
                "unidad"
            ):

                nodo_unidad = (
                    "unidad_"
                    + limpiar_nombre_nodo(
                        examen[
                            "unidad"
                        ]
                    )
                )


                self.grafo.add_node(
                    nodo_unidad,
                    tipo="unidad",
                    valor=str(
                        examen[
                            "unidad"
                        ]
                    )
                )


                self.grafo.add_edge(
                    nodo_resultado,
                    nodo_unidad,
                    rel="tiene_unidad"
                )


            # ==============================================
            # REFERENCIA
            # ==============================================

            if examen.get(
                "referencia"
            ):

                nodo_referencia = (
                    f"referencia_"
                    f"{documento_id}_"
                    f"{indice}"
                )


                self.grafo.add_node(
                    nodo_referencia,
                    tipo="rango_referencia",
                    valor=str(
                        examen[
                            "referencia"
                        ]
                    )
                )


                self.grafo.add_edge(
                    nodo_resultado,
                    nodo_referencia,
                    rel="tiene_referencia"
                )


            # ==============================================
            # CLASIFICACIÓN
            # ==============================================

            evaluado = (
                evaluados_por_examen.get(
                    clave_examen
                )
            )


            if evaluado:

                estado = evaluado.get(
                    "estado",
                    "NO EVALUABLE"
                )


                nodo_estado = (
                    f"clasificacion_"
                    f"{documento_id}_"
                    f"{indice}_"
                    f"{limpiar_nombre_nodo(estado)}"
                )


                self.grafo.add_node(
                    nodo_estado,
                    tipo="clasificacion_resultado",
                    estado=str(
                        estado
                    )
                )


                self.grafo.add_edge(
                    nodo_resultado,
                    nodo_estado,
                    rel="se_clasifica_como"
                )


        # ==================================================
        # INTERPRETACIÓN CLÍNICA
        # ==================================================

        if interpretacion:

            nodo_interpretacion = (
                f"interpretacion_{documento_id}"
            )


            self.grafo.add_node(
                nodo_interpretacion,
                tipo="interpretacion_clinica",
                conclusion=str(
                    interpretacion.get(
                        "conclusion",
                        ""
                    )
                )
            )


            self.grafo.add_edge(
                nodo_documento,
                nodo_interpretacion,
                rel="genera_interpretacion"
            )


            # ==============================================
            # CONDICIONES
            # ==============================================

            for indice, condicion in enumerate(
                (
                    interpretacion.get(
                        "posibles_condiciones",
                        []
                    )
                    or []
                ),
                start=1
            ):

                nombre_condicion = (
                    condicion.get(
                        "condicion",
                        "condicion"
                    )
                )


                nodo_condicion = (
                    f"condicion_"
                    f"{documento_id}_"
                    f"{indice}_"
                    f"{limpiar_nombre_nodo(nombre_condicion)}"
                )


                self.grafo.add_node(
                    nodo_condicion,
                    tipo="condicion_clinica",
                    nombre=str(
                        nombre_condicion
                    ),
                    nivel=str(
                        condicion.get(
                            "nivel",
                            "orientativo"
                        )
                    )
                )


                self.grafo.add_edge(
                    nodo_interpretacion,
                    nodo_condicion,
                    rel="incluye_hipotesis"
                )


                for examen_relacionado in (
                    condicion.get(
                        "examenes_relacionados",
                        []
                    )
                    or []
                ):

                    nodo_resultado = (
                        nodos_resultado_por_examen.get(
                            normalizar_texto(
                                examen_relacionado
                            )
                        )
                    )


                    if nodo_resultado:

                        self.grafo.add_edge(
                            nodo_resultado,
                            nodo_condicion,
                            rel="puede_sugerir"
                        )


        self.guardar()


    # ======================================================
    # REGISTRAR PREDICCIÓN DE IMAGEN
    # ======================================================

    def registrar_prediccion_imagen(
        self,
        reconocimiento_id,
        resultado
    ):

        nodo_imagen = (
            f"imagen_{reconocimiento_id}"
        )


        nodo_prediccion = (
            f"prediccion_{reconocimiento_id}"
        )


        nodo_digito = (
            f"digito_{resultado['prediccion']}"
        )


        self.grafo.add_node(
            nodo_imagen,
            tipo="imagen",
            archivo=str(
                resultado.get(
                    "archivo",
                    ""
                )
            )
        )


        self.grafo.add_node(
            nodo_prediccion,
            tipo="prediccion",
            valor=str(
                resultado[
                    "prediccion"
                ]
            )
        )


        self.grafo.add_node(
            nodo_digito,
            tipo="digito",
            valor=str(
                resultado[
                    "prediccion"
                ]
            )
        )


        self.grafo.add_edge(
            nodo_imagen,
            nodo_prediccion,
            rel="genera"
        )


        self.grafo.add_edge(
            "modelo_mlp",
            nodo_prediccion,
            rel="produce"
        )


        self.grafo.add_edge(
            nodo_prediccion,
            nodo_digito,
            rel="asigna_clase"
        )


        self.grafo.add_edge(
            nodo_digito,
            "dato_clinico",
            rel="puede_formar_parte_de"
        )


        self.guardar()


    # ======================================================
    # GUARDAR
    # ======================================================

    def guardar(self):

        nx.write_graphml(
            self.grafo,
            self.ontology_file
        )


    # ======================================================
    # RESUMEN
    # ======================================================

    def resumen(self):

        return {

            "nodos":
                int(
                    self.grafo.number_of_nodes()
                ),

            "relaciones":
                int(
                    self.grafo.number_of_edges()
                ),

            "archivo":
                str(
                    self.ontology_file
                )
        }


# ==========================================================
# SEMANA 8
# 6. SISTEMA INTEGRADO
# ==========================================================

class SistemaReconocimientoSemana8:

    def __init__(self):

        self.mlp = (
            ReconocedorDigitosMLP()
        )


        self.documentos = (
            ProcesadorDocumentoMedico()
        )


        self.interpretador = (
            MotorInterpretacionClinica()
        )


        self.base = (
            BaseEvidencias()
        )


        self.ontologia = (
            OntologiaHIS()
        )


    # ======================================================
    # INICIALIZAR
    # ======================================================

    def inicializar(self):

        estado_modelo = (
            self.mlp.asegurar_modelo()
        )


        self.ontologia.guardar()


        self.generar_reporte()


        return {

            "modelo":
                estado_modelo,

            "base":
                self.base.resumen(),

            "ontologia":
                self.ontologia.resumen(),

            "interpretacion_clinica":
                True
        }


    # ======================================================
    # PROCESAR IMAGEN
    # ======================================================

    def procesar_imagen(
        self,
        ruta_imagen
    ):

        resultado = (
            self.mlp.predecir_imagen(
                ruta_imagen
            )
        )


        reconocimiento_id = (
            self.base.registrar_imagen(
                ruta_imagen,
                resultado
            )
        )


        self.ontologia.registrar_prediccion_imagen(
            reconocimiento_id,
            resultado
        )


        resultado[
            "reconocimiento_id"
        ] = reconocimiento_id


        resultado[
            "evidencia_sqlite"
        ] = True


        resultado[
            "ontologia_actualizada"
        ] = True


        self.generar_reporte()


        return resultado


    # ======================================================
    # PROCESAR PDF
    # ======================================================

    def procesar_pdf(
        self,
        ruta_pdf
    ):

        # ==================================================
        # EXTRAER INFORMACIÓN
        # ==================================================

        resultado = (
            self.documentos.procesar_pdf(
                ruta_pdf
            )
        )


        # ==================================================
        # INTERPRETACIÓN CLÍNICA
        # ==================================================

        if not resultado.get(
            "requiere_ocr",
            False
        ):

            resultado[
                "interpretacion_clinica"
            ] = (
                self.interpretador.evaluar_examenes(
                    (
                        resultado.get(
                            "examenes",
                            []
                        )
                        or []
                    )
                )
            )


        else:

            resultado[
                "interpretacion_clinica"
            ] = None


        # ==================================================
        # SQLITE
        # ==================================================

        documento_id = (
            self.base.registrar_documento(
                ruta_pdf,
                resultado
            )
        )


        # ==================================================
        # ONTOLOGÍA
        # ==================================================

        self.ontologia.registrar_documento(
            documento_id,
            resultado
        )


        resultado[
            "documento_id"
        ] = documento_id


        resultado[
            "evidencia_sqlite"
        ] = True


        resultado[
            "ontologia_actualizada"
        ] = True


        self.generar_reporte()


        return resultado


    # ======================================================
    # DATASET
    # ======================================================

    def probar_dataset(
        self,
        indice=15
    ):

        return (
            self.mlp
            .predecir_ejemplo_dataset(
                indice
            )
        )


    # ======================================================
    # INTERPRETAR EXÁMENES DIRECTAMENTE
    # ======================================================

    def interpretar_examenes(
        self,
        examenes
    ):

        return (
            self.interpretador.evaluar_examenes(
                examenes
            )
        )


    # ======================================================
    # REPORTE
    # ======================================================

    def generar_reporte(self):

        resumen_bd = (
            self.base.resumen()
        )


        resumen_ontologia = (
            self.ontologia.resumen()
        )


        accuracy = (
            self.mlp.accuracy
        )


        accuracy_texto = (

            f"{accuracy:.4f}"

            if isinstance(
                accuracy,
                (int, float)
            )

            else (
                "Pendiente de entrenamiento"
            )
        )


        contenido = f"""
# Semana 8 - Representaciones del reconocimiento

## Proyecto

HIS_IA - Sistema Inteligente Híbrido aplicado al dominio clínico.

## Objetivo

Integrar reconocimiento mediante red neuronal MLP, evidencia persistente en SQLite, procesamiento documental, interpretación clínica orientativa y una ontología GraphML.

## Red neuronal

- Dataset: `sklearn.datasets.load_digits`.
- Entrada: imágenes de 8x8 convertidas en 64 valores.
- Modelo: `MLPClassifier` con una capa oculta de 64 neuronas.
- Accuracy registrado: **{accuracy_texto}**.
- Artefacto: `artifacts/modelo_mlp.pkl`.

## Procesamiento documental

El sistema permite procesar PDF con texto digital y extraer:

- Paciente.
- Identificación.
- Fecha.
- Examen.
- Resultado.
- Unidad.
- Rango de referencia.
- Página.

Los PDF sin texto digital suficiente se clasifican como documentos que requieren OCR.

## Interpretación clínica orientativa

El componente `MotorInterpretacionClinica` compara cada resultado con el rango proporcionado por el documento.

Clasificaciones:

- BAJO.
- DENTRO DE REFERENCIA.
- ALTO.
- NO EVALUABLE.

El motor puede generar hipótesis orientativas para patrones como glucosa alterada, creatinina elevada, hemoglobina y hematocrito bajos, alteraciones plaquetarias, leucocitos, perfil lipídico, patrón tiroideo, PCR y troponina.

Las asociaciones generadas no constituyen diagnósticos médicos.

## Evidencia SQLite

Archivo: `artifacts/imagenes.db`.

- Documentos: {resumen_bd['documentos']}.
- Resultados extraídos: {resumen_bd['resultados_extraidos']}.
- Imágenes reconocidas: {resumen_bd['imagenes_reconocidas']}.
- Interpretaciones clínicas: {resumen_bd['interpretaciones_clinicas']}.
- Condiciones orientativas registradas: {resumen_bd['condiciones_clinicas']}.

## Ontología

Archivo: `artifacts/ontologia.graphml`.

- Nodos: {resumen_ontologia['nodos']}.
- Relaciones: {resumen_ontologia['relaciones']}.

La ontología incluye relaciones entre documentos, pacientes, exámenes, resultados, rangos, clasificaciones y condiciones clínicas orientativas.

## Limitaciones

- La MLP fue entrenada con `load_digits`.
- La extracción depende de la estructura textual del PDF.
- Los PDF escaneados todavía requieren OCR.
- La interpretación utiliza principalmente los rangos incluidos en el propio documento.
- Los resultados deben ser correlacionados con el contexto clínico.
- HIS_IA no establece diagnósticos médicos.
"""


        REPORT_FILE.write_text(
            contenido.strip(),
            encoding="utf-8"
        )


# ==========================================================
# CONSOLA
# ==========================================================

def imprimir_estado(
    sistema
):

    estado = (
        sistema.inicializar()
    )


    print(
        "\nSEMANA 8 INICIALIZADA"
    )


    print(
        "=" * 60
    )


    accuracy = (
        estado[
            "modelo"
        ].get(
            "accuracy"
        )
    )


    if accuracy is not None:

        print(
            "Accuracy MLP:",
            round(
                float(
                    accuracy
                ),
                4
            )
        )


    else:

        print(
            "Accuracy MLP: no disponible"
        )


    print(
        "Modelo:",
        MODEL_FILE
    )


    print(
        "SQLite:",
        DB_FILE
    )


    print(
        "Ontología:",
        ONTOLOGY_FILE
    )


    print(
        "Reporte:",
        REPORT_FILE
    )


    print(
        "Interpretación clínica orientativa: Activa"
    )


# ==========================================================
# IMPRIMIR INTERPRETACIÓN CLÍNICA
# ==========================================================

def imprimir_interpretacion_clinica(
    interpretacion
):

    print(
        "\n"
        + "=" * 60
    )


    print(
        "ANÁLISIS CLÍNICO ORIENTATIVO"
    )


    print(
        "=" * 60
    )


    if not interpretacion:

        print(
            "No fue posible realizar la interpretación clínica."
        )

        return


    print(
        "Resultados evaluados:",
        interpretacion[
            "resultados_evaluados"
        ]
    )


    print(
        "Dentro de referencia:",
        interpretacion[
            "normales"
        ]
    )


    print(
        "Altos:",
        interpretacion[
            "altos"
        ]
    )


    print(
        "Bajos:",
        interpretacion[
            "bajos"
        ]
    )


    print(
        "No evaluables:",
        interpretacion[
            "no_evaluables"
        ]
    )


    # ======================================================
    # RESULTADOS
    # ======================================================

    print(
        "\nCLASIFICACIÓN DE RESULTADOS"
    )


    for resultado in (
        interpretacion.get(
            "resultados",
            []
        )
    ):

        print(
            "-"
        )


        print(
            "  Examen:",
            resultado[
                "examen"
            ]
        )


        print(
            "  Resultado:",
            resultado[
                "resultado"
            ]
        )


        print(
            "  Unidad:",
            (
                resultado[
                    "unidad"
                ]
                or "No detectada"
            )
        )


        print(
            "  Referencia:",
            (
                resultado[
                    "referencia"
                ]
                or "No detectada"
            )
        )


        print(
            "  Estado:",
            resultado[
                "estado"
            ]
        )


    # ======================================================
    # CONDICIONES
    # ======================================================

    print(
        "\nPOSIBLES CONDICIONES ASOCIADAS"
    )


    condiciones = (
        interpretacion.get(
            "posibles_condiciones",
            []
        )
    )


    if condiciones:

        for condicion in condiciones:

            print(
                "-"
            )


            print(
                "  Condición:",
                condicion[
                    "condicion"
                ]
            )


            print(
                "  Nivel:",
                condicion[
                    "nivel"
                ]
            )


            print(
                "  Exámenes:",
                ", ".join(
                    condicion[
                        "examenes_relacionados"
                    ]
                )
            )


            print(
                "  Descripción:",
                condicion[
                    "descripcion"
                ]
            )


    else:

        print(
            "No se identificaron patrones alterados específicos."
        )


    # ======================================================
    # CONCLUSIÓN
    # ======================================================

    print(
        "\nCONCLUSIÓN"
    )


    print(
        interpretacion[
            "conclusion"
        ]
    )


    # ======================================================
    # ADVERTENCIA
    # ======================================================

    print(
        "\nADVERTENCIA"
    )


    print(
        interpretacion[
            "advertencia"
        ]
    )


# ==========================================================
# MENÚ
# ==========================================================

def menu():

    sistema = (
        SistemaReconocimientoSemana8()
    )


    imprimir_estado(
        sistema
    )


    while True:

        print(
            "\n"
            + "=" * 60
        )


        print(
            "SEMANA 8 - RECONOCIMIENTO HIS_IA"
        )


        print(
            "=" * 60
        )


        print(
            "1. Probar MLP con imagen del dataset"
        )


        print(
            "2. Analizar imagen propia de un dígito"
        )


        print(
            "3. Analizar PDF médico digital"
        )


        print(
            "4. Ver resumen de evidencia"
        )


        print(
            "5. Salir"
        )


        opcion = input(
            "\nSeleccione una opción: "
        ).strip()


        # ==================================================
        # OPCIÓN 1
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
                    "\nRESULTADO"
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
        # OPCIÓN 2
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

                resultado = (
                    sistema.procesar_imagen(
                        ruta
                    )
                )


                print(
                    "\nRESULTADO"
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


                print(
                    "SQLite ID:",
                    resultado[
                        "reconocimiento_id"
                    ]
                )


                print(
                    "Ontología actualizada: Sí"
                )


            except Exception as error:

                print(
                    "Error:",
                    error
                )


        # ==================================================
        # OPCIÓN 3
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

                resultado = (
                    sistema.procesar_pdf(
                        ruta
                    )
                )


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


                # ==========================================
                # OCR
                # ==========================================

                if resultado[
                    "requiere_ocr"
                ]:

                    print(
                        (
                            "Estado: el PDF no contiene "
                            "suficiente texto digital."
                        )
                    )


                    print(
                        "El documento requiere OCR."
                    )


                else:

                    paciente = (
                        resultado[
                            "paciente"
                        ]
                    )


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


                    # ======================================
                    # NUEVA INTERPRETACIÓN
                    # ======================================

                    imprimir_interpretacion_clinica(
                        resultado.get(
                            "interpretacion_clinica"
                        )
                    )


                print(
                    "\nSQLite ID:",
                    resultado[
                        "documento_id"
                    ]
                )


                print(
                    "Evidencia registrada: Sí"
                )


                print(
                    "Ontología actualizada: Sí"
                )


            except Exception as error:

                print(
                    "Error:",
                    error
                )


        # ==================================================
        # OPCIÓN 4
        # ==================================================

        elif opcion == "4":

            print(
                "\nEVIDENCIA SQLITE"
            )


            print(
                sistema.base.resumen()
            )


            print(
                "\nONTOLOGÍA"
            )


            print(
                sistema.ontologia.resumen()
            )


        # ==================================================
        # OPCIÓN 5
        # ==================================================

        elif opcion == "5":

            print(
                "\nSemana 8 finalizada."
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

    menu()