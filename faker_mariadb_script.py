# ==============================================================================
# SCRIPT DE POBLACIÓN DE DATOS SINTÉTICOS PARA MARIADB - PROYECTO DATAGOB
# ==============================================================================
# 10 PROVIDERS DE FAKER UTILIZADOS (DECLARACIÓN REQUERIDA EN LA PRÁCTICA):
# 1. fake.name()               -> Provider: faker.providers.person
# 2. fake.company()            -> Provider: faker.providers.company
# 3. fake.job()                -> Provider: faker.providers.job
# 4. fake.date_between()       -> Provider: faker.providers.date_time
# 5. fake.sha256()             -> Provider: faker.providers.misc
# 6. fake.pydecimal()          -> Provider: faker.providers.python
# 7. fake.boolean()            -> Provider: faker.providers.python
# 8. fake.text()               -> Provider: faker.providers.lorem
# 9. fake.bothify()            -> Provider: faker.providers.base
# 10. fake.random_element()    -> Provider: faker.providers.base
# ==============================================================================

import pymysql
from faker import Faker
import sys

# Inicialización de Faker configurado para localización en español (España)
fake = Faker('es_ES')

# Configuración de conexión exclusiva a la instancia de MariaDB (Puerto 3307)
MARIADB_CONFIG = {
    'host': 'localhost',
    'port': 3307,
    'user': 'root',
    'password': 'admin',
    'database': 'datagob',
    'charset': 'utf8mb4',
    'autocommit': False
}

