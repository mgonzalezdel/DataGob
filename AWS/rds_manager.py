import json
import pymysql
from config_aws import RDS_CONFIG


def _conectar(usar_db=True):
    """Abre conexión PyMySQL devolviendo filas como diccionarios."""
    params = {
        "host": RDS_CONFIG["host"],
        "port": RDS_CONFIG["port"],
        "user": RDS_CONFIG["user"],
        "password": RDS_CONFIG["password"],
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": True,
    }
    if usar_db:
        params["database"] = RDS_CONFIG["database"]
    return pymysql.connect(**params)


def crear_bd_y_tablas_rds():
    """Crea la BBDD en RDS, las tablas relacionales e inserta datos iniciales."""
    # Conexión inicial sin BBDD seleccionada para crearla si no existe
    conn = _conectar(usar_db=False)
    with conn.cursor() as cur:
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS {RDS_CONFIG['database']} "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        )
        cur.execute(f"USE {RDS_CONFIG['database']};")

        # Tabla 1: Organismos públicos (clave primaria compartida con DynamoDB: organismo_id)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS organismos_publicos (
                organismo_id VARCHAR(20) PRIMARY KEY,
                nombre VARCHAR(150) NOT NULL,
                ambito ENUM('Estatal', 'Autonomico', 'Local') NOT NULL,
                comunidad VARCHAR(80) NOT NULL,
                empleados INT NOT NULL
            );
        """)

        # Tabla 2: Publicaciones de datos abiertos vinculadas por clave foránea
        cur.execute("""
            CREATE TABLE IF NOT EXISTS publicaciones_datasets (
                pub_id INT PRIMARY KEY,
                organismo_id VARCHAR(20) NOT NULL,
                categoria VARCHAR(50) NOT NULL,
                titulo VARCHAR(200) NOT NULL,
                descargas_totales INT NOT NULL,
                fecha_alta DATE NOT NULL,
                FOREIGN KEY (organismo_id) REFERENCES organismos_publicos(organismo_id)
            );
        """)

        # Inserción idempotente (ON DUPLICATE KEY UPDATE) para permitir re-ejecuciones limpias
        organismos_sql = """
            INSERT INTO organismos_publicos (organismo_id, nombre, ambito, comunidad, empleados)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), empleados=VALUES(empleados);
        """
        cur.executemany(organismos_sql, [
            ("ORG-01", "Ministerio de Hacienda", "Estatal", "Madrid", 12500),
            ("ORG-02", "Ministerio de Ciencia", "Estatal", "Madrid", 4800),
            ("ORG-03", "Junta de Andalucia", "Autonomico", "Andalucia", 9200),
        ])

        publicaciones_sql = """
            INSERT INTO publicaciones_datasets (pub_id, organismo_id, categoria, titulo, descargas_totales, fecha_alta)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE descargas_totales=VALUES(descargas_totales);
        """
        cur.executemany(publicaciones_sql, [
            (1, "ORG-01", "Economia", "Ejecucion Presupuestaria Mensual", 4200, "2026-02-10"),
            (2, "ORG-01", "Economia", "Recaudacion Tributaria Provincial", 3150, "2026-04-05"),
            (3, "ORG-02", "Tecnologia", "Proyectos I+D Financiados", 2890, "2026-03-18"),
            (4, "ORG-03", "MedioAmbiente", "Embalses y Recursos Hidricos", 5100, "2026-05-02"),
        ])

    conn.close()
    return f"Base de datos '{RDS_CONFIG['database']}' y tablas creadas con registros iniciales"


def ejecutar_consultas_rds_json():
    """Ejecuta 3 consultas SQL y devuelve los resultados estructurados en formato JSON."""
    conn = _conectar(usar_db=True)
    with conn.cursor() as cur:
        # Consulta 1: JOIN entre organismos y publicaciones con filtro de descargas
        cur.execute("""
            SELECT o.organismo_id, o.nombre, o.ambito, p.categoria, p.titulo, p.descargas_totales
            FROM organismos_publicos o
            INNER JOIN publicaciones_datasets p ON o.organismo_id = p.organismo_id
            WHERE p.descargas_totales > 3000
            ORDER BY p.descargas_totales DESC;
        """)
        consulta_1 = cur.fetchall()

        # Consulta 2: Agregación (GROUP BY) del total de descargas y datasets por ámbito
        cur.execute("""
            SELECT o.ambito,
                   COUNT(p.pub_id) AS total_publicaciones,
                   SUM(p.descargas_totales) AS suma_descargas
            FROM organismos_publicos o
            LEFT JOIN publicaciones_datasets p ON o.organismo_id = p.organismo_id
            GROUP BY o.ambito;
        """)
        consulta_2 = cur.fetchall()

        # Consulta 3: Organismos estatales con más de 4000 empleados y sus categorías activas
        cur.execute("""
            SELECT o.organismo_id, o.nombre, o.empleados, p.categoria, p.fecha_alta
            FROM organismos_publicos o
            INNER JOIN publicaciones_datasets p ON o.organismo_id = p.organismo_id
            WHERE o.ambito = 'Estatal' AND o.empleados > 4000;
        """)
        consulta_3 = cur.fetchall()

    conn.close()

    resultado = {
        "consulta_1_join_top_descargas": consulta_1,
        "consulta_2_agregacion_por_ambito": consulta_2,
        "consulta_3_organismos_estatales_filtrados": consulta_3,
    }
    return json.dumps(resultado, indent=2, default=str, ensure_ascii=False)