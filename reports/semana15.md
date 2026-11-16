# Semana 15 - Base de conocimiento empresarial aplicada a HIS_IA

## 1. Objetivo

Implementar una base de conocimiento organizada para HIS_IA que permita clasificar información por dominios, aplicaciones, expertos y herramientas, conservar la fuente y fecha de revisión, y controlar la publicación mediante los estados BORRADOR y VALIDADO.

La práctica adapta el enfoque de organización del conocimiento empresarial al contexto HIS-LIS-RIS.

## 2. Concepto principal

La Semana 15 trabaja la organización del conocimiento empresarial.

Una base de conocimiento no es solamente una base de datos. La base de datos almacena registros y relaciones; la base de conocimiento organiza contenido reutilizable junto con su contexto, responsable, fuente y estado de revisión.

En HIS_IA se modelaron:

- Dominios
- Aplicaciones
- Expertos
- Herramientas
- Artículos de conocimiento

## 3. Dominios utilizados

Los dominios fueron adaptados al proyecto HIS_IA:

- Historia Clínica
- Laboratorio
- Radiología
- Integración

Cada dominio agrupa conocimientos relacionados con una misma área funcional.

## 4. Aplicaciones

Las aplicaciones indican dónde se utiliza el conocimiento.

Se registraron:

- HIS
- LIS
- RIS
- PACS
- Motor de Integración

Ejemplo:

    Dominio: Laboratorio
    Aplicación: LIS

Esto permite distinguir el área del conocimiento del sistema donde se aplica.

## 5. Expertos responsables

Cada artículo tiene un experto responsable.

Se utilizaron nombres ficticios:

- Ana Torres - Responsable HIS
- Carlos Rojas - Responsable LIS
- Laura Perez - Responsable RIS
- Miguel Castro - Responsable de Integración

El objetivo es representar la responsabilidad humana sobre la revisión y mantenimiento del conocimiento.

## 6. Herramientas

Se registraron herramientas asociadas al conocimiento:

- Wiki HIS_IA
- Modulo de ordenes
- PACS
- Repositorio tecnico

Las herramientas representan medios de captura, consulta o gestión del conocimiento.

## 7. Modelo de datos

La base de conocimiento utiliza cinco tablas principales:

    dominio
    aplicacion
    experto
    herramienta
    articulo

Relaciones principales:

    dominio
       |
       +---- aplicacion

    dominio
       |
       +---- articulo ---- experto
                 |
                 +---- aplicacion
                 |
                 +---- herramienta

Cada artículo tiene obligatoriamente:

- Título
- Contenido
- Dominio
- Experto
- Fuente
- Fecha de revisión
- Estado

La aplicación y herramienta pueden ser opcionales.

## 8. Estados editoriales

Se implementaron dos estados:

    BORRADOR
    VALIDADO

Todo artículo nuevo comienza automáticamente como:

    BORRADOR

Un artículo en estado BORRADOR existe en la base, pero no aparece en las búsquedas normales por dominio.

Después de ejecutar la validación:

    BORRADOR
        ↓
    VALIDADO

el artículo queda disponible para consulta.

## 9. Artículos iniciales

Se cargaron artículos ficticios relacionados con HIS_IA:

### Laboratorio

    Creacion de orden de laboratorio
    Estado: VALIDADO

    Retorno de resultados LIS hacia HIS
    Estado: VALIDADO

### Radiología

    Flujo de imagenes RIS hacia PACS
    Estado: VALIDADO

    Procedimiento de contingencia RIS
    Estado: BORRADOR

Esto permite demostrar la diferencia entre conocimiento publicado y contenido pendiente de revisión.

## 10. SQLite

Se utilizó SQLite como mecanismo de almacenamiento.

Archivos:

    sql/semana15_esquema.sql
    sql/semana15_datos.sql

Base generada:

    data/semana15_conocimiento.db

El esquema utiliza:

- PRIMARY KEY
- FOREIGN KEY
- NOT NULL
- UNIQUE
- CHECK

Las claves foráneas permiten impedir referencias a dominios, expertos, aplicaciones o herramientas inexistentes.

## 11. Lógica Python

La implementación principal se encuentra en:

    src/semana15_base_conocimiento.py

Funciones principales:

### conectar()

Administra la conexión SQLite, activa las claves foráneas, confirma transacciones correctas y realiza rollback en caso de error.

### inicializar_base()

Crea las tablas y carga los datos iniciales.

### listar_dominios()

Recupera los dominios disponibles.

### listar_aplicaciones()

Recupera aplicaciones y el dominio al que pertenecen.

### listar_expertos()

Recupera los expertos responsables.

### listar_herramientas()

Recupera las herramientas disponibles.

