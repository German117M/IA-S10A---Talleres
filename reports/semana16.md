# Semana 16 - Diseño de sistemas inteligentes

## Arquitectura de sistemas inteligentes y motor de referencia aplicado a HIS_IA

## 1. Objetivo

Implementar un motor de referencia dentro del proyecto HIS_IA que permita recibir una pregunta, normalizar su contenido, consultar conocimiento previamente validado, seleccionar la referencia más pertinente y devolver una respuesta trazable con identificador, fuente y metadatos.

El sistema debe abstenerse cuando no exista conocimiento aprobado suficiente para responder.

## 2. Integración con HIS_IA

Semana 16 se implementó como una nueva capa sobre la base de conocimiento desarrollada en Semana 15.

La relación entre ambas semanas es:

    Semana 15
    Base de conocimiento
    Artículos BORRADOR / VALIDADO
            ↓
    Semana 16
    Motor de referencia
            ↓
    Recuperación de conocimiento VALIDADO

Semana 16 no modifica los artículos ni la estructura de Semana 15.

Únicamente consulta los artículos que tienen estado:

    VALIDADO

## 3. Arquitectura

La arquitectura implementada contiene los siguientes componentes:

    Usuario
       ↓
    Interfaz HIS_IA
       ↓
    Pregunta
       ↓
    Normalización
       ↓
    Motor de referencia
       ↓
    Base de conocimiento Semana 15
       ↓
    Selección de referencia validada
       ↓
    Respuesta + ID + fuente
       ↓
    Interfaz web

Cada componente tiene una responsabilidad específica.

## 4. Diferencia entre motor de referencia y motor de inferencia

### Motor de inferencia

Utilizado en Semana 13.

Trabaja con:

    hechos
      +
    reglas
      ↓
    conclusión nueva

Ejemplo:

    SI prioridad_alta
    Y resultados_pendientes
    ENTONCES requiere_seguimiento

### Motor de referencia

Utilizado en Semana 16.

Trabaja con:

    pregunta
       +
    conocimiento aprobado
       ↓
    referencia existente

No crea una nueva conclusión.

Selecciona una respuesta que ya existe dentro de la base de conocimiento.

## 5. Archivo principal

La implementación se encuentra en:

    src/semana16_motor_referencia.py

Las funciones principales son:

    normalizar()
    obtener_referencias_validadas()
    obtener_claves_referencia()
    consultar()

## 6. Normalización

La función:

    normalizar()

prepara la pregunta antes de realizar la búsqueda.

Realiza:

- conversión a minúsculas;
- eliminación de tildes;
- separación de palabras;
- eliminación de palabras poco útiles;
- eliminación de términos repetidos.

Ejemplo:

    ¿Cómo se crea una orden de Laboratorio?

se transforma aproximadamente en:

    crea
    orden
    laboratorio

Esto permite comparar palabras sin depender de mayúsculas o tildes.

## 7. Palabras vacías

Se definió un conjunto de términos que aportan poco a la búsqueda:

    de
    la
    el
    como
    que
    para
    una
    un
    entre otros

Estas palabras se eliminan antes de calcular las coincidencias.

## 8. Base de conocimiento utilizada

Semana 16 reutiliza:

    data/semana15_conocimiento.db

No se creó una segunda base de datos.

El motor consulta las tablas creadas en Semana 15 y recupera únicamente artículos cuyo estado sea:

    VALIDADO

Esto evita duplicar conocimiento.

## 9. Referencias

Cada artículo validado puede utilizarse como una referencia.

El motor devuelve un identificador con el formato:

    ART-001
    ART-002
    ART-003

El número corresponde al identificador del artículo almacenado en SQLite.

La referencia también conserva:

- título;
- dominio;
- aplicación;
- responsable;
- herramienta;
- fuente;
- fecha de revisión;
- estado;
- coincidencias;
- términos coincidentes.

## 10. Algoritmo del motor

El funcionamiento general es:

    Pregunta
       ↓
    Normalizar texto
       ↓
    Obtener artículos VALIDADO
       ↓
    Generar palabras clave
       ↓
    Comparar pregunta con cada artículo
       ↓
    Contar coincidencias
       ↓
    Ordenar candidatos
       ↓
    Seleccionar mejor referencia
       ↓
    Devolver respuesta y fuente

Si dos referencias tienen la misma cantidad de coincidencias, el sistema utiliza el menor ID para mantener un comportamiento determinista.

## 11. Puntuación

La puntuación corresponde únicamente al número de términos coincidentes.

Ejemplo:

    Pregunta:
    ¿Cómo se crea una orden de laboratorio?

Términos útiles:

    crea
    orden
    laboratorio

Referencia seleccionada:

    ART-001

Coincidencias:

    laboratorio
    orden

Puntuación:

    2

El valor 2 no representa una probabilidad ni un porcentaje de confianza.

Significa únicamente que se encontraron dos términos en común.

## 12. Estados de respuesta

Se implementaron tres estados.

### ENCONTRADA

Existe una referencia validada relacionada con la consulta.

Ejemplo:

    ¿Cómo se crea una orden de laboratorio?

Resultado:

    ENCONTRADA

Referencia:

    ART-001

### SIN_REFERENCIA

No existe conocimiento validado suficiente.

Ejemplo:

    ¿Dónde parqueo mi bicicleta?

Resultado:

    SIN_REFERENCIA

