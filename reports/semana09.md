# Semana 09 - Reconocimiento de imágenes

## 1. Imagen utilizada y relación con el proyecto

La imagen utilizada corresponde al archivo:

`data/imagen_proyecto.png`

La imagen representa una entrada visual relacionada con HIS_IA. El objetivo es preparar imágenes del sector salud o documentos clínicos para etapas posteriores como reconocimiento, clasificación, OCR o validación visual.

Archivo de origen analizado:

`/Users/germanmanrique/Downloads/mi_imagen.jpg`

## 2. Resultado de Canny

Se utilizó el detector de bordes Canny con:

**sigma = 2.0**

Cantidad de píxeles identificados como borde:

**2787**

Porcentaje aproximado de píxeles de borde:

**0.7492%**

Canny permite identificar cambios importantes de intensidad y aproximar los límites de estructuras visibles.

## 3. Umbral Otsu obtenido

El umbral automático calculado fue:

**0.517578**

Este valor se utilizó para crear una máscara binaria que separa regiones de interés respecto al fondo de la imagen.

## 4. Número de regiones encontradas

El sistema identificó:

**4 regiones conectadas**

Las regiones corresponden a grupos de píxeles conectados después de aplicar la segmentación.

El número de regiones no representa necesariamente el número real de objetos presentes en la imagen.

## 5. Cambios realizados al modificar sigma

- Sigma 0.5: 3318 píxeles de borde (0.8919%).
- Sigma 1.0: 3249 píxeles de borde (0.8734%).
- Sigma 2.0: 2787 píxeles de borde (0.7492%).
- Sigma 3.0: 2607 píxeles de borde (0.7008%).

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

`/Users/germanmanrique/Documents/ia_semestre/artifacts/semana09_vision.png`

Región principal:

`/Users/germanmanrique/Documents/ia_semestre/artifacts/semana09_region_principal.png`
