# ==========================================================
# SEMANA 10
# RECONOCIMIENTO Y COMPARACIÓN DE IMÁGENES
#
# Imagen
#   ↓
# Escala de grises
#   ↓
# Otsu
#   ↓
# Regiones
#   ↓
# Intensidad
#   ↓
# Textura LBP
#   ↓
# Vector de características
#   ↓
# Comparación entre imágenes
# ==========================================================

from pathlib import Path
import argparse
import json

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from PIL import Image

from skimage import (
    color,
    data,
    filters,
    measure,
)

from skimage.feature import (
    local_binary_pattern,
)


# ==========================================================
# CONFIGURACIÓN GENERAL
# ==========================================================

ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

ARTIFACTS = (
    ROOT
    / "artifacts"
)

REPORTS = (
    ROOT
    / "reports"
)

ARTIFACTS.mkdir(
    parents=True,
    exist_ok=True
)

REPORTS.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================================
# CLASE PRINCIPAL
# ==========================================================

class ProcesadorCaracteristicasSemana10:

    def __init__(
        self,
        area_minima=50,
        radio_lbp=2
    ):

        self.area_minima = int(
            area_minima
        )

        self.radio_lbp = int(
            radio_lbp
        )

        if self.area_minima < 1:

            raise ValueError(
                "El área mínima debe ser mayor o igual a 1."
            )

        if self.radio_lbp < 1:

            raise ValueError(
                "El radio LBP debe ser mayor o igual a 1."
            )

        self.puntos_lbp = (
            8
            *
            self.radio_lbp
        )


    # ======================================================
    # CARGAR IMAGEN
    # ======================================================

    def cargar_imagen(
        self,
        ruta_imagen
    ):

        ruta = Path(
            ruta_imagen
        ).expanduser()


        if not ruta.is_absolute():

            ruta = (
                ROOT
                /
                ruta
            ).resolve()


        if not ruta.exists():

            raise FileNotFoundError(
                f"No existe la imagen: {ruta}"
            )


        permitidas = {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
            ".bmp",
            ".tif",
            ".tiff"
        }


        if ruta.suffix.lower() not in permitidas:

            raise ValueError(
                (
                    "Formato no permitido. "
                    "Use PNG, JPG, JPEG, WEBP, "
                    "BMP, TIF o TIFF."
                )
            )


        with Image.open(
            ruta
        ) as imagen:

            imagen = (
                imagen
                .convert(
                    "RGB"
                )
            )

            imagen = np.array(
                imagen
            )


        return (
            imagen,
            ruta
        )


    # ======================================================
    # IMAGEN ACADÉMICA DE PRUEBA
    # ======================================================

    def cargar_imagen_prueba(
        self
    ):

        return data.coins()


    # ======================================================
    # ESCALA DE GRISES
    # ======================================================

    def convertir_grises(
        self,
        imagen
    ):

        if imagen.ndim == 2:

            gris = imagen.astype(
                np.float64
            )

            if gris.max() > 1:

                gris = (
                    gris
                    /
                    255.0
                )

        else:

            gris = color.rgb2gray(
                imagen
            )


        return gris


    # ======================================================
    # SEGMENTACIÓN OTSU
    # ======================================================

    def segmentar_otsu(
        self,
        gris
    ):

        umbral = (
            filters.threshold_otsu(
                gris
            )
        )


        mascara = (
            gris
            >
            umbral
        )


        return (
            float(
                umbral
            ),
            mascara
        )


    # ======================================================
    # REGIONES CONECTADAS
    # ======================================================

    def detectar_regiones(
        self,
        mascara
    ):

        etiquetas = (
            measure.label(
                mascara
            )
        )


        regiones_totales = (
            measure.regionprops(
                etiquetas
            )
        )


        regiones_validas = [
            region
            for region in regiones_totales
            if region.area
            >
            self.area_minima
        ]


        return (
            etiquetas,
            regiones_totales,
            regiones_validas
        )


    # ======================================================
    # MEDICIÓN DE REGIONES
    # ======================================================

    def medir_regiones(
        self,
        regiones_validas
    ):

        areas = np.array(
            [
                region.area
                for region in regiones_validas
            ],
            dtype=float
        )


        if len(
            areas
        ) > 0:

            area_media = float(
                areas.mean()
            )

            desviacion_area = float(
                areas.std()
            )

        else:

            area_media = 0.0
            desviacion_area = 0.0


        return {

            "cantidad_regiones":
                int(
                    len(
                        regiones_validas
                    )
                ),

            "area_media":
                area_media,

            "desviacion_area":
                desviacion_area
        }


    # ======================================================
    # HISTOGRAMA DE INTENSIDAD
    # ======================================================

    def calcular_histograma_intensidad(
        self,
        gris
    ):

        imagen_255 = (
            gris
            *
            255.0
        )


        histograma, bins = (
            np.histogram(
                imagen_255.ravel(),
                bins=32,
                range=(
                    0,
                    256
                ),
                density=True
            )
        )


        return (
            histograma,
            bins
        )


    # ======================================================
    # DISTRIBUCIÓN DE INTENSIDAD
    # ======================================================

    def calcular_distribucion_intensidad(
        self,
        gris
    ):

        imagen_255 = (
            gris
            *
            255.0
        )


        total = int(
            imagen_255.size
        )


        oscuros = int(
            np.sum(
                imagen_255 <= 84
            )
        )


        intermedios = int(
            np.sum(
                (
                    imagen_255 >= 85
                )
                &
                (
                    imagen_255 <= 169
                )
            )
        )


        claros = int(
            np.sum(
                imagen_255 >= 170
            )
        )


        def calcular_porcentaje(
            cantidad
        ):

            if total == 0:
                return 0.0

            return round(
                (
                    cantidad
                    /
                    total
                )
                *
                100,
                2
            )


        return {

            "oscuras": {
                "pixeles":
                    oscuros,

                "porcentaje":
                    calcular_porcentaje(
                        oscuros
                    )
            },

            "intermedias": {
                "pixeles":
                    intermedios,

                "porcentaje":
                    calcular_porcentaje(
                        intermedios
                    )
            },

            "claras": {
                "pixeles":
                    claros,

                "porcentaje":
                    calcular_porcentaje(
                        claros
                    )
            },

            "total_pixeles":
                total
        }


    # ======================================================
    # TEXTURA LBP
    # ======================================================

    def calcular_textura_lbp(
        self,
        gris
    ):

        imagen_lbp = (
            gris
            *
            255
        ).astype(
            np.uint8
        )


        lbp = (
            local_binary_pattern(
                imagen_lbp,
                self.puntos_lbp,
                self.radio_lbp,
                method="uniform"
            )
        )


        histograma_lbp, _ = (
            np.histogram(
                lbp.ravel(),
                bins=np.arange(
                    0,
                    self.puntos_lbp + 3
                ),
                density=True
            )
        )


        return (
            lbp,
            histograma_lbp
        )


    # ======================================================
    # VECTOR DE CARACTERÍSTICAS
    # ======================================================

    def construir_vector_caracteristicas(
        self,
        mediciones,
        histograma_intensidad,
        histograma_lbp
    ):

        regiones = np.array(
            [
                mediciones[
                    "area_media"
                ],

                mediciones[
                    "desviacion_area"
                ],

                mediciones[
                    "cantidad_regiones"
                ]
            ],
            dtype=float
        )


        vector = np.concatenate(
            [
                regiones,
                histograma_intensidad,
                histograma_lbp
            ]
        )


        return vector


    # ======================================================
    # EXTRAER DESCRIPTORES
    # ======================================================

    def extraer_descriptores(
        self,
        imagen
    ):

        gris = (
            self.convertir_grises(
                imagen
            )
        )


        (
            umbral,
            mascara
        ) = (
            self.segmentar_otsu(
                gris
            )
        )


        (
            etiquetas,
            regiones_totales,
            regiones_validas
        ) = (
            self.detectar_regiones(
                mascara
            )
        )


        mediciones = (
            self.medir_regiones(
                regiones_validas
            )
        )


        (
            histograma_intensidad,
            bins
        ) = (
            self.calcular_histograma_intensidad(
                gris
            )
        )


        distribucion_intensidad = (
            self.calcular_distribucion_intensidad(
                gris
            )
        )


        (
            lbp,
            histograma_lbp
        ) = (
            self.calcular_textura_lbp(
                gris
            )
        )


        vector = (
            self.construir_vector_caracteristicas(
                mediciones,
                histograma_intensidad,
                histograma_lbp
            )
        )


        return {

            "gris":
                gris,

            "umbral":
                umbral,

            "mascara":
                mascara,

            "etiquetas":
                etiquetas,

            "regiones_totales":
                regiones_totales,

            "regiones_validas":
                regiones_validas,

            "mediciones":
                mediciones,

            "histograma_intensidad":
                histograma_intensidad,

            "bins":
                bins,

            "distribucion_intensidad":
                distribucion_intensidad,

            "lbp":
                lbp,

            "histograma_lbp":
                histograma_lbp,

            "vector":
                vector
        }


    # ======================================================
    # GUARDAR VECTOR
    # ======================================================

    def guardar_vector(
        self,
        vector,
        nombre="semana10_features.npy"
    ):

        ruta = (
            ARTIFACTS
            /
            nombre
        )


        np.save(
            ruta,
            vector
        )


        return ruta


    # ======================================================
    # GUARDAR HISTOGRAMA
    # ======================================================

    def guardar_histograma(
        self,
        histograma,
        bins,
        nombre="semana10_histograma.png"
    ):

        centros = (
            bins[:-1]
            +
            bins[1:]
        ) / 2


        figura, eje = (
            plt.subplots(
                figsize=(
                    7,
                    4
                )
            )
        )


        eje.plot(
            centros,
            histograma
        )


        eje.set_title(
            "Histograma de intensidad - Semana 10"
        )


        eje.set_xlabel(
            "Intensidad"
        )


        eje.set_ylabel(
            "Densidad"
        )


        figura.tight_layout()


        ruta = (
            ARTIFACTS
            /
            nombre
        )


        figura.savefig(
            ruta,
            dpi=160
        )


        plt.close(
            figura
        )


        return ruta


    # ======================================================
    # CONVERTIR DESCRIPTORES A RESULTADO
    # ======================================================

    def construir_resultado(
        self,
        nombre,
        descriptores,
        ruta_features=None,
        ruta_histograma=None
    ):

        mediciones = (
            descriptores[
                "mediciones"
            ]
        )


        resultado = {

            "archivo":
                str(
                    nombre
                ),

            "umbral_otsu":
                float(
                    descriptores[
                        "umbral"
                    ]
                ),

            "regiones_totales":
                int(
                    len(
                        descriptores[
                            "regiones_totales"
                        ]
                    )
                ),

            "regiones":
                int(
                    mediciones[
                        "cantidad_regiones"
                    ]
                ),

            "area_minima":
                int(
                    self.area_minima
                ),

            "area_media":
                float(
                    mediciones[
                        "area_media"
                    ]
                ),

            "desviacion_area":
                float(
                    mediciones[
                        "desviacion_area"
                    ]
                ),

            "radio_lbp":
                int(
                    self.radio_lbp
                ),

            "puntos_lbp":
                int(
                    self.puntos_lbp
                ),

            "dimension_vector":
                int(
                    len(
                        descriptores[
                            "vector"
                        ]
                    )
                ),

            "distribucion_intensidad":
                descriptores[
                    "distribucion_intensidad"
                ]
        }


        if ruta_features is not None:

            resultado[
                "features"
            ] = str(
                ruta_features
            )


        if ruta_histograma is not None:

            resultado[
                "histograma"
            ] = str(
                ruta_histograma
            )


        return resultado


    # ======================================================
    # ANALIZAR UNA IMAGEN
    # ======================================================

    def procesar_imagen(
        self,
        imagen,
        nombre="imagen"
    ):

        descriptores = (
            self.extraer_descriptores(
                imagen
            )
        )


        ruta_features = (
            self.guardar_vector(
                descriptores[
                    "vector"
                ]
            )
        )


        ruta_histograma = (
            self.guardar_histograma(
                descriptores[
                    "histograma_intensidad"
                ],
                descriptores[
                    "bins"
                ]
            )
        )


        return (
            self.construir_resultado(
                nombre,
                descriptores,
                ruta_features,
                ruta_histograma
            )
        )


    def analizar(
        self,
        ruta_imagen
    ):

        (
            imagen,
            ruta
        ) = (
            self.cargar_imagen(
                ruta_imagen
            )
        )


        return (
            self.procesar_imagen(
                imagen,
                nombre=ruta
            )
        )


    # ======================================================
    # UTILIDAD DE SIMILITUD
    # ======================================================

    @staticmethod
    def similitud_coseno(
        vector_a,
        vector_b
    ):

        vector_a = np.asarray(
            vector_a,
            dtype=float
        )

        vector_b = np.asarray(
            vector_b,
            dtype=float
        )


        denominador = (
            np.linalg.norm(
                vector_a
            )
            *
            np.linalg.norm(
                vector_b
            )
        )


        if denominador == 0:

            return 1.0


        valor = float(
            np.dot(
                vector_a,
                vector_b
            )
            /
            denominador
        )


        return float(
            np.clip(
                valor,
                0.0,
                1.0
            )
        )


    @staticmethod
    def similitud_relativa(
        valor_a,
        valor_b
    ):

        valor_a = float(
            valor_a
        )

        valor_b = float(
            valor_b
        )


        maximo = max(
            abs(
                valor_a
            ),
            abs(
                valor_b
            ),
            1.0
        )


        diferencia = (
            abs(
                valor_a
                -
                valor_b
            )
            /
            maximo
        )


        return float(
            np.clip(
                1.0
                -
                diferencia,
                0.0,
                1.0
            )
        )


    # ======================================================
    # COMPARAR DOS IMÁGENES
    # ======================================================

    def comparar(
        self,
        ruta_referencia,
        ruta_comparacion
    ):

        (
            imagen_referencia,
            ruta_referencia
        ) = (
            self.cargar_imagen(
                ruta_referencia
            )
        )


        (
            imagen_comparacion,
            ruta_comparacion
        ) = (
            self.cargar_imagen(
                ruta_comparacion
            )
        )


        referencia = (
            self.extraer_descriptores(
                imagen_referencia
            )
        )


        comparacion = (
            self.extraer_descriptores(
                imagen_comparacion
            )
        )


        # ==================================================
        # GUARDAR EVIDENCIA DE AMBAS
        # ==================================================

        referencia_features = (
            self.guardar_vector(
                referencia[
                    "vector"
                ],
                "semana10_referencia_features.npy"
            )
        )


        comparacion_features = (
            self.guardar_vector(
                comparacion[
                    "vector"
                ],
                "semana10_comparacion_features.npy"
            )
        )


        referencia_histograma = (
            self.guardar_histograma(
                referencia[
                    "histograma_intensidad"
                ],
                referencia[
                    "bins"
                ],
                "semana10_referencia_histograma.png"
            )
        )


        comparacion_histograma = (
            self.guardar_histograma(
                comparacion[
                    "histograma_intensidad"
                ],
                comparacion[
                    "bins"
                ],
                "semana10_comparacion_histograma.png"
            )
        )


        # ==================================================
        # SIMILITUD DE INTENSIDAD
        # ==================================================

        similitud_intensidad = (
            self.similitud_coseno(
                referencia[
                    "histograma_intensidad"
                ],
                comparacion[
                    "histograma_intensidad"
                ]
            )
        )


        # ==================================================
        # SIMILITUD DE TEXTURA
        # ==================================================

        similitud_textura = (
            self.similitud_coseno(
                referencia[
                    "histograma_lbp"
                ],
                comparacion[
                    "histograma_lbp"
                ]
            )
        )


        # ==================================================
        # SIMILITUD DE REGIONES
        # ==================================================

        ref_mediciones = (
            referencia[
                "mediciones"
            ]
        )


        comp_mediciones = (
            comparacion[
                "mediciones"
            ]
        )


        similitud_cantidad = (
            self.similitud_relativa(
                ref_mediciones[
                    "cantidad_regiones"
                ],
                comp_mediciones[
                    "cantidad_regiones"
                ]
            )
        )


        similitud_area = (
            self.similitud_relativa(
                ref_mediciones[
                    "area_media"
                ],
                comp_mediciones[
                    "area_media"
                ]
            )
        )


        similitud_desviacion = (
            self.similitud_relativa(
                ref_mediciones[
                    "desviacion_area"
                ],
                comp_mediciones[
                    "desviacion_area"
                ]
            )
        )


        similitud_regiones = (
            (
                similitud_cantidad
                +
                similitud_area
                +
                similitud_desviacion
            )
            /
            3
        )


        # ==================================================
        # RESULTADO GLOBAL
        # ==================================================

        similitud_global = (
            (
                similitud_intensidad
                *
                0.35
            )
            +
            (
                similitud_textura
                *
                0.35
            )
            +
            (
                similitud_regiones
                *
                0.30
            )
        )


        similitud_global = float(
            np.clip(
                similitud_global,
                0.0,
                1.0
            )
        )


        porcentaje_similitud = round(
            similitud_global
            *
            100,
            2
        )


        porcentaje_diferencia = round(
            100
            -
            porcentaje_similitud,
            2
        )


        # ==================================================
        # INTERPRETACIÓN
        # ==================================================

        if porcentaje_similitud >= 85:

            nivel = (
                "alta similitud visual"
            )

            conclusion = (
                "La imagen comparada conserva un patrón visual "
                "muy similar al de la imagen de referencia. "
                "Las regiones, intensidades y texturas presentan "
                "pocas diferencias globales."
            )

        elif porcentaje_similitud >= 65:

            nivel = (
                "similitud visual moderada"
            )

            conclusion = (
                "La imagen comparada mantiene algunas "
                "características de la referencia, pero presenta "
                "diferencias apreciables en regiones, intensidad "
                "o textura."
            )

        else:

            nivel = (
                "baja similitud visual"
            )

            conclusion = (
                "La imagen comparada presenta diferencias "
                "importantes respecto a la referencia en la "
                "distribución de regiones, intensidades o texturas."
            )


        conclusion += (
            " Este resultado representa una comparación "
            "computacional de características visuales y no "
            "constituye una interpretación diagnóstica."
        )


        # ==================================================
        # RESULTADOS INDIVIDUALES
        # ==================================================

        resultado_referencia = (
            self.construir_resultado(
                ruta_referencia,
                referencia,
                referencia_features,
                referencia_histograma
            )
        )


        resultado_comparacion = (
            self.construir_resultado(
                ruta_comparacion,
                comparacion,
                comparacion_features,
                comparacion_histograma
            )
        )


        # ==================================================
        # RESPUESTA
        # ==================================================

        return {

            "referencia":
                resultado_referencia,

            "comparacion":
                resultado_comparacion,

            "similitud": {

                "global":
                    porcentaje_similitud,

                "diferencia":
                    porcentaje_diferencia,

                "intensidad":
                    round(
                        similitud_intensidad
                        *
                        100,
                        2
                    ),

                "textura":
                    round(
                        similitud_textura
                        *
                        100,
                        2
                    ),

                "regiones":
                    round(
                        similitud_regiones
                        *
                        100,
                        2
                    )
            },

            "nivel":
                nivel,

            "diferencias": {

                "regiones_validas":
                    int(
                        comp_mediciones[
                            "cantidad_regiones"
                        ]
                        -
                        ref_mediciones[
                            "cantidad_regiones"
                        ]
                    ),

                "area_media":
                    round(
                        comp_mediciones[
                            "area_media"
                        ]
                        -
                        ref_mediciones[
                            "area_media"
                        ],
                        2
                    ),

                "desviacion_area":
                    round(
                        comp_mediciones[
                            "desviacion_area"
                        ]
                        -
                        ref_mediciones[
                            "desviacion_area"
                        ],
                        2
                    ),

                "umbral_otsu":
                    round(
                        comparacion[
                            "umbral"
                        ]
                        -
                        referencia[
                            "umbral"
                        ],
                        4
                    )
            },

            "conclusion":
                conclusion
        }


    # ======================================================
    # EJEMPLO INDIVIDUAL
    # ======================================================

    def ejecutar_ejemplo_clase(
        self
    ):

        imagen = (
            self.cargar_imagen_prueba()
        )


        return (
            self.procesar_imagen(
                imagen,
                nombre="skimage.data.coins"
            )
        )


