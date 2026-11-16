"""
Semana 15 - Base de conocimiento HIS_IA.
"""

from contextlib import contextmanager
from datetime import date
from pathlib import Path
import sqlite3


RAIZ = Path(__file__).resolve().parent.parent

RUTA_DB = RAIZ / "data" / "semana15_conocimiento.db"
RUTA_ESQUEMA = RAIZ / "sql" / "semana15_esquema.sql"
RUTA_DATOS = RAIZ / "sql" / "semana15_datos.sql"


@contextmanager
def conectar(ruta=RUTA_DB):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)

    conexion = sqlite3.connect(ruta)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")

    try:
        yield conexion
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def inicializar_base(ruta=RUTA_DB):
    with conectar(ruta) as conexion:
        conexion.executescript(
            RUTA_ESQUEMA.read_text(encoding="utf-8")
        )
        conexion.executescript(
            RUTA_DATOS.read_text(encoding="utf-8")
        )


def listar_dominios(ruta=RUTA_DB):
    with conectar(ruta) as conexion:
        filas = conexion.execute(
            """
            SELECT id, nombre
            FROM dominio
            ORDER BY nombre
            """
        ).fetchall()

        return [dict(fila) for fila in filas]


def listar_aplicaciones(ruta=RUTA_DB):
    with conectar(ruta) as conexion:
        filas = conexion.execute(
            """
            SELECT
                ap.id,
                ap.nombre,
                d.nombre AS dominio
            FROM aplicacion ap
            JOIN dominio d
                ON d.id = ap.dominio_id
            ORDER BY ap.nombre
            """
        ).fetchall()

        return [dict(fila) for fila in filas]


def listar_expertos(ruta=RUTA_DB):
    with conectar(ruta) as conexion:
        filas = conexion.execute(
            """
            SELECT id, nombre, cargo
            FROM experto
            ORDER BY nombre
            """
        ).fetchall()

        return [dict(fila) for fila in filas]


def listar_herramientas(ruta=RUTA_DB):
    with conectar(ruta) as conexion:
        filas = conexion.execute(
            """
            SELECT id, nombre, finalidad
            FROM herramienta
            ORDER BY nombre
            """
        ).fetchall()

        return [dict(fila) for fila in filas]


def buscar_articulos(dominio, ruta=RUTA_DB):
    consulta = """
        SELECT
            a.id,
            a.titulo,
            a.contenido,
            d.nombre AS dominio,
            ap.nombre AS aplicacion,
            e.nombre AS responsable,
            e.cargo AS cargo_responsable,
            h.nombre AS herramienta,
            a.fuente,
            a.fecha_revision,
            a.estado
        FROM articulo a
        JOIN dominio d
            ON d.id = a.dominio_id
        JOIN experto e
            ON e.id = a.experto_id
        LEFT JOIN aplicacion ap
            ON ap.id = a.aplicacion_id
        LEFT JOIN herramienta h
            ON h.id = a.herramienta_id
        WHERE
            d.nombre = ?
            AND a.estado = 'VALIDADO'
        ORDER BY a.titulo
    """

    with conectar(ruta) as conexion:
        filas = conexion.execute(
            consulta,
            (dominio,)
        ).fetchall()

        return [dict(fila) for fila in filas]


def registrar_articulo(
    titulo,
    contenido,
    dominio_id,
    experto_id,
    fuente,
    aplicacion_id=None,
    herramienta_id=None,
    ruta=RUTA_DB
):
    titulo = str(titulo).strip()
    contenido = str(contenido).strip()
    fuente = str(fuente).strip()

    if not titulo or not contenido or not fuente:
        raise ValueError(
            "Título, contenido y fuente son obligatorios."
        )

    with conectar(ruta) as conexion:
        cursor = conexion.execute(
            """
            INSERT INTO articulo
            (
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'BORRADOR')
            """,
            (
                titulo,
                contenido,
                dominio_id,
                aplicacion_id,
                experto_id,
                herramienta_id,
                fuente,
                date.today().isoformat(),
            )
        )

        return cursor.lastrowid


def validar_articulo(articulo_id, ruta=RUTA_DB):
    with conectar(ruta) as conexion:
        cursor = conexion.execute(
            """
            UPDATE articulo
            SET estado = 'VALIDADO'
            WHERE id = ?
            """,
            (articulo_id,)
        )

        if cursor.rowcount == 0:
            raise ValueError(
                "Artículo no encontrado."
            )


def listar_articulos(ruta=RUTA_DB):
    with conectar(ruta) as conexion:
        filas = conexion.execute(
            """
            SELECT
                a.id,
                a.titulo,
                a.estado,
                d.nombre AS dominio,
                e.nombre AS responsable,
                a.fecha_revision
            FROM articulo a
            JOIN dominio d
                ON d.id = a.dominio_id
            JOIN experto e
                ON e.id = a.experto_id
            ORDER BY a.id
            """
        ).fetchall()

        return [dict(fila) for fila in filas]


def main():
    inicializar_base()

    print()
    print("=" * 70)
    print("SEMANA 15 - BASE DE CONOCIMIENTO HIS_IA")
    print("=" * 70)

    print()
    print("DOMINIOS")

    for dominio in listar_dominios():
        print(
            dominio["id"],
            "-",
            dominio["nombre"]
        )

    print()
    print("ARTÍCULOS VALIDADOS - LABORATORIO")

    for articulo in buscar_articulos("Laboratorio"):
        print(
            "-",
            articulo["titulo"],
            "| Responsable:",
            articulo["responsable"]
        )

    print()
    print("TODOS LOS ARTÍCULOS")

    for articulo in listar_articulos():
        print(
            articulo["id"],
            "-",
            articulo["titulo"],
            "-",
            articulo["estado"]
        )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
