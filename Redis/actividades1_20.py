import json
from typing import List, Dict, Any, Optional
import redis
from redis.commands.search.field import TextField, TagField, NumericField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from redis.commands.search.aggregation import AggregateRequest 
from redis.commands.search import reducers

def obtener_conexion_redis(host: str = 'localhost', port: int = 6379, db: int = 0) -> redis.Redis:
    """
    Establece la conexión con el servidor Redis Stack en el puerto 6379.
    Configura decode_responses=True para recibir cadenas UTF-8 nativas.
    """
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)

def ejer01(client: redis.Redis) -> None:
    
    print("==================================================")
    print("EJERCICIO 01: Crear registros clave-valor")
    print("==================================================")
    registros: Dict[str, str] = {
        "partido:1": "Partido Transparencia Democrática | CIF: P0000001A | Tipo: Nacional",
        "partido:2": "Coalición de Alianza Ciudadana | CIF: P0000002B | Tipo: Autonómico",
        "partido:3": "Unión Progresista del Sur | CIF: P0000003C | Tipo: Local",
        "cargo:101": "Cargo Público: Carlos Mendoza | Puesto: Diputado General | DNI_HASH: a7f8b9",
        "cargo:102": "Cargo Público: Ana Belén Gómez | Puesto: Secretaria de Estado | DNI_HASH: c1d2e3",
        "cargo:103": "Cargo Público: Roberto Silva | Puesto: Alcalde General | DNI_HASH: e5f6a7",
        "entidad:201": "Entidad Privada: Construcciones Ibéricas S.A. | CIF: B88223311",
        "entidad:202": "Entidad Privada: Tecnología y Consultoría DataGov S.L. | CIF: B99445566",
        "subvencion:301": "Subvención: Fomento Digital 2024 | Monto: 450000.00 EUR | Entidad: 202",
        "sancion:401": "Sanción: Infracción Ley Contratos | Veto: 36 meses | Entidad: 201"
    }
    client.mset(registros)
    print(f"-> Inserción exitosa. Registros almacenados: {len(registros)}")
    for k, v in registros.items():
        print(f" [SET] Clave: '{k}' => Valor: '{v}'")

def ejer02(client: redis.Redis) -> None:
    
    print("==================================================")
    print("EJERCICIO 02: Obtener número total de claves")
    print("==================================================")
    total_claves: int = client.dbsize()
    print(f"-> Número total de claves en la base de datos: {total_claves}")

def ejer03(client: redis.Redis) -> None:
    
    print("==================================================")
    print("EJERCICIO 03: Obtener registro por clave")
    print("==================================================")
    clave_busqueda: str = "cargo:101"
    valor: Optional[str] = client.get(clave_busqueda)
    if valor:
        print(f"-> Registro obtenido para la clave '{clave_busqueda}':")
        print(f"   Contenido: '{valor}'")
    else:
        print(f"-> No se encontró ningún registro para '{clave_busqueda}'.")

def ejer04(client: redis.Redis) -> None:
    
    print("==================================================")
    print("EJERCICIO 04: Actualizar valor de clave y verificar")
    print("==================================================")
    clave_actualizar: str = "subvencion:301"
    valor_anterior: Optional[str] = client.get(clave_actualizar)
    nuevo_valor: str = "Subvención: Fomento Digital 2024 (AMPLIADA) | Monto: 600000.00 EUR | Entidad: 202"
    client.set(clave_actualizar, nuevo_valor)
    valor_actualizado: Optional[str] = client.get(clave_actualizar)
    print(f"-> Clave modificada: '{clave_actualizar}'")
    print(f"   Valor anterior : '{valor_anterior}'")
    print(f"   Valor nuevo    : '{valor_actualizado}'")

def ejer05(client: redis.Redis) -> None:
    
    print("==================================================")
    print("EJERCICIO 05: Eliminar clave y retornar contenido")
    print("==================================================")
    clave_eliminar: str = "sancion:401"
    valor_eliminado: Optional[str] = client.get(clave_eliminar)
    if valor_eliminado:
        eliminados: int = client.delete(clave_eliminar)
        print(f"-> Eliminación realizada. Claves removidas: {eliminados}")
        print(f"   Clave eliminada: '{clave_eliminar}'")
        print(f"   Valor eliminado: '{valor_eliminado}'")
    else:
        print(f"-> La clave '{clave_eliminar}' no existe.")

def ejer06(client: redis.Redis) -> None:
    
    print("==================================================")
    print("EJERCICIO 06: Obtener todas las claves guardadas")
    print("==================================================")
    claves: List[str] = client.keys('*')
    print(f"-> Total de claves encontradas ({len(claves)}):")
    for idx, c in enumerate(sorted(claves), 1):
        print(f"   {idx}. {c}")