def poblar_mariadb():
    print("Iniciando conexión con la base de datos MariaDB (datagob)...")
    try:
        conn = pymysql.connect(**MARIADB_CONFIG)
        cursor = conn.cursor()
        print("Conexión establecida exitosamente.")

        # Desactivar temporalmente restricciones de clave foránea para reseteo ordenado
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        tablas = [
            "reuniones_lobby", "agente_lobby", "donaciones", "subvencion_publica",
            "sancion_inhabilitante", "historial_empleo_privado", "declaracion_bienes",
            "cargo_politico", "entidad_privada", "partido_politico"
        ]
        for tabla in tablas:
            cursor.execute(f"TRUNCATE TABLE {tabla};")
        
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        print("Tablas limpiadas. Generando e insertando datos sintéticos...")

        # ----------------------------------------------------------------------
        # 1. Tabla: partido_politico (5 registros)
        # ----------------------------------------------------------------------
        sql_partido = "INSERT INTO partido_politico (id, nombre, cif, tipo_entidad) VALUES (%s, %s, %s, %s)"
        for i in range(1, 6):
            cursor.execute(sql_partido, (
                i,
                f"Partido {fake.company()}",
                fake.bothify(text='G########'),  # CIF de entidades sin ánimo de lucro / partidos
                fake.random_element(elements=('Partido Político', 'Coalición Electoral', 'Federación'))
            ))
        print("  [✓] Tabla partido_politico poblada (5 registros).")

        # ----------------------------------------------------------------------
        # 2. Tabla: entidad_privada (15 registros)
        # ----------------------------------------------------------------------
        sql_entidad = "INSERT INTO entidad_privada (id, cif, razon_social, sector_actividad) VALUES (%s, %s, %s, %s)"
        for i in range(1, 16):
            cursor.execute(sql_entidad, (
                i,
                fake.bothify(text='A########'),  # CIF Sociedad Anónima
                fake.company(),
                fake.job()
            ))
        print("  [✓] Tabla entidad_privada poblada (15 registros).")

        # ----------------------------------------------------------------------
        # 3. Tabla: cargo_politico (20 registros -> FK id_partido)
        # ----------------------------------------------------------------------
        sql_cargo = """
        INSERT INTO cargo_politico 
        (id, id_partido, nombre_completo, dni_hash, puesto, fecha_toma, fecha_cese, nivel_gobierno) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        for i in range(1, 21):
            fecha_toma = fake.date_between(start_date='-6y', end_date='-2y')
            fecha_cese = fake.date_between(start_date='-2y', end_date='today')
            cursor.execute(sql_cargo, (
                i,
                fake.random_int(min=1, max=5),
                fake.name(),
                fake.sha256(),
                fake.job(),
                fecha_toma,
                fecha_cese,
                fake.random_element(elements=('Estatal', 'Autonómico', 'Municipal'))
            ))
        print("  [✓] Tabla cargo_politico poblada (20 registros).")

        # ----------------------------------------------------------------------
        # 4. Tabla: declaracion_bienes (20 registros -> FK id_cargo)
        # ----------------------------------------------------------------------
        sql_bienes = """
        INSERT INTO declaracion_bienes 
        (id, id_cargo, fecha, ejercicio_fiscal, patrimonio_bruto, deudas_totales, participaciones_emp_valor) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        for i in range(1, 21):
            cursor.execute(sql_bienes, (
                i,
                i,  # Relación 1:1 conceptual para este lote
                fake.date_between(start_date='-2y', end_date='today'),
                2023,
                fake.pydecimal(left_digits=6, right_digits=2, positive=True),
                fake.pydecimal(left_digits=5, right_digits=2, positive=True),
                fake.pydecimal(left_digits=5, right_digits=2, positive=True)
            ))
        print("  [✓] Tabla declaracion_bienes poblada (20 registros).")

        # ----------------------------------------------------------------------
        # 5. Tabla: historial_empleo_privado (25 registros -> FK id_cargo, FK id_entidad)
        # ----------------------------------------------------------------------
        sql_empleo = """
        INSERT INTO historial_empleo_privado 
        (id, id_cargo, id_entidad, puesto, fecha_inicio, fecha_fin) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        for i in range(1, 26):
            f_ini = fake.date_between(start_date='-12y', end_date='-6y')
            f_fin = fake.date_between(start_date='-6y', end_date='-3y')
            cursor.execute(sql_empleo, (
                i,
                fake.random_int(min=1, max=20),
                fake.random_int(min=1, max=15),
                fake.job(),
                f_ini,
                f_fin
            ))
        print("  [✓] Tabla historial_empleo_privado poblada (25 registros).")

        # ----------------------------------------------------------------------
        # 6. Tabla: sancion_inhabilitante (10 registros -> FK id_entidad)
        # ----------------------------------------------------------------------
        sql_sancion = """
        INSERT INTO sancion_inhabilitante 
        (id, id_entidad, tipo_infraccion, fecha_inicio_sancion, duracion_veto) 
        VALUES (%s, %s, %s, %s, %s)
        """
        for i in range(1, 11):
            cursor.execute(sql_sancion, (
                i,
                fake.random_int(min=1, max=15),
                fake.text(max_nb_chars=80),
                fake.date_between(start_date='-4y', end_date='today'),
                fake.random_int(min=6, max=48)  # Meses de veto
            ))
        print("  [✓] Tabla sancion_inhabilitante poblada (10 registros).")

        # ----------------------------------------------------------------------
        # 7. Tabla: subvencion_publica (20 registros -> FK id_entidad)
        # ----------------------------------------------------------------------
        sql_subvencion = """
        INSERT INTO subvencion_publica 
        (id, id_entidad, monto_concedido, programa_presupuestario, fecha_concesion, concesion_directa) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        for i in range(1, 21):
            cursor.execute(sql_subvencion, (
                i,
                fake.random_int(min=1, max=15),
                fake.pydecimal(left_digits=6, right_digits=2, positive=True),
                fake.bothify(text='PRG-2024-###'),
                fake.date_between(start_date='-2y', end_date='today'),
                fake.boolean()
            ))
        print("  [✓] Tabla subvencion_publica poblada (20 registros).")

        # ----------------------------------------------------------------------
        # 8. Tabla: donaciones (15 registros -> FK id_partido, FK id_entidad)
        # ----------------------------------------------------------------------
        sql_donacion = """
        INSERT INTO donaciones 
        (id, id_partido, id_entidad, fecha, tipo_donacion, monto) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        for i in range(1, 16):
            cursor.execute(sql_donacion, (
                i,
                fake.random_int(min=1, max=5),
                fake.random_int(min=1, max=15),
                fake.date_between(start_date='-3y', end_date='today'),
                fake.random_element(elements=('Dineraria', 'Especie', 'Cesión de bienes')),
                fake.pydecimal(left_digits=5, right_digits=2, positive=True)
            ))
        print("  [✓] Tabla donaciones poblada (15 registros).")

        # ----------------------------------------------------------------------
        # 9. Tabla: agente_lobby (12 registros -> FK id_entidad)
        # ----------------------------------------------------------------------
        sql_lobby = """
        INSERT INTO agente_lobby 
        (id, id_entidad, nombre_representante, num_reg_lobby) 
        VALUES (%s, %s, %s, %s)
        """
        for i in range(1, 13):
            cursor.execute(sql_lobby, (
                i,
                fake.random_int(min=1, max=15),
                fake.name(),
                fake.bothify(text='REG-LOBBY-#####')
            ))
        print("  [✓] Tabla agente_lobby poblada (12 registros).")

        # ----------------------------------------------------------------------
        # 10. Tabla: reuniones_lobby (30 registros -> FK id_cargo, FK id_lobbyista)
        # ----------------------------------------------------------------------
        sql_reunion = """
        INSERT INTO reuniones_lobby 
        (id, id_cargo, id_lobbyista, fecha, materia_tratada, exp_normativo_rel) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        for i in range(1, 31):
            cursor.execute(sql_reunion, (
                i,
                fake.random_int(min=1, max=20),
                fake.random_int(min=1, max=12),
                fake.date_between(start_date='-1y', end_date='today'),
                fake.text(max_nb_chars=120),
                fake.bothify(text='LEY-2024-###')
            ))
        print("  [✓] Tabla reuniones_lobby poblada (30 registros).")

        # Confirmación de la transacción en MariaDB
        conn.commit()
        print("\n[ÉXITO] Inserción de datos sintéticos en MariaDB completada correctamente.")

    except Exception as e:
        if 'conn' in locals() and conn.open:
            conn.rollback()
        print(f"\n[ERROR] Ocurrió un fallo durante la carga en MariaDB: {e}", file=sys.stderr)
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()
            print("Conexión con MariaDB cerrada.")

if __name__ == '__main__':
    poblar_mariadb()