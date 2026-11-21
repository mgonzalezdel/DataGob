import json
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Attr
import pymysql
from config_aws import AWS_REGION, RDS_CONFIG


def _json_serial(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return str(obj)


def generar_json_integrado(ruta_salida="datagob_integrado.json"):
    """Extrae datos filtrados de DynamoDB y RDS y los une lógicamente por organismo_id."""
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)

    # 1. Extracción filtrada desde DynamoDB
    # Organismos con presupuesto >= 500.000
    org_dynamo = dynamodb.Table("DataGob_Organismos").scan(
        FilterExpression=Attr("presupuesto_anual").gte(Decimal("500000"))
    ).get("Items", [])

    # Licitaciones adjudicadas consultando el GSI
    lic_dynamo = dynamodb.Table("DataGob_Licitaciones").scan(
        IndexName="gsi-estado-importe",
        FilterExpression=Attr("estado").eq("ADJUDICADA"),
    ).get("Items", [])

    # Datasets populares (> 1000 descargas)
    dat_dynamo = dynamodb.Table("DataGob_Datasets").scan(
        FilterExpression=Attr("descargas").gt(1000)
    ).get("Items", [])

    # 2. Extracción filtrada desde RDS (MySQL/MariaDB)
    conn = pymysql.connect(
        host=RDS_CONFIG["host"],
        port=RDS_CONFIG["port"],
        user=RDS_CONFIG["user"],
        password=RDS_CONFIG["password"],
        database=RDS_CONFIG["database"],
        cursorclass=pymysql.cursors.DictCursor,
    )
    with conn.cursor() as cur:
        cur.execute("""
            SELECT organismo_id, nombre, ambito, comunidad, empleados
            FROM organismos_publicos
            WHERE ambito = 'Estatal';
        """)
        org_rds = cur.fetchall()

        cur.execute("""
            SELECT pub_id, organismo_id, categoria, titulo, descargas_totales, fecha_alta
            FROM publicaciones_datasets
            WHERE descargas_totales >= 2500;
        """)
        pub_rds = cur.fetchall()
    conn.close()

    # 3. Unión lógica relacional + NoSQL indexada por 'organismo_id'
    dynamo_org_map = {item["organismo_id"]: item for item in org_dynamo}
    entidades_integradas = []

    for org in org_rds:
        oid = org["organismo_id"]
        info_nosql = dynamo_org_map.get(oid, {})

        # Vincular publicaciones RDS y licitaciones DynamoDB pertenecientes al mismo organismo
        publicaciones_org = [p for p in pub_rds if p["organismo_id"] == oid]
        licitaciones_org = [l for l in lic_dynamo if l["organismo_id"] == oid]

        # Vincular datasets DynamoDB que coincidan con las categorías publicadas por el organismo
        categorias_org = {p["categoria"] for p in publicaciones_org}
        datasets_relacionados = [d for d in dat_dynamo if d["categoria"] in categorias_org]

        entidades_integradas.append({
            "organismo_id": oid,
            "nombre": org["nombre"],
            "datos_institucionales_rds": {
                "ambito": org["ambito"],
                "comunidad": org["comunidad"],
                "empleados": org["empleados"],
                "publicaciones_destacadas": publicaciones_org,
            },
            "datos_operativos_dynamodb": {
                "sector": info_nosql.get("sector"),
                "presupuesto_anual": info_nosql.get("presupuesto_anual"),
                "licitaciones_adjudicadas": licitaciones_org,
                "datasets_alta_demanda": datasets_relacionados,
            },
        })

    documento_final = {
        "proyecto": "DataGob - Integracion Hibrida RDS + DynamoDB",
        "total_organismos_integrados": len(entidades_integradas),
        "organismos": entidades_integradas,
    }

    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(documento_final, f, indent=2, default=_json_serial, ensure_ascii=False)

    return f"Archivo '{ruta_salida}' generado con {len(entidades_integradas)} organismos integrados"