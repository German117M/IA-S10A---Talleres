from pathlib import Path
import argparse
import json

import matplotlib.pyplot as plt
import numpy as np

from PIL import Image

from skimage import (
    color,
    feature,
    filters,
    measure,
    morphology
)


# ==========================================================
# CONFIGURACIÓN GENERAL
# ==========================================================

ROOT = Path(
    __file__
).resolve().parent.parent


DATA_DIR = (
    ROOT
    / "data"
)


ARTIFACTS_DIR = (
    ROOT
    / "artifacts"
)


REPORTS_DIR = (
    ROOT
    / "reports"
)


DEFAULT_IMAGE = (
    DATA_DIR
    / "imagen_proyecto.png"
)


ARTIFACT_IMAGE = (
    ARTIFACTS_DIR
    / "semana09_vision.png"
)


ARTIFACT_REGION = (
    ARTIFACTS_DIR
    / "semana09_region_principal.png"
)


REPORT_FILE = (
    REPORTS_DIR
    / "semana09.md"
)


EXTENSIONES_PERMITIDAS = {

    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff"
}


for carpeta in (
    DATA_DIR,
    ARTIFACTS_DIR,
    REPORTS_DIR
):

    carpeta.mkdir(
        parents=True,
        exist_ok=True
    )


# ==========================================================
# UTILIDADES
# ==========================================================

def porcentaje(
    parte,
    total
):

    if not total:

        return 0.0


    return (
        float(
            parte
        )
        / float(
            total
        )
        * 100.0
    )


def convertir_json(
    valor
):

    if isinstance(
        valor,
        np.integer
    ):

        return int(
            valor
        )


    if isinstance(
        valor,
        np.floating
    ):

        return float(
            valor
        )


    if isinstance(
        valor,
        np.ndarray
    ):

        return valor.tolist()


    raise TypeError(
        (
            "Tipo no serializable: "
            f"{type(valor).__name__}"
        )
    )


# ==========================================================
# SEMANA 9
# PROCESAMIENTO DE VISIÓN
# ==========================================================

