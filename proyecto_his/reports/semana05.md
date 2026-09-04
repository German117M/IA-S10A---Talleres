# Semana 05 - Sistema híbrido HIS_IA

## Descripción
HIS_IA integra reglas expertas, recuperación de información mediante TF-IDF y similitud coseno, clasificación de texto y procesamiento básico de lenguaje natural.

El sistema está orientado a apoyar la organización y recuperación de información dentro de un HIS.

## Consulta 1

**Consulta:** Tengo pendiente revisar el resultado de creatinina del paciente

**Regla activada:** revisar_resultados_laboratorio, evaluar_prioridad_revision

**Evidencia recuperada:** Un resultado de laboratorio pendiente debe identificarse para facilitar el seguimiento de la información clínica que aún no ha sido revisada.

**Similitud:** 0.286

**Clasificación:** laboratorio

## Consulta 2

**Consulta:** Hay una radiografía disponible para revisión

**Regla activada:** revisar_estudio_imagen

**Evidencia recuperada:** Un estudio de imagen pendiente debe quedar identificado para evitar que información diagnóstica disponible quede sin revisar.

**Similitud:** 0.302

**Clasificación:** imagen_diagnostica

## Consulta 3

**Consulta:** Necesito consultar los antecedentes y la evolución registrada en la historia clínica

**Regla activada:** revisar_historia_clinica

**Evidencia recuperada:** Los antecedentes médicos permiten conocer condiciones previas del paciente y deben ser considerados durante la revisión de la historia clínica.

**Similitud:** 0.379

**Clasificación:** historia_clinica

## Análisis

El resultado es explicable porque el sistema muestra qué regla fue activada, qué información recuperó, qué similitud obtuvo y qué categoría predijo.

## Limitaciones

La calidad de las respuestas depende de las reglas definidas, de la base de conocimiento y de los ejemplos utilizados para entrenar el clasificador.

Este prototipo académico organiza y recupera información. No interpreta resultados clínicos ni reemplaza la valoración de un profesional.