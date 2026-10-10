# Semana 10 - Reconocimiento de imágenes

## Objetivo

Transformar una imagen en un vector de características numéricas mediante:

- Segmentación Otsu.
- Etiquetado de regiones.
- Área media de regiones.
- Desviación de áreas.
- Histograma de intensidad.
- Textura LBP.

## Flujo

Imagen → Otsu → Regiones → Histograma → LBP → Vector de características

## Archivos generados

- `artifacts/semana10_features.npy`
- `artifacts/semana10_histograma.png`

## Observación

El procesamiento visual genera características numéricas reutilizables por análisis o modelos posteriores de Inteligencia Artificial.
