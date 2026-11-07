# Semana 14 - Redes semánticas aplicadas a HIS_IA

## 1. Objetivo

Implementar una red semántica aplicada al proyecto HIS_IA para representar conceptos y relaciones del dominio HIS-LIS-RIS mediante triples sujeto-relación-objeto, permitiendo consultas, inferencias jerárquicas y transformación de oraciones simples.

## 2. Dominio utilizado

La práctica fue adaptada a la interoperabilidad entre HIS, LIS y RIS.

Conceptos principales:

- Paciente
- Orden diagnóstica
- Orden de laboratorio
- Orden de radiología
- HIS
- LIS
- RIS
- Resultado de laboratorio
- Resultado diagnóstico
- Imagen
- Informe radiológico
- PACS

## 3. Representación mediante triples

El conocimiento se representa utilizando:

    (sujeto, relación, objeto)

Ejemplos:

    (orden_laboratorio, es_un, orden_diagnostica)
    (orden_laboratorio, se_envia_a, lis)
    (lis, genera, resultado_laboratorio)
    (resultado_laboratorio, retorna_a, his)
    (orden_radiologia, se_envia_a, ris)
    (ris, genera, imagen)
    (ris, genera, informe_radiologico)
    (imagen, se_almacena_en, pacs)

Los conceptos funcionan como nodos y las relaciones como conexiones dirigidas.

## 4. Inferencia jerárquica

La relación `es_un` permite determinar si un concepto pertenece a una categoría.

Ejemplo:

    orden_laboratorio
        es_un
    orden_diagnostica

La consulta:

    ¿Orden de laboratorio es una orden diagnóstica?

produce:

    True

La búsqueda utiliza un conjunto de nodos visitados para evitar ciclos infinitos.

## 5. Herencia de propiedades

La red permite heredar propiedades desde una categoría superior.

Se tienen las relaciones:

    orden_laboratorio es_un orden_diagnostica
    orden_diagnostica se_registra_en his

Aunque no exista directamente:

    orden_laboratorio se_registra_en his

el sistema puede inferir que una orden de laboratorio se registra en HIS.

Resultado:

    ['his']

La misma inferencia se aplica a la orden de radiología.

## 6. Búsqueda de caminos

Se implementó una búsqueda de caminos entre conceptos.

Ejemplo:

    Origen: orden_laboratorio
    Destino: his

Camino obtenido:

    orden_laboratorio
        --es_un-->
    orden_diagnostica
        --se_registra_en-->
    his

## 7. Conversión de oraciones a triples

Se implementó un analizador de lenguaje controlado.

Entrada:

    La orden de laboratorio se envía al LIS

Resultado:

    ('orden_laboratorio', 'se_envia_a', 'lis')

También reconoce frases relacionadas con órdenes de radiología, LIS, RIS, resultados, imágenes y PACS.

El analizador no interpreta lenguaje natural general. Utiliza patrones definidos específicamente para el dominio HIS_IA.

## 8. Integración web

Semana 14 fue integrada a la aplicación web HIS_IA.

Endpoints implementados:

    GET  /api/semana14/red
    POST /api/semana14/consultar
    POST /api/semana14/oracion

La interfaz permite:

- Consultar relaciones directas.
- Consultar jerarquías.
- Consultar propiedades heredadas.
- Buscar caminos entre conceptos.
- Convertir oraciones en triples.
- Visualizar los triples registrados.

Actualmente la red contiene 14 triples.

## 9. Pruebas automáticas

Se implementaron 8 pruebas con `unittest`:

1. Relación directa.
2. Inferencia jerárquica.
3. Herencia de propiedades.
4. Búsqueda de caminos.
5. Conversión de oración a triple.
6. Rechazo de oraciones no reconocidas.
7. Prevención de ciclos.
8. Incorporación de oraciones a la red.

Resultado:

    Ran 8 tests
    OK

## 10. Diferencia con Semana 13

Semana 13 utiliza:

    Hechos + Reglas + Encadenamiento hacia adelante

Su objetivo es producir conclusiones y acciones.

Semana 14 utiliza:

    Conceptos + Relaciones + Red semántica

Su objetivo es representar cómo se conecta el conocimiento y realizar inferencias sobre esas conexiones.

## 11. Limitaciones

- El lenguaje natural está limitado a patrones controlados.
- No utiliza procesamiento avanzado de lenguaje natural.
- La red representa una parte del dominio HIS_IA.
- No realiza diagnósticos médicos.
- Las inferencias dependen de relaciones previamente definidas.

## 12. Conclusión

La Semana 14 permitió incorporar redes semánticas al proyecto HIS_IA.

El sistema representa conceptos relacionados con HIS, LIS y RIS mediante triples, consulta relaciones, realiza inferencias jerárquicas, hereda propiedades, busca caminos entre conceptos y transforma frases sencillas en conocimiento estructurado.

Esto complementa el motor de reglas de Semana 13 con una representación explícita de las relaciones existentes entre los conceptos del dominio.

## Respuesta corta para sustentación

En la Semana 14 implementé una red semántica aplicada a HIS_IA. Representé conceptos como HIS, LIS, RIS, órdenes, resultados e imágenes mediante triples sujeto-relación-objeto. La red permite consultas directas, inferencias jerárquicas, herencia de propiedades, búsqueda de caminos y conversión de oraciones simples en triples semánticos.