class ProcesadorVisionSemana9:

    """
    Procesador visual académico para HIS_IA.

    Flujo:

    Imagen
        ↓
    Escala de grises
        ↓
    Canny
        ↓
    Otsu
        ↓
    Máscara binaria
        ↓
    Regiones conectadas
        ↓
    Región principal
        ↓
    Evidencia visual

    Este módulo no realiza diagnóstico médico.

    Su objetivo es preparar imágenes relacionadas con
    el dominio clínico para posteriores procesos como:

    - OCR.
    - reconocimiento.
    - clasificación.
    - validación visual.
    - integración con módulos posteriores de HIS_IA.
    """


    # ======================================================
    # INICIALIZACIÓN
    # ======================================================

    def __init__(
        self,
        sigma=2.0,
        area_minima=20
    ):

        self.sigma = float(
            sigma
        )


        self.area_minima = int(
            area_minima
        )


        if self.sigma <= 0:

            raise ValueError(
                "Sigma debe ser mayor que cero."
            )


        if self.area_minima < 1:

            raise ValueError(
                (
                    "El área mínima debe ser "
                    "mayor o igual a 1."
                )
            )


    # ======================================================
    # RESOLVER RUTA
    # ======================================================

    def resolver_ruta(
        self,
        ruta_imagen
    ):

        ruta = Path(
            ruta_imagen
        ).expanduser()


        if not ruta.is_absolute():

            ruta = (
                ROOT
                / ruta
            ).resolve()


        return ruta


    # ======================================================
    # CARGAR IMAGEN
    # ======================================================

    def cargar_imagen(
        self,
        ruta_imagen
    ):

        ruta = (
            self.resolver_ruta(
                ruta_imagen
            )
        )


        if not ruta.exists():

            raise FileNotFoundError(
                (
                    "No existe la imagen:\n"
                    f"{ruta}"
                )
            )


        if (
            ruta.suffix.lower()
            not in EXTENSIONES_PERMITIDAS
        ):

            raise ValueError(
                (
                    "Formato no permitido. "
                    "Utilice PNG, JPG, JPEG, WEBP, "
                    "BMP, TIF o TIFF."
                )
            )


        with Image.open(
            ruta
        ) as imagen:

            imagen_rgb = (
                imagen
                .convert(
                    "RGB"
                )
            )


            matriz_rgb = np.asarray(
                imagen_rgb,
                dtype=np.uint8
            )


        return (
            ruta,
            matriz_rgb
        )


    # ======================================================
    # GUARDAR IMAGEN DEL PROYECTO
    # ======================================================

    def guardar_imagen_proyecto(
        self,
        matriz_rgb
    ):

        imagen = Image.fromarray(
            matriz_rgb
        )


        imagen.save(
            DEFAULT_IMAGE
        )


        return str(
            DEFAULT_IMAGE
        )


    # ======================================================
    # CONVERTIR A GRISES
    # ======================================================

    def convertir_grises(
        self,
        matriz_rgb
    ):

        matriz_float = (
            matriz_rgb.astype(
                np.float32
            )
            / 255.0
        )


        gris = color.rgb2gray(
            matriz_float
        )


        gris = np.clip(
            gris,
            0.0,
            1.0
        )


        return gris


    # ======================================================
    # CANNY
    # ======================================================

    def detectar_bordes(
        self,
        imagen_gris,
        sigma=None
    ):

        sigma_final = (

            self.sigma

            if sigma is None

            else float(
                sigma
            )
        )


        if sigma_final <= 0:

            raise ValueError(
                "Sigma debe ser mayor que cero."
            )


        bordes = feature.canny(
            imagen_gris,
            sigma=sigma_final
        )


        return bordes


    # ======================================================
    # OTSU
    # ======================================================

    def segmentar_otsu(
        self,
        imagen_gris
    ):

        # ==================================================
        # IMAGEN COMPLETAMENTE UNIFORME
        # ==================================================

        if np.allclose(
            imagen_gris,
            imagen_gris.flat[
                0
            ]
        ):

            umbral = float(
                imagen_gris.flat[
                    0
                ]
            )


            mascara = np.zeros_like(
                imagen_gris,
                dtype=bool
            )


            return (
                umbral,
                mascara
            )


        # ==================================================
        # CALCULAR UMBRAL
        # ==================================================

        umbral = float(
            filters.threshold_otsu(
                imagen_gris
            )
        )


        mascara_clara = (
            imagen_gris
            > umbral
        )


        mascara_oscura = (
            imagen_gris
            <= umbral
        )


        # ==================================================
        # SELECCIONAR REGIÓN MENOS DOMINANTE
        # ==================================================
        #
        # Para documentos, etiquetas y muchas imágenes
        # clínicas, el fondo suele ocupar la mayor parte.
        #
        # Por eso se selecciona como región inicial la
        # clase menos dominante.
        # ==================================================

        porcentaje_claro = float(
            mascara_clara.mean()
        )


        porcentaje_oscuro = float(
            mascara_oscura.mean()
        )


        if (
            porcentaje_claro
            <= porcentaje_oscuro
        ):

            mascara = (
                mascara_clara
            )

        else:

            mascara = (
                mascara_oscura
            )


        # ==================================================
        # LIMPIEZA BÁSICA
        # ==================================================

        mascara = (
            morphology
            .remove_small_objects(
                mascara,
                min_size=self.area_minima
            )
        )


        mascara = (
            morphology
            .remove_small_holes(
                mascara,
                area_threshold=self.area_minima
            )
        )


        return (
            umbral,
            mascara
        )


    # ======================================================
    # REGIONES CONECTADAS
    # ======================================================

    def detectar_regiones(
        self,
        mascara
    ):

        etiquetas = measure.label(
            mascara,
            connectivity=2
        )


        propiedades = measure.regionprops(
            etiquetas
        )


        regiones = []


        for region in propiedades:

            if (
                region.area
                < self.area_minima
            ):

                continue


            (
                fila_min,
                columna_min,
                fila_max,
                columna_max
            ) = region.bbox


            regiones.append(
                {
                    "etiqueta":
                        int(
                            region.label
                        ),

                    "area":
                        int(
                            region.area
                        ),

                    "bbox":
                        [
                            int(
                                fila_min
                            ),

                            int(
                                columna_min
                            ),

                            int(
                                fila_max
                            ),

                            int(
                                columna_max
                            )
                        ],

                    "centroide":
                        [
                            round(
                                float(
                                    region.centroid[
                                        0
                                    ]
                                ),
                                2
                            ),

                            round(
                                float(
                                    region.centroid[
                                        1
                                    ]
                                ),
                                2
                            )
                        ],

                    "solidez":
                        round(
                            float(
                                region.solidity
                            ),
                            4
                        ),

                    "excentricidad":
                        round(
                            float(
                                region.eccentricity
                            ),
                            4
                        )
                }
            )


        # Región más grande primero.

        regiones.sort(
            key=lambda region:
                region[
                    "area"
                ],
            reverse=True
        )


        return (
            etiquetas,
            regiones
        )


    # ======================================================
    # EXTRAER REGIÓN PRINCIPAL
    # ======================================================

    def extraer_region_principal(
        self,
        imagen_gris,
        regiones
    ):

        if not regiones:

            return None


        principal = (
            regiones[
                0
            ]
        )


        (
            fila_min,
            columna_min,
            fila_max,
            columna_max
        ) = principal[
            "bbox"
        ]


        recorte = imagen_gris[
            fila_min:fila_max,
            columna_min:columna_max
        ]


        if recorte.size == 0:

            return None


        recorte_uint8 = (
            np.clip(
                recorte
                * 255.0,
                0,
                255
            )
            .astype(
                np.uint8
            )
        )


        Image.fromarray(
            recorte_uint8
        ).save(
            ARTIFACT_REGION
        )


        return {
            "archivo":
                str(
                    ARTIFACT_REGION
                ),

            "area":
                principal[
                    "area"
                ],

            "bbox":
                principal[
                    "bbox"
                ]
        }


    # ======================================================
    # COMPARAR SIGMA
    # ======================================================

    def comparar_sigma(
        self,
        imagen_gris,
        valores=None
    ):

        if valores is None:

            valores = [
                0.5,
                1.0,
                2.0,
                3.0
            ]


        comparacion = []


        for sigma in valores:

            bordes = (
                self.detectar_bordes(
                    imagen_gris,
                    sigma=sigma
                )
            )


            cantidad_bordes = int(
                np.count_nonzero(
                    bordes
                )
            )


            comparacion.append(
                {
                    "sigma":
                        float(
                            sigma
                        ),

                    "pixeles_borde":
                        cantidad_bordes,

                    "porcentaje_borde":
                        round(
                            porcentaje(
                                cantidad_bordes,
                                bordes.size
                            ),
                            4
                        )
                }
            )


        return comparacion


    # ======================================================
    # GENERAR EVIDENCIA VISUAL
    # ======================================================

    def generar_evidencia(
        self,
        matriz_rgb,
        bordes,
        mascara,
        etiquetas,
        umbral,
        sigma
    ):

        figura, ejes = plt.subplots(
            1,
            4,
            figsize=(
                16,
                4.5
            )
        )


        # ==================================================
        # ORIGINAL
        # ==================================================

        ejes[
            0
        ].imshow(
            matriz_rgb
        )


        ejes[
            0
        ].set_title(
            "Original"
        )


        # ==================================================
        # CANNY
        # ==================================================

        ejes[
            1
        ].imshow(
            bordes,
            cmap="gray"
        )


        ejes[
            1
        ].set_title(
            (
                "Canny\n"
                f"sigma = {sigma}"
            )
        )


        # ==================================================
        # OTSU
        # ==================================================

        ejes[
            2
        ].imshow(
            mascara,
            cmap="gray"
        )


        ejes[
            2
        ].set_title(
            (
                "Otsu\n"
                f"umbral = {umbral:.4f}"
            )
        )


        # ==================================================
        # REGIONES
        # ==================================================

        ejes[
            3
        ].imshow(
            etiquetas,
            cmap="nipy_spectral"
        )


        ejes[
            3
        ].set_title(
            (
                "Regiones conectadas\n"
                f"{int(etiquetas.max())}"
            )
        )


        for eje in ejes:

            eje.axis(
                "off"
            )


        figura.tight_layout()


        figura.savefig(
            ARTIFACT_IMAGE,
            dpi=160,
            bbox_inches="tight"
        )


        plt.close(
            figura
        )


        return str(
            ARTIFACT_IMAGE
        )


    # ======================================================
    # GENERAR REPORTE MARKDOWN
    # ======================================================

    def generar_reporte(
        self,
        resultado
    ):

        lineas_sigma = []


        for item in (
            resultado[
                "comparacion_sigma"
            ]
        ):

            lineas_sigma.append(
                (
                    f"- Sigma {item['sigma']}: "
                    f"{item['pixeles_borde']} "
                    "píxeles de borde "
                    f"({item['porcentaje_borde']:.4f}%)."
                )
            )


        comparacion_texto = (
            "\n".join(
                lineas_sigma
            )
        )


        region_principal = (
            resultado.get(
                "region_principal"
            )
            or {}
        )


        archivo_region = (
            region_principal.get(
                "archivo"
            )
            or (
                "No se generó una "
                "región principal."
            )
        )


        contenido = f"""# Semana 09 - Reconocimiento de imágenes

## 1. Imagen utilizada y relación con el proyecto

La imagen utilizada corresponde al archivo:

`data/imagen_proyecto.png`

La imagen representa una entrada visual relacionada con HIS_IA. El objetivo es preparar imágenes del sector salud o documentos clínicos para etapas posteriores como reconocimiento, clasificación, OCR o validación visual.

Archivo de origen analizado:

`{resultado['archivo_original']}`

## 2. Resultado de Canny

Se utilizó el detector de bordes Canny con:

**sigma = {resultado['sigma']}**

Cantidad de píxeles identificados como borde:

**{resultado['pixeles_borde']}**

Porcentaje aproximado de píxeles de borde:

**{resultado['porcentaje_borde']:.4f}%**

Canny permite identificar cambios importantes de intensidad y aproximar los límites de estructuras visibles.

## 3. Umbral Otsu obtenido

El umbral automático calculado fue:

**{resultado['umbral_otsu']:.6f}**

Este valor se utilizó para crear una máscara binaria que separa regiones de interés respecto al fondo de la imagen.

## 4. Número de regiones encontradas

El sistema identificó:

**{resultado['regiones_detectadas']} regiones conectadas**

Las regiones corresponden a grupos de píxeles conectados después de aplicar la segmentación.

El número de regiones no representa necesariamente el número real de objetos presentes en la imagen.

## 5. Cambios realizados al modificar sigma

{comparacion_texto}

Con valores bajos de sigma se conserva más detalle, pero también puede aparecer más ruido.

Con valores altos se aplica un mayor suavizado, disminuyendo la cantidad de pequeños bordes detectados.

## 6. Limitaciones encontradas

- La iluminación afecta la segmentación.
- El contraste modifica el resultado de Otsu.
- El ruido puede producir bordes que no pertenecen a objetos reales.
- Una región conectada no equivale necesariamente a un objeto clínico.
- La región de mayor área no siempre corresponde a la estructura de interés.
- Los documentos escaneados pueden requerir posteriormente OCR.
- Este procesamiento visual no realiza diagnóstico médico.

## 7. Aplicación futura dentro del proyecto

Semana 9 se integra con HIS_IA como una etapa previa al reconocimiento.

Flujo propuesto:

`Imagen → escala de grises → Canny → Otsu → regiones → región de interés → reconocimiento`

La región de interés podrá utilizarse posteriormente como entrada para:

- OCR de documentos médicos.
- Reconocimiento de caracteres.
- Procesamiento de etiquetas de muestras.
- Validación visual.
- Integración con los módulos de reconocimiento de Semana 8.

## Evidencias generadas

Evidencia comparativa:

`{resultado['evidencia_visual']}`

Región principal:

`{archivo_region}`
"""


        REPORT_FILE.write_text(
            contenido,
            encoding="utf-8"
        )


        return str(
            REPORT_FILE
        )


    # ======================================================
    # ANALIZAR IMAGEN
    # ======================================================

    def analizar_imagen(
        self,
        ruta_imagen,
        sigma=None
    ):

        sigma_final = (

            self.sigma

            if sigma is None

            else float(
                sigma
            )
        )


        # ==================================================
        # 1. CARGAR
        # ==================================================

        (
            ruta,
            matriz_rgb
        ) = self.cargar_imagen(
            ruta_imagen
        )


        # ==================================================
        # 2. GUARDAR COMO IMAGEN DEL PROYECTO
        # ==================================================

        imagen_proyecto = (
            self.guardar_imagen_proyecto(
                matriz_rgb
            )
        )


        # ==================================================
        # 3. ESCALA DE GRISES
        # ==================================================

        imagen_gris = (
            self.convertir_grises(
                matriz_rgb
            )
        )


        # ==================================================
        # 4. CANNY
        # ==================================================

        bordes = (
            self.detectar_bordes(
                imagen_gris,
                sigma=sigma_final
            )
        )


        # ==================================================
        # 5. OTSU
        # ==================================================

        (
            umbral,
            mascara
        ) = self.segmentar_otsu(
            imagen_gris
        )


        # ==================================================
        # 6. REGIONES
        # ==================================================

        (
            etiquetas,
            regiones
        ) = self.detectar_regiones(
            mascara
        )


        # ==================================================
        # 7. REGIÓN PRINCIPAL
        # ==================================================

        region_principal = (
            self.extraer_region_principal(
                imagen_gris,
                regiones
            )
        )


        # ==================================================
        # 8. MÉTRICAS CANNY
        # ==================================================

        cantidad_bordes = int(
            np.count_nonzero(
                bordes
            )
        )


        porcentaje_bordes = round(
            porcentaje(
                cantidad_bordes,
                bordes.size
            ),
            4
        )


        # ==================================================
        # 9. EVIDENCIA VISUAL
        # ==================================================

        evidencia = (
            self.generar_evidencia(
                matriz_rgb=matriz_rgb,
                bordes=bordes,
                mascara=mascara,
                etiquetas=etiquetas,
                umbral=umbral,
                sigma=sigma_final
            )
        )


        # ==================================================
        # 10. COMPARAR SIGMAS
        # ==================================================

        comparacion_sigma = (
            self.comparar_sigma(
                imagen_gris
            )
        )


        # ==================================================
        # 11. RESULTADO
        # ==================================================

        resultado = {

            "archivo_original":
                str(
                    ruta
                ),

            "imagen_proyecto":
                imagen_proyecto,

            "sigma":
                float(
                    sigma_final
                ),

            "umbral_otsu":
                float(
                    umbral
                ),

            "pixeles_borde":
                cantidad_bordes,

            "porcentaje_borde":
                porcentaje_bordes,

            "regiones_detectadas":
                len(
                    regiones
                ),

            "regiones":
                regiones,

            "region_principal":
                (
                    region_principal
                    or {}
                ),

            "comparacion_sigma":
                comparacion_sigma,

            "evidencia_visual":
                evidencia
        }


        # ==================================================
        # 12. REPORTE
        # ==================================================

        resultado[
            "reporte"
        ] = self.generar_reporte(
            resultado
        )


        return resultado


