# Semana 13 - Ingeniería del conocimiento en HIS_IA

## Objetivo
Implementar un motor de inferencia basado en reglas dentro de HIS_IA, utilizando hechos, reglas explícitas, encadenamiento hacia adelante y trazabilidad.

## Integración con el proyecto
Semana 13 recibe información de:

- Semana 7: temperatura, frecuencia cardíaca, presión y hallazgos.
- Semana 11: prioridad, nivel de acuerdo y recomendación de revisión.

Luego transforma esa información en hechos y aplica reglas para generar acciones recomendadas.

## Hechos principales
- prioridad_alta
- prioridad_normal
- documentos_pendientes
- documentos_completos
- resultados_pendientes
- resultados_completos
- imagenes_pendientes
- imagenes_completas
- revision_recomendada

## Reglas

### R1
prioridad_alta + resultados_pendientes -> requiere_seguimiento

### R2
requiere_seguimiento + imagenes_pendientes -> validar_resultados_diagnosticos

### R3
prioridad_alta + revision_recomendada -> revision_manual_prioritaria

### R4
prioridad_alta + documentos_pendientes -> completar_documentacion

### R5
documentos_completos + resultados_completos + imagenes_completas -> caso_listo_para_cierre

## Encadenamiento hacia adelante
El motor parte de los hechos iniciales y revisa todas las reglas.

Si las premisas de una regla están presentes, se agrega su conclusión como un nuevo hecho.

Ese nuevo hecho puede activar posteriormente otras reglas.

Ejemplo:

prioridad_alta + resultados_pendientes
-> requiere_seguimiento

requiere_seguimiento + imagenes_pendientes
-> validar_resultados_diagnosticos

## Integración real probada

Caso utilizado:

- Edad: 76
- Temperatura: 38.5
- Frecuencia cardíaca: 90
- Presión arterial: 150
- Documentos pendientes: 1
- Resultados pendientes: 3
- Imágenes pendientes: 2

### Semana 7
Se identificaron:

- Temperatura: Fiebre
- Frecuencia cardíaca: Inadecuado
- Presión arterial: Hipertensión nivel 1

### Semana 11
Resultado:

- Random Forest: Prioritaria
- Logistic Regression: Prioritaria
- MLP: Prioritaria
- Nivel de acuerdo: Alto
- Coincidencia: 3 de 3

### Semana 13
Reglas activadas:

- R1 -> requiere_seguimiento
- R2 -> validar_resultados_diagnosticos
- R4 -> completar_documentacion

Acciones recomendadas:

- Completar documentación pendiente.
- Realizar seguimiento al caso.
- Validar resultados diagnósticos e imágenes pendientes.

## Pruebas automáticas

Se implementaron cinco pruebas con unittest:

1. Caso prioritario con pendientes.
2. Caso normal sin pendientes.
3. Verificación de no mutación de hechos iniciales.
4. Reglas circulares sin ciclo infinito.
5. Caso con premisas insuficientes.

Resultado:

Ran 5 tests
OK

## Integración web

Se agregó:

POST /api/semana13/analizar

Y una sección visual de Semana 13 en HIS_IA.

La interfaz muestra:

- Prioridad
- Nivel de acuerdo
- Estado del caso
- Hallazgos
- Interpretación
- Acciones recomendadas
- Reglas activadas

## Limitaciones

- No realiza diagnóstico médico.
- No genera reglas automáticamente.
- Trabaja con reglas explícitas.
- No utiliza lógica difusa.
- No interpreta lenguaje natural general.
- La ausencia de un hecho no significa que su contrario sea verdadero.

## Conclusión

Semana 13 agrega ingeniería del conocimiento a HIS_IA.

Semana 11 determina la prioridad mediante aprendizaje automático.

Semana 13 utiliza esa prioridad, junto con los hallazgos y pendientes del caso, para aplicar reglas explicables y recomendar acciones.

## Sustentación corta

Semana 13 implementa un motor de inferencia basado en reglas.

Toma hechos obtenidos de Semana 7 y Semana 11, aplica encadenamiento hacia adelante y genera conclusiones explicables.

A diferencia de Semana 11, no entrena un modelo. Utiliza conocimiento explícito mediante hechos y reglas.