def ejer07(client: redis.Redis) -> None:
    
    print("==================================================")
    print("EJERCICIO 07: Obtener todos los valores guardados")
    print("==================================================")
    claves: List[str] = client.keys('*')
    if claves:
        valores: List[Optional[str]] = client.mget(sorted(claves))
        print(f"-> Listado de los {len(valores)} valores almacenados:")
        for k, v in zip(sorted(claves), valores):
            print(f"   [KEY] {k} => [VALUE] {v}")
    else:
        print("-> La base de datos está vacía.")

def ejer08(client: redis.Redis) -> None:
    
    print("==================================================")
    print("EJERCICIO 08: Búsqueda con comodín '*' (partido:*)")
    print("==================================================")
    patron: str = "partido:*"
    coincidencias: List[str] = client.keys(patron)
    print(f"-> Patrón de búsqueda: '{patron}'. Coincidencias ({len(coincidencias)}):")
    for k in sorted(coincidencias):
        val = client.get(k)
        print(f"   [MATCH *] {k} => {val}")

def ejer09(client: redis.Redis) -> None:
    
    print("==================================================")
    print("EJERCICIO 09: Búsqueda con conjunto '[]' (cargo:10[12])")
    print("==================================================")
    patron: str = "cargo:10[12]"
    coincidencias: List[str] = client.keys(patron)
    print(f"-> Patrón de búsqueda: '{patron}'. Coincidencias ({len(coincidencias)}):")
    for k in sorted(coincidencias):
        val = client.get(k)
        print(f"   [MATCH []] {k} => {val}")

def ejer10(client: redis.Redis) -> None:

    print("==================================================")
    print("EJERCICIO 10: Búsqueda con comodín único '?' (entidad:20?)")
    print("==================================================")
    patron: str = "entidad:20?"
    coincidencias: List[str] = client.keys(patron)
    print(f"-> Patrón de búsqueda: '{patron}'. Coincidencias ({len(coincidencias)}):")
    for k in sorted(coincidencias):
        val = client.get(k)
        print(f"   [MATCH ?] {k} => {val}")

# Para ejercicios 11 al 13
def sembrar_subvenciones_base(client: redis.Redis) -> None:
    """Garantiza la existencia de datos iniciales para los ejercicios 11 a 13."""
    subvenciones: Dict[str, str] = {
        "subvencion:101": json.dumps({"entidad": "TechGov S.L.", "monto": 45000.0, "programa": "Digitalización"}),
        "subvencion:102": json.dumps({"entidad": "Construcciones Civiles S.A.", "monto": 120000.0, "programa": "Infraestructura"}),
        "subvencion:103": json.dumps({"entidad": "Consultoría Social", "monto": 15000.0, "programa": "Empleo"}),
        "subvencion:104": json.dumps({"entidad": "Innovación Pública", "monto": 85000.0, "programa": "I+D+i"}),
    }
    for k, v in subvenciones.items():
        client.set(k, v)

def ejer11(client: redis.Redis) -> None:
    print("==================================================")
    print("EJERCICIO 11: Obtener y filtrar registros por valor (monto > 50000)")
    print("==================================================")
    for key in client.keys("subvencion:*"):
        client.delete(key)
    sembrar_subvenciones_base(client)
    patron: str = "subvencion:*"
    claves: List[str] = client.keys(patron)
    print(f"-> Analizando {len(claves)} claves bajo el patrón '{patron}' (Filtro: monto > 50000):")
    for k in sorted(claves):
        raw_val: Optional[str] = client.get(k)
        if raw_val:
            try:
                data: Dict[str, Any] = json.loads(raw_val)
                if data.get("monto", 0) > 50000:
                    print(f"   [FILTRO CUMPLIDO] {k} => Entidad: {data['entidad']} | Monto: {data['monto']} €")
            except json.JSONDecodeError: print(f" [AVISO] Se omitió la clave corrupta: '{k}'")


def ejer12(client: redis.Redis) -> None:
    print("==================================================")
    print("EJERCICIO 12: Actualizar registros por filtro (+10000 al monto si < 50000)")
    print("==================================================")
    claves: List[str] = client.keys("subvencion:*")
    print("-> Actualizando subvenciones con monto menor a 50,000 € (+10,000 € de incremento):")
    for k in sorted(claves):
        raw_val: Optional[str] = client.get(k)
        if raw_val:
            data: Dict[str, Any] = json.loads(raw_val)
            monto_actual: float = float(data.get("monto", 0))
            if monto_actual < 50000:
                nuevo_monto: float = monto_actual + 10000.0
                data["monto"] = nuevo_monto
                client.set(k, json.dumps(data))
                print(f"   [ACTUALIZADO] {k} => {data['entidad']}: {monto_actual} € -> {nuevo_monto} €")