# ==========================================================
# FUNCIÓN DE INTEGRACIÓN INDIVIDUAL
# ==========================================================

def analizar_imagen_semana10(
    ruta_imagen,
    area_minima=50,
    radio_lbp=2
):

    procesador = (
        ProcesadorCaracteristicasSemana10(
            area_minima=area_minima,
            radio_lbp=radio_lbp
        )
    )


    return (
        procesador.analizar(
            ruta_imagen
        )
    )


# ==========================================================
# FUNCIÓN DE COMPARACIÓN
# ==========================================================

def comparar_imagenes_semana10(
    ruta_referencia,
    ruta_comparacion,
    area_minima=50,
    radio_lbp=2
):

    procesador = (
        ProcesadorCaracteristicasSemana10(
            area_minima=area_minima,
            radio_lbp=radio_lbp
        )
    )


    return (
        procesador.comparar(
            ruta_referencia=ruta_referencia,
            ruta_comparacion=ruta_comparacion
        )
    )


# ==========================================================
# EJEMPLO ACADÉMICO
# ==========================================================

def ejecutar_semana10_clase(
    area_minima=50,
    radio_lbp=2
):

    procesador = (
        ProcesadorCaracteristicasSemana10(
            area_minima=area_minima,
            radio_lbp=radio_lbp
        )
    )


    return (
        procesador.ejecutar_ejemplo_clase()
    )


