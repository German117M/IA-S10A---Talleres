# Semana 8 - Representaciones del reconocimiento

## Proyecto

HIS_IA - Sistema Inteligente Híbrido aplicado al dominio clínico.

## Objetivo

Integrar reconocimiento mediante red neuronal MLP, evidencia persistente en SQLite, procesamiento documental, interpretación clínica orientativa y una ontología GraphML.

## Red neuronal

- Dataset: `sklearn.datasets.load_digits`.
- Entrada: imágenes de 8x8 convertidas en 64 valores.
- Modelo: `MLPClassifier` con una capa oculta de 64 neuronas.
- Accuracy registrado: **0.9622**.
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

- Documentos: 11.
- Resultados extraídos: 56.
- Imágenes reconocidas: 2.
- Interpretaciones clínicas: 4.
- Condiciones orientativas registradas: 4.

## Ontología

Archivo: `artifacts/ontologia.graphml`.

- Nodos: 134.
- Relaciones: 164.

La ontología incluye relaciones entre documentos, pacientes, exámenes, resultados, rangos, clasificaciones y condiciones clínicas orientativas.

## Limitaciones

- La MLP fue entrenada con `load_digits`.
- La extracción depende de la estructura textual del PDF.
- Los PDF escaneados todavía requieren OCR.
- La interpretación utiliza principalmente los rangos incluidos en el propio documento.
- Los resultados deben ser correlacionados con el contexto clínico.
- HIS_IA no establece diagnósticos médicos.