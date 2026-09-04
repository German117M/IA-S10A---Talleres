# Semana 05 - Sistema híbrido

## Objetivo
Aplicar sistemas expertos, recuperación de información, clasificación y procesamiento de lenguaje natural.

## Consulta 1

**Consulta:** Internet se cae y aparece error DNS

**Regla activada:** revisar_conectividad

**Evidencia recuperada:** Cuando un equipo no tiene conexión a internet se debe revisar red, DNS, gateway y conectividad.

**Similitud:** 0.492

**Clasificación:** red

## Consulta 2

**Consulta:** El equipo está caliente y el ventilador hace ruido

**Regla activada:** revisar_ventilacion

**Evidencia recuperada:** Cuando una cuenta está bloqueada se deben validar credenciales, permisos y estado del usuario.

**Similitud:** 0.277

**Clasificación:** hardware

## Consulta 3

**Consulta:** No puedo iniciar sesión porque mi cuenta está bloqueada

**Regla activada:** revisar_acceso

**Evidencia recuperada:** Cuando una cuenta está bloqueada se deben validar credenciales, permisos y estado del usuario.

**Similitud:** 0.441

**Clasificación:** acceso

## Análisis

El sistema combina reglas expertas, recuperación mediante TF-IDF y similitud coseno, y clasificación automática de texto.

La respuesta es trazable porque permite identificar la regla utilizada, la evidencia recuperada, el valor de similitud y la clase predicha.

## Limitaciones

El sistema depende de las reglas, documentos y ejemplos utilizados durante su construcción. Una base pequeña puede producir clasificaciones o recuperaciones poco precisas.