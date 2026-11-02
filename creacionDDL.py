import os
import pymysql
import psycopg2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RUTA_MYSQL = os.path.join(BASE_DIR, 'scriptMySQL.sql')
RUTA_POSTGRES = os.path.join(BASE_DIR, 'scriptPostgres.sql')

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

def ejecutar_sql_file_postgres(config, ruta_archivo): 
    """Lee un archivo SQL y ejecuta sus sentencias en PostgreSQL.""" 
    with open(ruta_archivo, 'r', encoding='utf-8') as f: 
        sql_script = f.read() 
        conn = psycopg2.connect(**config) 
        
        cursor = conn.cursor() 
        cursor.execute(sql_script) 
        
        conn.commit() 
        conn.close() 
        
if __name__ == "__main__": 
    try: 
        # 1. Ejecutar script MySQL para la BD MySQL 
        print("Ejecutando scriptMySQL.sql en MySQL...") 
        ejecutar_sql_file_mysql(MYSQL_CONFIG, RUTA_MYSQL) 
        # 2. Reutilizar scriptMySQL.sql para MariaDB (misma sintaxis DDL) 
        print("Ejecutando scriptMySQL.sql en MariaDB...") 
        ejecutar_sql_file_mysql(MARIADB_CONFIG, RUTA_MYSQL) 
        # 3. Ejecutar scriptPostgres.sql para PostgreSQL 
        print("Ejecutando scriptPostgres.sql en PostgreSQL...") 
        ejecutar_sql_file_postgres(POSTGRES_CONFIG, RUTA_POSTGRES) 
        
        print("-&gt; Estructura de las 10 tablas creada correctamente en las 3 bases de datos.")

    except Exception as e: print(f"Error al ejecutar los scripts de creación: {e}")