# ==========================================================
# FUNCIÓN PARA INTEGRAR CON HIS_IA
# ==========================================================

def analizar_imagen_semana9(
    ruta_imagen,
    sigma=2.0,
    area_minima=20
):

    procesador = (
        ProcesadorVisionSemana9(
            sigma=sigma,
            area_minima=area_minima
        )
    )


    return (
        procesador.analizar_imagen(
            ruta_imagen,
            sigma=sigma
        )
    )


# ==========================================================
# MOSTRAR RESULTADO
# ==========================================================

def imprimir_resultado(
    resultado
):

    print(
        "\n"
        + "=" * 65
    )


    print(
        "SEMANA 9 - RECONOCIMIENTO DE IMÁGENES"
    )


    print(
        "=" * 65
    )


    print(
        "Imagen:",
        resultado[
            "archivo_original"
        ]
    )


    print(
        "Sigma:",
        resultado[
            "sigma"
        ]
    )


    print(
        "Umbral Otsu:",
        round(
            resultado[
                "umbral_otsu"
            ],
            6
        )
    )


    print(
        "Píxeles de borde:",
        resultado[
            "pixeles_borde"
        ]
    )


    print(
        "Porcentaje de borde:",
        (
            f"{resultado['porcentaje_borde']:.4f}%"
        )
    )


    print(
        "Regiones detectadas:",
        resultado[
            "regiones_detectadas"
        ]
    )


    print(
        "\nEvidencia visual:"
    )


    print(
        resultado[
            "evidencia_visual"
        ]
    )


    region = (
        resultado.get(
            "region_principal"
        )
        or {}
    )


    if region:

        print(
            "\nRegión principal:"
        )


        print(
            region.get(
                "archivo"
            )
        )


        print(
            "Área:",
            region.get(
                "area"
            )
        )


    print(
        "\nComparación de sigma"
    )


    print(
        "-" * 65
    )


    for item in (
        resultado[
            "comparacion_sigma"
        ]
    ):

        print(
            (
                f"Sigma {item['sigma']}: "
                f"{item['pixeles_borde']} "
                "píxeles de borde "
                f"({item['porcentaje_borde']:.4f}%)"
            )
        )


    print(
        "\nReporte:"
    )


    print(
        resultado[
            "reporte"
        ]
    )


    print(
        "=" * 65
    )


