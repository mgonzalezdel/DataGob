import pymysql 
import psycopg2 

# Configuración de conexiones a los tres motores de base de datos 
MYSQL_CONFIG = {
    'host': 'localhost', 
    'port': 3306, 
    'user': 'root', 
    'password': 'admin', 
    'database': 'datagob' 
}

MARIADB_CONFIG = { 
    'host': 'localhost', 
    'port': 3307, 
    'user': 'root', 
    'password': 'admin', 
    'database': 'datagob' 
}

POSTGRES_CONFIG = {
    'host': 'localhost', 
    'port': 5432, 
    'user': 'postgres', 
    'password': 'admin', 
    'dbname': 'datagob' 
}

def ejecutar_sql_file_mysql(config, ruta_archivo): 
    """Lee un archivo SQL y ejecuta sus sentencias en MySQL / MariaDB.""" 
    with open(ruta_archivo, 'r', encoding='utf-8') as f: 
        sql_script = f.read()

    conn = pymysql.connect(**config) 
    cursor = conn.cursor()

    # Se dividen las instrucciones por punto y coma ';' 
    sentencias = sql_script.split(';') 
    for sentencia in sentencias: 
        sql_limpio = sentencia.strip() 
        if sql_limpio: 
            cursor.execute(sql_limpio)

    conn.commit()
    conn.close()

def ejecutar\_sql\_file\_postgres(config, ruta\_archivo): """Lee un archivo SQL y ejecuta sus sentencias en PostgreSQL.""" with open(ruta\_archivo, 'r', encoding='utf-8') as f: sql\_script = f.read() conn = psycopg2.connect(\*\*config) cursor = conn.cursor() cursor.execute(sql\_script) conn.commit() conn.close() if \_\_name\_\_ == "\_\_main\_\_": try: # 1\. Ejecutar script MySQL para la BD MySQL print("Ejecutando scriptMySQL.sql en MySQL...") ejecutar\_sql\_file\_mysql(MYSQL\_CONFIG, 'scriptMySQL.sql') # 2\. Reutilizar scriptMySQL.sql para MariaDB (misma sintaxis DDL) print("Ejecutando scriptMySQL.sql en MariaDB...") ejecutar\_sql\_file\_mysql(MARIADB\_CONFIG, 'scriptMySQL.sql') # 3\. Ejecutar scriptPostgres.sql para PostgreSQL print("Ejecutando scriptPostgres.sql en PostgreSQL...") ejecutar\_sql\_file\_postgres(POSTGRES\_CONFIG, 'scriptPostgres.sql') print("-&gt; Estructura de las 10 tablas creada correctamente en las 3 bases de datos.") 
    except Exception as e: print(f"Error al ejecutar los scripts de creación: {e}")