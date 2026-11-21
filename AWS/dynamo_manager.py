import json
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Attr
from boto3.dynamodb.types import TypeDeserializer
from botocore.exceptions import ClientError
from config_aws import AWS_REGION

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
client = boto3.client("dynamodb", region_name=AWS_REGION)
deserializer = TypeDeserializer()


def _json_serial(obj):
    """Convierte objetos Decimal de DynamoDB a float/int para serializar a JSON."""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return str(obj)


def _deserializar_partiql(items_raw):
    """Transforma la respuesta tipada de PartiQL ({'S': 'valor'}) a dict estándar."""
    return [{k: deserializer.deserialize(v) for k, v in item.items()} for item in items_raw]


def crear_tablas_dynamodb():
    """Crea 3 tablas: sin índices, con LSI y con GSI, esperando a que estén activas."""
    existentes = client.list_tables()["TableNames"]
    creadas = []

    # 1. Tabla SIN índice local ni global (Clave primaria simple)
    if "DataGob_Organismos" not in existentes:
        t1 = dynamodb.create_table(
            TableName="DataGob_Organismos",
            KeySchema=[{"AttributeName": "organismo_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "organismo_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        t1.wait_until_exists()
        creadas.append("DataGob_Organismos (Sin índices)")

    # 2. Tabla CON Índice Local Secundario (LSI)
    # El LSI exige clave primaria compuesta (HASH + RANGE) y comparte la misma Partition Key
    if "DataGob_Datasets" not in existentes:
        t2 = dynamodb.create_table(
            TableName="DataGob_Datasets",
            KeySchema=[
                {"AttributeName": "categoria", "KeyType": "HASH"},
                {"AttributeName": "dataset_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "categoria", "AttributeType": "S"},
                {"AttributeName": "dataset_id", "AttributeType": "S"},
                {"AttributeName": "fecha_publicacion", "AttributeType": "S"},
            ],
            LocalSecondaryIndexes=[
                {
                    "IndexName": "lsi-fecha-publicacion",
                    "KeySchema": [
                        {"AttributeName": "categoria", "KeyType": "HASH"},
                        {"AttributeName": "fecha_publicacion", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        t2.wait_until_exists()
        creadas.append("DataGob_Datasets (Con LSI: lsi-fecha-publicacion)")

    # 3. Tabla CON Índice Global Secundario (GSI)
    # El GSI permite consultar por atributos distintos a la clave primaria de la tabla
    if "DataGob_Licitaciones" not in existentes:
        t3 = dynamodb.create_table(
            TableName="DataGob_Licitaciones",
            KeySchema=[
                {"AttributeName": "licitacion_id", "KeyType": "HASH"},
                {"AttributeName": "organismo_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "licitacion_id", "AttributeType": "S"},
                {"AttributeName": "organismo_id", "AttributeType": "S"},
                {"AttributeName": "estado", "AttributeType": "S"},
                {"AttributeName": "importe", "AttributeType": "N"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "gsi-estado-importe",
                    "KeySchema": [
                        {"AttributeName": "estado", "KeyType": "HASH"},
                        {"AttributeName": "importe", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        t3.wait_until_exists()
        creadas.append("DataGob_Licitaciones (Con GSI: gsi-estado-importe)")

    return creadas if creadas else ["Las 3 tablas ya existían activas en DynamoDB"]


def insertar_registros_iniciales():
    """Inserta 3 registros iniciales operativos y 1 de prueba de borrado en cada tabla."""
    t_org = dynamodb.Table("DataGob_Organismos")
    t_dat = dynamodb.Table("DataGob_Datasets")
    t_lic = dynamodb.Table("DataGob_Licitaciones")

    organismos = [
        {"organismo_id": "ORG-01", "nombre": "Ministerio de Hacienda", "sector": "Economia", "presupuesto_anual": Decimal("850000")},
        {"organismo_id": "ORG-02", "nombre": "Ministerio de Ciencia", "sector": "Tecnologia", "presupuesto_anual": Decimal("620000")},
        {"organismo_id": "ORG-03", "nombre": "Junta de Andalucia", "sector": "MedioAmbiente", "presupuesto_anual": Decimal("410000")},
        {"organismo_id": "ORG-TMP", "nombre": "Ente Temporal Prueba", "sector": "Otros", "presupuesto_anual": Decimal("50000")},
    ]
    for item in organismos:
        t_org.put_item(Item=item)

    datasets = [
        {"categoria": "Economia", "dataset_id": "DS-101", "titulo": "Presupuestos Generales", "fecha_publicacion": "2026-01-15", "descargas": 1450},
        {"categoria": "Tecnologia", "dataset_id": "DS-102", "titulo": "Red 5G Nacional", "fecha_publicacion": "2026-03-10", "descargas": 980},
        {"categoria": "MedioAmbiente", "dataset_id": "DS-103", "titulo": "Calidad del Aire", "fecha_publicacion": "2026-05-20", "descargas": 2100},
        {"categoria": "Economia", "dataset_id": "DS-TMP", "titulo": "Borrador Obsoleto", "fecha_publicacion": "2025-01-01", "descargas": 15},
    ]
    for item in datasets:
        t_dat.put_item(Item=item)

    licitaciones = [
        {"licitacion_id": "LIC-501", "organismo_id": "ORG-01", "estado": "ADJUDICADA", "importe": Decimal("120000"), "concepto": "Portal Tributario"},
        {"licitacion_id": "LIC-502", "organismo_id": "ORG-02", "estado": "ABIERTA", "importe": Decimal("340000"), "concepto": "Supercomputacion IA"},
        {"licitacion_id": "LIC-503", "organismo_id": "ORG-03", "estado": "ADJUDICADA", "importe": Decimal("95000"), "concepto": "Sensores Hidricos"},
        {"licitacion_id": "LIC-TMP", "organismo_id": "ORG-01", "estado": "CANCELADA", "importe": Decimal("10000"), "concepto": "Contrato Anulado"},
    ]
    for item in licitaciones:
        t_lic.put_item(Item=item)

    return "4 registros insertados por tabla (3 operativos + 1 para pruebas de borrado)"


def obtener_un_registro():
    """Obtiene un registro específico de cada tabla usando su clave primaria."""
    r1 = dynamodb.Table("DataGob_Organismos").get_item(Key={"organismo_id": "ORG-01"}).get("Item")
    r2 = dynamodb.Table("DataGob_Datasets").get_item(Key={"categoria": "Tecnologia", "dataset_id": "DS-102"}).get("Item")
    r3 = dynamodb.Table("DataGob_Licitaciones").get_item(Key={"licitacion_id": "LIC-502", "organismo_id": "ORG-02"}).get("Item")
    return json.loads(json.dumps({"Organismos": r1, "Datasets": r2, "Licitaciones": r3}, default=_json_serial))


def actualizar_un_registro():
    """Actualiza un atributo en un registro de cada tabla mediante UpdateExpression."""
    u1 = dynamodb.Table("DataGob_Organismos").update_item(
        Key={"organismo_id": "ORG-01"},
        UpdateExpression="SET presupuesto_anual = :val",
        ExpressionAttributeValues={":val": Decimal("900000")},
        ReturnValues="UPDATED_NEW",
    )["Attributes"]

    u2 = dynamodb.Table("DataGob_Datasets").update_item(
        Key={"categoria": "Tecnologia", "dataset_id": "DS-102"},
        UpdateExpression="SET descargas = descargas + :inc",
        ExpressionAttributeValues={":inc": 200},
        ReturnValues="UPDATED_NEW",
    )["Attributes"]

    u3 = dynamodb.Table("DataGob_Licitaciones").update_item(
        Key={"licitacion_id": "LIC-502", "organismo_id": "ORG-02"},
        UpdateExpression="SET estado = :est",
        ExpressionAttributeValues={":est": "ADJUDICADA"},
        ReturnValues="UPDATED_NEW",
    )["Attributes"]

    return json.loads(json.dumps({"Organismos": u1, "Datasets": u2, "Licitaciones": u3}, default=_json_serial))


def eliminar_un_registro():
    """Elimina un registro de prueba en cada tabla usando delete_item."""
    dynamodb.Table("DataGob_Organismos").delete_item(Key={"organismo_id": "ORG-TMP"})
    dynamodb.Table("DataGob_Datasets").delete_item(Key={"categoria": "Economia", "dataset_id": "DS-TMP"})
    dynamodb.Table("DataGob_Licitaciones").delete_item(Key={"licitacion_id": "LIC-TMP", "organismo_id": "ORG-01"})
    return "Eliminados ORG-TMP, DS-TMP y LIC-TMP correctamente"


def obtener_todos_registros():
    """Recupera todos los registros actuales de las 3 tablas mediante scan()."""
    datos = {
        "Organismos": dynamodb.Table("DataGob_Organismos").scan().get("Items", []),
        "Datasets": dynamodb.Table("DataGob_Datasets").scan().get("Items", []),
        "Licitaciones": dynamodb.Table("DataGob_Licitaciones").scan().get("Items", []),
    }
    return json.loads(json.dumps(datos, default=_json_serial))


def filtrar_con_scan():
    """Filtra cada tabla con scan(); en la tabla global usa explícitamente el GSI."""
    # Tabla sin índice: filtro simple por sector
    f1 = dynamodb.Table("DataGob_Organismos").scan(
        FilterExpression=Attr("sector").eq("Economia")
    ).get("Items", [])

    # Tabla con LSI: filtro simple por descargas
    f2 = dynamodb.Table("DataGob_Datasets").scan(
        FilterExpression=Attr("descargas").gt(1000)
    ).get("Items", [])

    # Tabla con GSI: scan apuntando directamente al índice global 'gsi-estado-importe'
    f3 = dynamodb.Table("DataGob_Licitaciones").scan(
        IndexName="gsi-estado-importe",
        FilterExpression=Attr("estado").eq("ADJUDICADA"),
    ).get("Items", [])

    return json.loads(json.dumps({"Organismos": f1, "Datasets": f2, "Licitaciones_GSI": f3}, default=_json_serial))


def filtrar_multiples_condiciones():
    """Aplica varios filtros combinados (AND) en cada tabla."""
    m1 = dynamodb.Table("DataGob_Organismos").scan(
        FilterExpression=Attr("presupuesto_anual").gte(Decimal("500000")) & Attr("sector").ne("Otros")
    ).get("Items", [])

    m2 = dynamodb.Table("DataGob_Datasets").scan(
        FilterExpression=Attr("descargas").gte(1000) & Attr("fecha_publicacion").gte("2026-01-01")
    ).get("Items", [])

    m3 = dynamodb.Table("DataGob_Licitaciones").scan(
        IndexName="gsi-estado-importe",
        FilterExpression=Attr("estado").eq("ADJUDICADA") & Attr("importe").gte(Decimal("100000")),
    ).get("Items", [])

    return json.loads(json.dumps({"Organismos": m1, "Datasets": m2, "Licitaciones": m3}, default=_json_serial))


def eliminacion_condicional():
    """Ejecuta borrado condicional (ConditionExpression) en cada tabla; en la global localiza vía GSI."""
    resultados = {}

    # 1. Tabla sin índice: solo borra si presupuesto_anual < 450000
    try:
        dynamodb.Table("DataGob_Organismos").delete_item(
            Key={"organismo_id": "ORG-03"},
            ConditionExpression=Attr("presupuesto_anual").lt(Decimal("450000")),
        )
        resultados["Organismos"] = "ORG-03 eliminado (cumplió presupuesto < 450000)"
    except ClientError as e:
        resultados["Organismos"] = f"Condición no cumplida: {e.response['Error']['Code']}"

    # 2. Tabla con LSI: solo borra si descargas < 1500
    try:
        dynamodb.Table("DataGob_Datasets").delete_item(
            Key={"categoria": "Tecnologia", "dataset_id": "DS-102"},
            ConditionExpression=Attr("descargas").lt(1500),
        )
        resultados["Datasets"] = "DS-102 eliminado (cumplió descargas < 1500)"
    except ClientError as e:
        resultados["Datasets"] = f"Condición no cumplida: {e.response['Error']['Code']}"

    # 3. Tabla con GSI: primero consultamos el GSI para encontrar la clave del ítem con importe < 100000
    t_lic = dynamodb.Table("DataGob_Licitaciones")
    candidatos = t_lic.scan(
        IndexName="gsi-estado-importe",
        FilterExpression=Attr("estado").eq("ADJUDICADA") & Attr("importe").lt(Decimal("100000")),
    ).get("Items", [])

    if candidatos:
        objetivo = candidatos[0]
        t_lic.delete_item(
            Key={"licitacion_id": objetivo["licitacion_id"], "organismo_id": objetivo["organismo_id"]},
            ConditionExpression=Attr("importe").lt(Decimal("100000")),
        )
        resultados["Licitaciones_GSI"] = f"{objetivo['licitacion_id']} localizado vía GSI y eliminado condicionalmente"
    else:
        resultados["Licitaciones_GSI"] = "Ningún registro en el GSI cumplió la condición de borrado"

    return resultados


def consultas_partiql():
    """Ejecuta sentencias PartiQL (SQL-compatible para DynamoDB) en las 3 tablas."""
    q1 = client.execute_statement(
        Statement='SELECT organismo_id, nombre, presupuesto_anual FROM "DataGob_Organismos" WHERE presupuesto_anual > 500000'
    )["Items"]

    q2 = client.execute_statement(
        Statement='SELECT categoria, dataset_id, titulo, descargas FROM "DataGob_Datasets" WHERE descargas > 1000'
    )["Items"]

    q3 = client.execute_statement(
        Statement='SELECT licitacion_id, organismo_id, estado, importe FROM "DataGob_Licitaciones" WHERE estado = \'ADJUDICADA\''
    )["Items"]

    datos = {
        "PartiQL_Organismos": _deserializar_partiql(q1),
        "PartiQL_Datasets": _deserializar_partiql(q2),
        "PartiQL_Licitaciones": _deserializar_partiql(q3),
    }
    return json.loads(json.dumps(datos, default=_json_serial))