# ==========================================================
# CONSOLA
# ==========================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Semana 9 de HIS_IA: "
            "Canny, Otsu y regiones conectadas."
        )
    )


    parser.add_argument(
        "imagen",
        nargs="?",
        default=str(
            DEFAULT_IMAGE
        ),
        help=(
            "Ruta de la imagen a analizar. "
            "Si se omite usa data/imagen_proyecto.png."
        )
    )


    parser.add_argument(
        "--sigma",
        type=float,
        default=2.0,
        help=(
            "Sigma utilizado por Canny. "
            "Valor por defecto: 2.0"
        )
    )


    parser.add_argument(
        "--area-minima",
        type=int,
        default=20,
        help=(
            "Área mínima de una región conectada. "
            "Valor por defecto: 20"
        )
    )


    parser.add_argument(
        "--json",
        action="store_true",
        help=(
            "Muestra también el resultado "
            "completo en JSON."
        )
    )


    argumentos = (
        parser.parse_args()
    )


    procesador = (
        ProcesadorVisionSemana9(
            sigma=argumentos.sigma,
            area_minima=argumentos.area_minima
        )
    )


    resultado = (
        procesador.analizar_imagen(
            argumentos.imagen,
            sigma=argumentos.sigma
        )
    )


    imprimir_resultado(
        resultado
    )


    if argumentos.json:

        print(
            "\nRESULTADO JSON"
        )


        print(
            json.dumps(
                resultado,
                indent=2,
                ensure_ascii=False,
                default=convertir_json
            )
        )


# ==========================================================
# EJECUCIÓN
# ==========================================================

if __name__ == "__main__":

    main()