También puede producirse si existe información relacionada pero permanece en estado BORRADOR.

### SIN_DATOS

La consulta está vacía o no contiene palabras útiles.

Resultado:

    SIN_DATOS

## 13. Ejemplos ejecutados

### Caso 1

Pregunta:

    ¿Cómo se crea una orden de laboratorio?

Resultado:

    Estado: ENCONTRADA
    Referencia: ART-001
    Coincidencias: 2

Términos:

    laboratorio
    orden

### Caso 2

Pregunta:

    ¿Cómo retornan los resultados LIS al HIS?

Resultado:

    Estado: ENCONTRADA
    Referencia: ART-002
    Coincidencias: 4

### Caso 3

Pregunta:

    ¿Dónde se almacenan las imágenes RIS?

Resultado:

    Estado: ENCONTRADA
    Referencia: ART-003
    Coincidencias: 3

### Caso 4

Pregunta:

    ¿Dónde parqueo mi bicicleta?

Resultado:

    SIN_REFERENCIA

El sistema no inventa una respuesta.

## 14. Abstención

Una característica importante del motor es su capacidad de abstenerse.

Si no existe una referencia VALIDADO relacionada con la consulta, el sistema responde:

    No hay evidencia validada para responder esta consulta.
    Se recomienda revisión humana.

Esto evita generar información que no existe en la base de conocimiento.

## 15. Pruebas automatizadas

Archivo:

    tests/test_semana16_motor_referencia.py

Se implementaron cinco pruebas.

### Prueba 1

Comprueba la normalización de tildes.

    RADIOLOGÍA
        ↓
    radiologia

### Prueba 2

Comprueba que una consulta conocida encuentra una referencia validada.

Resultado esperado:

    ENCONTRADA
    ART-001

### Prueba 3

Comprueba que el sistema no inventa respuestas fuera de cobertura.

Resultado esperado:

    SIN_REFERENCIA

### Prueba 4

Comprueba que un artículo BORRADOR no puede utilizarse como referencia.

Resultado esperado:

    SIN_REFERENCIA

### Prueba 5

Comprueba una consulta vacía.

Resultado esperado:

    SIN_DATOS

Resultado de ejecución:

    Ran 5 tests in 0.094s

    OK

## 16. Integración con Flask

Semana 16 fue integrada al backend de HIS_IA mediante:

    POST /api/semana16/consultar

El endpoint recibe:

    {
        "pregunta":
        "¿Cómo se crea una orden de laboratorio?"
    }

y devuelve:

    estado
    mensaje
    palabras_consulta
    referencia

La referencia contiene la trazabilidad completa del conocimiento utilizado.

## 17. Integración web

Semana 16 fue agregada como una nueva sección dentro del menú de HIS_IA.

La interfaz permite:

- escribir una pregunta;
- consultar el motor;
- visualizar el estado;
- visualizar la respuesta;
- identificar la referencia;
- visualizar la fuente;
- consultar dominio y aplicación;
- visualizar responsable y herramienta;
- visualizar términos coincidentes;
- visualizar la puntuación.

## 18. Relación entre Semanas 13, 14, 15 y 16

### Semana 13

    Hechos + reglas
       ↓
    Inferencia

Responde:

    ¿Qué conclusión se puede obtener?

### Semana 14

    Conceptos + relaciones
       ↓
    Red semántica

Responde:

    ¿Cómo está relacionado el conocimiento?

### Semana 15

    Artículos + responsables + fuentes + estados
       ↓
    Base de conocimiento

Responde:

    ¿Qué conocimiento aprobado existe?

### Semana 16

    Pregunta + referencias validadas
       ↓
    Motor de referencia

Responde:

    ¿Qué conocimiento aprobado responde mejor
    a esta pregunta y de dónde proviene?

## 19. Limitaciones

La implementación actual tiene las siguientes limitaciones:

- No utiliza aprendizaje automático.
- No aprende automáticamente de las consultas.
- No utiliza modelos de lenguaje.
- La búsqueda utiliza coincidencia de palabras.
- La puntuación no representa confianza estadística.
- No utiliza sinónimos avanzados.
- Depende de la calidad del conocimiento registrado en Semana 15.
- No utiliza artículos BORRADOR.
- Una consulta ambigua podría seleccionar una referencia poco específica.
- La revisión humana continúa siendo necesaria.

## 20. Conclusión

Semana 16 permitió incorporar una arquitectura de recuperación de conocimiento trazable dentro de HIS_IA.

El sistema recibe una pregunta, normaliza el texto, consulta únicamente conocimiento aprobado, compara términos, selecciona la referencia más pertinente y devuelve la respuesta junto con su identificador y fuente.

La integración con Semana 15 evita duplicar información y demuestra una arquitectura modular en la que una capa administra y valida el conocimiento y otra capa lo recupera.

El motor también puede abstenerse cuando no existe evidencia suficiente, evitando fabricar respuestas sin respaldo.

## Respuesta corta para sustentación

En la Semana 16 implementé un motor de referencia integrado con la base de conocimiento de Semana 15. El sistema normaliza la pregunta, consulta únicamente artículos VALIDADOS, cuenta las coincidencias, selecciona la mejor referencia y devuelve la respuesta junto con su ID y fuente. Si no existe conocimiento aprobado relacionado, devuelve SIN_REFERENCIA y no inventa una respuesta.