def ejer13(client: redis.Redis) -> None:
    print("==================================================")
    print("EJERCICIO 13: Eliminar registros en base a un filtro (monto < 30000)")
    print("==================================================")
    claves: List[str] = client.keys("subvencion:*")
    print("-> Buscando registros a eliminar (Filtro: monto < 30000 €):")
    for k in sorted(claves):
        raw_val: Optional[str] = client.get(k)
        if raw_val:
            data: Dict[str, Any] = json.loads(raw_val)
            if float(data.get("monto", 0)) < 30000:
                client.delete(k)
                print(f"   [ELIMINADO] Clave: {k} | Contenido: {data}")


def ejer14(client: redis.Redis) -> None:
    print("==================================================")
    print("EJERCICIO 14: Crear estructura JSON de array de datos")
    print("==================================================")
    cargos_array: List[Dict[str, Any]] = [
        {"id": 1, "nombre": "Laura Gómez", "puesto": "Ministra Sanidad", "nivel": "Nacional", "patrimonio": 350000.0},
        {"id": 2, "nombre": "Carlos Ruiz", "puesto": "Concejal Urbanismo", "nivel": "Local", "patrimonio": 120000.0},
        {"id": 3, "nombre": "Elena Torres", "puesto": "Consejera Hacienda", "nivel": "Autonómico", "patrimonio": 450000.0},
        {"id": 4, "nombre": "Miguel Ángel Mateo", "puesto": "Secretario Estado", "nivel": "Nacional", "patrimonio": 280000.0}
    ]
    clave_json: str = "datagob:cargos_array"
    try:
        client.json().set(clave_json, "$", cargos_array)
        print(f"-> Estructura JSON Array almacenada mediante RedisJSON en la clave '{clave_json}'.")
    except Exception:
        client.set(clave_json, json.dumps(cargos_array))
        print(f"-> Estructura JSON Array almacenada como String JSON en la clave '{clave_json}'.")
    print(f"-> Registros incluidos en la estructura: {len(cargos_array)}.")

def ejer15(client: redis.Redis) -> None:
    print("==================================================")
    print("EJERCICIO 15: Filtrar por cada atributo de la estructura JSON")
    print("==================================================")
    clave_json: str = "datagob:cargos_array"
    raw_data: Optional[Any] = None
    try:
        raw_data = client.json().get(clave_json)
    except Exception:
        raw_val = client.get(clave_json)
        if raw_val:
            raw_data = json.loads(raw_val)

    if not raw_data:
        print("-> No se encontraron datos JSON para filtrar.")
        return

    print("-> 1. Filtro Atributo 'nivel' == 'Nacional':")
    for elem in raw_data:
        if elem.get("nivel") == "Nacional":
            print(f"   [MATCH nivel] {elem['nombre']} ({elem['puesto']})")

    print("-> 2. Filtro Atributo 'patrimonio' > 300000:")
    for elem in raw_data:
        if float(elem.get("patrimonio", 0)) > 300000:
            print(f"   [MATCH patrimonio] {elem['nombre']} - {elem['patrimonio']} €")

    print("-> 3. Filtro Atributo 'id' == 2:")
    for elem in raw_data:
        if elem.get("id") == 2:
            print(f"   [MATCH id] {elem['nombre']} - ID: {elem['id']}")


def ejer16(client: redis.Redis) -> None:
    print("==================================================")
    print("EJERCICIO 16: Crear una lista en Redis (expedientes_lobby)")
    print("==================================================")
    clave_lista: str = "lista:expedientes_lobby"
    client.delete(clave_lista)
    expedientes: List[str] = [
        "EXP-2024-001:Sanidad:Aprobado",
        "EXP-2024-002:Urbanismo:Pendiente",
        "EXP-2024-003:Sanidad:Revisión",
        "EXP-2024-004:Hacienda:Aprobado",
        "EXP-2024-005:Sanidad:Rechazado"
    ]
    client.rpush(clave_lista, *expedientes)
    total: int = client.llen(clave_lista)
    print(f"-> Lista '{clave_lista}' creada correctamente con {total} elementos.")


def ejer17(client: redis.Redis) -> None:
    print("==================================================")
    print("EJERCICIO 17: Obtener elementos de una lista con filtro ('Sanidad')")
    print("==================================================")
    clave_lista: str = "lista:expedientes_lobby"
    elementos: List[str] = client.lrange(clave_lista, 0, -1)
    filtro: str = "Sanidad"
    print(f"-> Filtrando elementos de la lista '{clave_lista}' que contienen '{filtro}':")
    for elem in elementos:
        if filtro in elem:
            print(f"   [MATCH LISTA] {elem}")