### buscar_articulos()

Consulta únicamente artículos con estado VALIDADO para un dominio específico.

### registrar_articulo()

Crea un nuevo artículo.

El estado inicial siempre es:

    BORRADOR

### validar_articulo()

Cambia el estado de un artículo existente a:

    VALIDADO

### listar_articulos()

Permite consultar todos los artículos, incluyendo BORRADOR y VALIDADO.

## 12. Flujo de conocimiento

El proceso implementado es:

    Captura de conocimiento
            ↓
    Clasificación por dominio
            ↓
    Asociación con aplicación
            ↓
    Asignación de experto
            ↓
    Asociación de herramienta y fuente
            ↓
    Estado BORRADOR
            ↓
    Revisión
            ↓
    VALIDADO
            ↓
    Disponible para consulta

## 13. Pruebas automatizadas

Se implementaron cinco pruebas con unittest:

1. Comprobar que las búsquedas solo muestran artículos VALIDADO.
2. Comprobar el ciclo registro → BORRADOR → VALIDADO.
3. Rechazar campos obligatorios vacíos.
4. Rechazar un dominio inexistente mediante integridad referencial.
5. Generar error al intentar validar un artículo inexistente.

Archivo:

    tests/test_semana15_base_conocimiento.py

Resultado esperado:

    Ran 5 tests
    OK

Las pruebas utilizan una base temporal independiente para no modificar la base principal del proyecto.

## 14. Integración con Flask

Semana 15 fue integrada al backend de HIS_IA.

Endpoints:

    GET /api/semana15/catalogos

Devuelve:

- dominios
- aplicaciones
- expertos
- herramientas

---

    GET /api/semana15/articulos

Sin parámetro devuelve todos los artículos.

Con:

    ?dominio=Laboratorio

devuelve únicamente artículos VALIDADO del dominio seleccionado.

---

    POST /api/semana15/articulos

Permite registrar un nuevo artículo.

El nuevo artículo se crea como:

    BORRADOR

---

    POST /api/semana15/articulos/<id>/validar

Permite cambiar un artículo de BORRADOR a VALIDADO.

## 15. Integración web

Semana 15 aparece en el menú principal de HIS_IA.

La interfaz incluye tres secciones.

### Buscar conocimiento validado

Permite seleccionar un dominio y consultar solo artículos aprobados.

### Registrar nuevo conocimiento

Permite registrar:

- título
- contenido
- dominio
- aplicación
- experto
- herramienta
- fuente

Todo registro comienza como BORRADOR.

### Gestión de artículos

Permite visualizar todos los artículos y validar aquellos que continúan en BORRADOR.

## 16. Diferencia entre Semanas 13, 14 y 15

### Semana 13

    Hechos + reglas
        ↓
    Conclusiones

Implementa un motor de inferencia mediante encadenamiento hacia adelante.

### Semana 14

    Conceptos + relaciones
        ↓
    Red semántica

Representa relaciones y permite inferencia jerárquica.

### Semana 15

    Conocimiento + contexto + responsable + estado
        ↓
    Base de conocimiento organizada

Su objetivo principal es organizar, validar y recuperar conocimiento.

## 17. Limitaciones

La implementación actual tiene las siguientes limitaciones:

- No implementa autenticación para validar artículos.
- No existe historial de versiones.
- Un artículo tiene un solo experto principal.
- La búsqueda actual se realiza por dominio exacto.
- No utiliza búsqueda semántica.
- No interpreta el contenido mediante modelos de lenguaje.
- Los datos utilizados son ficticios.
- No se incluyen datos clínicos sensibles.

## 18. Conclusión

La Semana 15 permitió incorporar organización y gobernanza del conocimiento al proyecto HIS_IA.

A diferencia de las semanas anteriores, el objetivo no es clasificar, inferir o interpretar automáticamente, sino garantizar que el conocimiento almacenado tenga contexto, fuente, responsable y estado de revisión.

La solución permite registrar conocimiento como BORRADOR, revisarlo, validarlo y posteriormente hacerlo visible para consulta.

Esto convierte la aplicación HIS_IA en una plataforma que no solo procesa información, sino que también puede conservar y organizar conocimiento operativo relacionado con HIS, LIS, RIS y PACS.

## Respuesta corta para sustentación

En la Semana 15 implementé una base de conocimiento empresarial adaptada a HIS_IA. Organicé artículos mediante dominios, aplicaciones, expertos y herramientas. Cada artículo conserva una fuente, fecha y estado. Los nuevos artículos comienzan como BORRADOR y solo aparecen en las búsquedas después de ser VALIDADOS. La información se almacena en SQLite y se integró con Flask y la interfaz web de HIS_IA.
