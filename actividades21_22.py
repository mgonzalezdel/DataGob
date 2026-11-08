import json
from decimal import Decimal
from datetime import date, datetime
from typing import List, Dict, Any, Optional
import pymysql
import pymysql.cursors
import redis


def conectar_mariadb() -> pymysql.Connection:
    """Establece conexión con el contenedor de MariaDB (puerto 3307)."""
    return pymysql.connect(
        host='localhost',
        port=3307,
        user='root',
        password='admin',
        database='datagob',
        cursorclass=pymysql.cursors.DictCursor
    )


def conectar_redis() -> redis.Redis:
    """Establece conexión con el contenedor de Redis Stack (puerto 6379)."""
    return redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


def serializar_adaptador(obj: Any) -> Any:
    """Convierte tipos no serializables de MariaDB (Decimal, date) a formatos estándar JSON."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Tipo {type(obj)} no es serializable en JSON")


def ejer21(conn_mariadb: pymysql.Connection, client_redis: redis.Redis) -> None:
    print("==================================================")
    print("EJERCICIO 21: Consulta SQL desde MariaDB e inserción en Redis")
    print("==================================================")
    
    sql_query: str = """
        SELECT id, id_entidad, monto_concedido, programa_presupuestario, fecha_concesion, concesion_directa
        FROM subvencion_publica
        LIMIT 10;
    """
    
    registros: List[Dict[str, Any]] = []
    
    with conn_mariadb.cursor() as cursor:
        cursor.execute(sql_query)
        registros = cursor.fetchall()
        
    print(f"-> Extraídos {len(registros)} registros desde la tabla 'subvencion_publica' en MariaDB.")
    
    contador_insertados: int = 0
    for reg in registros:
        clave_redis: str = f"mariadb:subvencion:{reg['id']}"
        
        # Adaptación de tipos de datos para la estructura JSON
        datos_limpios: Dict[str, Any] = {
            "id": reg["id"],
            "id_entidad": reg["id_entidad"],
            "monto_concedido": float(reg["monto_concedido"]) if reg["monto_concedido"] is not None else 0.0,
            "programa_presupuestario": str(reg["programa_presupuestario"]),
            "fecha_concesion": reg["fecha_concesion"].isoformat() if isinstance(reg["fecha_concesion"], (date, datetime)) else str(reg["fecha_concesion"]),
            "concesion_directa": bool(reg["concesion_directa"])
        }
        
        try:
            # Intento de almacenamiento nativo con RedisJSON
            client_redis.json().set(clave_redis, "$", datos_limpios)
            print(f"   [REDISJSON SET] Clave: '{clave_redis}' => Entidad ID: {datos_limpios['id_entidad']} | Monto: {datos_limpios['monto_concedido']} €")
        except Exception:
            # Mecanismo de reserva usando String JSON
            client_redis.set(clave_redis, json.dumps(datos_limpios, default=serializar_adaptador))
            print(f"   [STRING JSON SET] Clave: '{clave_redis}' => Entidad ID: {datos_limpios['id_entidad']} | Monto: {datos_limpios['monto_concedido']} €")
            
        contador_insertados += 1
        
    print(f"-> Migración finalizada: {contador_insertados} registros almacenados en Redis con el prefijo 'mariadb:subvencion:'.")


def ejer22(conn_mariadb: pymysql.Connection, client_redis: redis.Redis) -> None:
    print("==================================================")
    print("EJERCICIO 22: Lectura desde Redis y persistencia de vuelta a MariaDB")
    print("==================================================")
    
    patron_redis: str = "mariadb:subvencion:*"
    claves_redis: List[str] = client_redis.keys(patron_redis)
    
    print(f"-> Localizadas {len(claves_redis)} claves en Redis bajo el patrón '{patron_redis}'.")
    
    if not claves_redis:
        print("-> No hay claves en Redis para procesar en el Ejercicio 22.")
        return
        
    sql_upsert: str = """
        INSERT INTO subvencion_publica 
        (id, id_entidad, monto_concedido, programa_presupuestario, fecha_concesion, concesion_directa)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            monto_concedido = VALUES(monto_concedido),
            programa_presupuestario = VALUES(programa_presupuestario),
            fecha_concesion = VALUES(fecha_concesion),
            concesion_directa = VALUES(concesion_directa);
    """
    
    contador_persisitidos: int = 0
    
    with conn_mariadb.cursor() as cursor:
        for clave in sorted(claves_redis):
            datos_registro: Optional[Dict[str, Any]] = None
            
            try:
                datos_registro = client_redis.json().get(clave)
            except Exception:
                val_raw = client_redis.get(clave)
                if val_raw:
                    datos_registro = json.loads(val_raw)
                    
            if datos_registro:
                val_tuple = (
                    datos_registro["id"],
                    datos_registro["id_entidad"],
                    datos_registro["monto_concedido"],
                    datos_registro["programa_presupuestario"],
                    datos_registro["fecha_concesion"],
                    1 if datos_registro["concesion_directa"] else 0
                )
                cursor.execute(sql_upsert, val_tuple)
                print(f"   [MARIADB UPSERT] ID: {datos_registro['id']} | Entidad: {datos_registro['id_entidad']} | Monto: {datos_registro['monto_concedido']} €")
                contador_persisitidos += 1
                
    conn_mariadb.commit()
    print(f"-> Transacción completada en MariaDB: {contador_persisitidos} registros insertados/actualizados.")


if __name__ == "__main__":
    try:
        maria_conn = conectar_mariadb()
        redis_cli = conectar_redis()
        print("Conexiones a MariaDB (3307) y Redis (6379) establecidas correctamente.")
        
        ejer21(maria_conn, redis_cli)
        ejer22(maria_conn, redis_cli)
        
        maria_conn.close()
        print("Ejecución finalizada con éxito y conexiones cerradas.")
    except Exception as e:
        print(f"Error durante la ejecución de los ejercicios 21 y 22: {e}")