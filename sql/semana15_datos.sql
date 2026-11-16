INSERT OR IGNORE INTO dominio
    (id, nombre)
VALUES
    (1, 'Historia Clínica'),
    (2, 'Laboratorio'),
    (3, 'Radiología'),
    (4, 'Integración');


INSERT OR IGNORE INTO aplicacion
    (id, nombre, dominio_id)
VALUES
    (1, 'HIS', 1),
    (2, 'LIS', 2),
    (3, 'RIS', 3),
    (4, 'PACS', 3),
    (5, 'Motor de Integración', 4);


INSERT OR IGNORE INTO experto
    (id, nombre, cargo)
VALUES
    (
        1,
        'Ana Torres',
        'Responsable HIS'
    ),
    (
        2,
        'Carlos Rojas',
        'Responsable LIS'
    ),
    (
        3,
        'Laura Perez',
        'Responsable RIS'
    ),
    (
        4,
        'Miguel Castro',
        'Responsable de Integración'
    );


INSERT OR IGNORE INTO herramienta
    (id, nombre, finalidad)
VALUES
    (
        1,
        'Wiki HIS_IA',
        'Documentar conocimiento'
    ),
    (
        2,
        'Modulo de ordenes',
        'Gestionar ordenes diagnosticas'
    ),
    (
        3,
        'PACS',
        'Gestionar imagenes diagnosticas'
    ),
    (
        4,
        'Repositorio tecnico',
        'Conservar documentacion tecnica'
    );


INSERT OR IGNORE INTO articulo
(
    id,
    titulo,
    contenido,
    dominio_id,
    aplicacion_id,
    experto_id,
    herramienta_id,
    fuente,
    fecha_revision,
    estado
)
VALUES
(
    1,
    'Creacion de orden de laboratorio',
    'La orden se registra en HIS y se envia al LIS para su procesamiento.',
    2,
    2,
    2,
    2,
    'Procedimiento interno ficticio HIS_IA',
    '2026-11-16',
    'VALIDADO'
),
(
    2,
    'Retorno de resultados LIS hacia HIS',
    'Los resultados procesados en LIS retornan al HIS para su consulta.',
    2,
    2,
    2,
    1,
    'Manual ficticio de integracion HIS_IA',
    '2026-11-16',
    'VALIDADO'
),
(
    3,
    'Flujo de imagenes RIS hacia PACS',
    'Las imagenes generadas por RIS se almacenan en PACS.',
    3,
    3,
    3,
    3,
    'Procedimiento ficticio de radiologia',
    '2026-11-16',
    'VALIDADO'
),
(
    4,
    'Procedimiento de contingencia RIS',
    'Documento pendiente de revision para contingencias del modulo RIS.',
    3,
    3,
    3,
    4,
    'Borrador tecnico HIS_IA',
    '2026-11-16',
    'BORRADOR'
);
