PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS dominio (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS aplicacion (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    dominio_id INTEGER NOT NULL
        REFERENCES dominio(id)
);

CREATE TABLE IF NOT EXISTS experto (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    cargo TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS herramienta (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    finalidad TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS articulo (
    id INTEGER PRIMARY KEY,
    titulo TEXT NOT NULL,
    contenido TEXT NOT NULL,

    dominio_id INTEGER NOT NULL
        REFERENCES dominio(id),

    aplicacion_id INTEGER
        REFERENCES aplicacion(id),

    experto_id INTEGER NOT NULL
        REFERENCES experto(id),

    herramienta_id INTEGER
        REFERENCES herramienta(id),

    fuente TEXT NOT NULL,

    fecha_revision TEXT NOT NULL,

    estado TEXT NOT NULL DEFAULT 'BORRADOR'
        CHECK (
            estado IN (
                'BORRADOR',
                'VALIDADO'
            )
        ),

    UNIQUE (
        titulo,
        dominio_id
    )
);

CREATE INDEX IF NOT EXISTS
idx_semana15_articulo_dominio_estado
ON articulo(
    dominio_id,
    estado
);