# ==========================================================
# CONSOLA
# ==========================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Semana 10 - Extracción y comparación "
            "de características visuales."
        )
    )


    parser.add_argument(
        "--imagen",
        type=str,
        default=None
    )


    parser.add_argument(
        "--referencia",
        type=str,
        default=None
    )


    parser.add_argument(
        "--comparacion",
        type=str,
        default=None
    )


    parser.add_argument(
        "--area-minima",
        type=int,
        default=50
    )


    parser.add_argument(
        "--radio-lbp",
        type=int,
        default=2
    )


    parser.add_argument(
        "--json",
        action="store_true"
    )


    args = (
        parser.parse_args()
    )


    try:

        if (
            args.referencia
            and
            args.comparacion
        ):

            resultado = (
                comparar_imagenes_semana10(
                    ruta_referencia=
                        args.referencia,

                    ruta_comparacion=
                        args.comparacion,

                    area_minima=
                        args.area_minima,

                    radio_lbp=
                        args.radio_lbp
                )
            )

        elif args.imagen:

            resultado = (
                analizar_imagen_semana10(
                    ruta_imagen=
                        args.imagen,

                    area_minima=
                        args.area_minima,

                    radio_lbp=
                        args.radio_lbp
                )
            )

        else:

            resultado = (
                ejecutar_semana10_clase(
                    area_minima=
                        args.area_minima,

                    radio_lbp=
                        args.radio_lbp
                )
            )


        if args.json:

            print(
                json.dumps(
                    {
                        "success":
                            True,

                        "resultado":
                            resultado
                    },
                    ensure_ascii=False,
                    indent=2
                )
            )

        else:

            print(
                json.dumps(
                    resultado,
                    ensure_ascii=False,
                    indent=2
                )
            )


    except Exception as error:

        print(
            json.dumps(
                {
                    "success":
                        False,

                    "error":
                        str(
                            error
                        )
                },
                ensure_ascii=False,
                indent=2
            )
        )


# ==========================================================
# EJECUCIÓN
# ==========================================================

if __name__ == "__main__":

    main()