def ejer18(client: redis.Redis) -> None:
    print("==================================================")
    print("EJERCICIO 18: Crear datos con índices (Esquema: nombre, nivel, patrimonio)")
    print("==================================================")
    registros: List[Dict[str, Any]] = [
        {"id": "cargo_idx:1", "nombre": "Laura Gómez", "nivel": "Nacional", "patrimonio": 350000.0},
        {"id": "cargo_idx:2", "nombre": "Carlos Ruiz", "nivel": "Local", "patrimonio": 120000.0},
        {"id": "cargo_idx:3", "nombre": "Elena Torres", "nivel": "Autonómico", "patrimonio": 450000.0},
        {"id": "cargo_idx:4", "nombre": "Miguel Ángel Mateo", "nivel": "Nacional", "patrimonio": 280000.0}
    ]
    for r in registros:
        client.hset(r["id"], mapping={"nombre": r["nombre"], "nivel": r["nivel"], "patrimonio": str(r["patrimonio"])})

    nombre_indice: str = "idx:cargo_politico"
    try:
        try:
            client.ft(nombre_indice).dropindex(delete_documents=False)
        except Exception:
            pass

        schema = (
            TextField("nombre"),
            TagField("nivel"),
            NumericField("patrimonio")
        )
        definition = IndexDefinition(prefix=["cargo_idx:"], index_type=IndexType.HASH)
        client.ft(nombre_indice).create_index(schema, definition=definition)
        print(f"-> Índice RediSearch '{nombre_indice}' creado sobre el prefijo 'cargo_idx:' con 3 campos.")
    except Exception as e:
        print(f"-> Registros de prueba almacenados correctamente ({e}).")


def ejer19(client: redis.Redis) -> None:
    print("==================================================")
    print("EJERCICIO 19: Búsqueda con índices por campo (@nivel:{Nacional})")
    print("==================================================")
    nombre_indice: str = "idx:cargo_politico"
    try:
        query = Query("@nivel:{Nacional}")
        res = client.ft(nombre_indice).search(query)
        print(f"-> Resultados devueltos por RediSearch ({res.total}):")
        for doc in res.docs:
            print(f"   [SEARCH MATCH] ID: {doc.id} | Nombre: {doc.nombre} | Nivel: {doc.nivel} | Patrimonio: {doc.patrimonio} €")
    except Exception:
        print("-> Búsqueda de reserva sobre Hashes:")
        for k in sorted(client.keys("cargo_idx:*")):
            h = client.hgetall(k)
            if h.get("nivel") == "Nacional":
                print(f"   [MATCH] Clave: {k} | Nombre: {h.get('nombre')} | Nivel: {h.get('nivel')}")


def ejer20(client: redis.Redis) -> None:
    print("==================================================")
    print("EJERCICIO 20: Realizar un GROUP BY usando los índices (@nivel)")
    print("==================================================")
    nombre_indice: str = "idx:cargo_politico"
    try:
        req = AggregateRequest("*").group_by("@nivel", reducers.count().as_name("total_cargos"))
        res = client.ft(nombre_indice).aggregate(req)
        print("-> Agregación GROUP BY @nivel mediante RediSearch:")
        for row in res.rows:
            print(f"   [GROUP BY] Nivel: {row[1]} => Total de cargos: {row[3]}")
    except Exception:
        print("-> Agregación de reserva por Python:")
        conteo: Dict[str, int] = {}
        for k in client.keys("cargo_idx:*"):
            h = client.hgetall(k)
            nivel = h.get("nivel", "Desconocido")
            conteo[nivel] = conteo.get(nivel, 0) + 1
        for nivel, total in conteo.items():
            print(f"   [GROUP BY] Nivel: {nivel} => Total de cargos: {total}")

def main() -> None:
    """
    Punto de entrada principal. Ejecuta la secuencia completa de los ejercicios 1 al 10.
    """
    try:
        r = obtener_conexion_redis()
        r.flushdb()
        print("-> Espacio de claves de Redis inicializado y limpio.")

        ejer01(r)
        ejer02(r)
        ejer03(r)
        ejer04(r)
        ejer05(r)
        ejer06(r)
        ejer07(r)
        ejer08(r)
        ejer09(r)
        ejer10(r)
        ejer11(r) 
        ejer12(r) 
        ejer13(r) 
        ejer14(r) 
        ejer15(r) 
        ejer16(r) 
        ejer17(r) 
        ejer18(r) 
        ejer19(r) 
        ejer20(r)

        print("==================================================")
        print("EJECUCIÓN FINALIZADA CORRECTAMENTE (EJERCICIOS 1-20)")
        print("==================================================")

    except redis.ConnectionError:
        print("Error: No se pudo conectar al servidor de Redis en localhost:6379.")
    except Exception as ex:
        print(f"Ocurrió un error inesperado durante la ejecución: {ex}")

if __name__ == '__main__':
    main()
