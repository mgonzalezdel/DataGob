import json
import dynamo_manager as dyn
import rds_manager as rds
import integracion_json as integ


def ejecutar_paso(titulo, descripcion, funcion):
    """Ejecuta una funcionalidad mostrando traza clara en consola y capturando errores."""
    print("=" * 80)
    print(f"[EJECUTANDO] {titulo}")
    print(f"[DESCRIPCIÓN] {descripcion}")
    print("-" * 80)
    try:
        resultado = funcion()
        if isinstance(resultado, (dict, list)):
            print("[RESULTADO]:\n" + json.dumps(resultado, indent=2, ensure_ascii=False))
        else:
            print(f"[RESULTADO]:\n{resultado}")
    except Exception as error:
        print(f"[ERROR CONTROLADO en {titulo}]: {error}")
    print("=" * 80 + "\n")


def main():
    print("\n>>> INICIANDO PRÁCTICA AWS DYNAMODB & RDS - PROYECTO DATAGOB <<<\n")

    # BLOQUE 1: DYNAMODB
    ejecutar_paso(
        "1. DynamoDB -> crear_tablas_dynamodb()",
        "Crea 3 tablas: sin índices (Organismos), con LSI (Datasets) y con GSI (Licitaciones).",
        dyn.crear_tablas_dynamodb,
    )
    ejecutar_paso(
        "2. DynamoDB -> insertar_registros_iniciales()",
        "Inserta los registros iniciales en cada una de las 3 tablas de DynamoDB.",
        dyn.insertar_registros_iniciales,
    )
    ejecutar_paso(
        "3. DynamoDB -> obtener_un_registro()",
        "Recupera un registro individual por clave primaria en cada tabla (get_item).",
        dyn.obtener_un_registro,
    )
    ejecutar_paso(
        "4. DynamoDB -> actualizar_un_registro()",
        "Modifica atributos específicos de un registro en cada tabla (update_item).",
        dyn.actualizar_un_registro,
    )
    ejecutar_paso(
        "5. DynamoDB -> eliminar_un_registro()",
        "Elimina un registro de prueba en cada tabla (delete_item).",
        dyn.eliminar_un_registro,
    )
    ejecutar_paso(
        "6. DynamoDB -> obtener_todos_registros()",
        "Lista todos los ítems almacenados actualmente en las 3 tablas (scan).",
        dyn.obtener_todos_registros,
    )
    ejecutar_paso(
        "7. DynamoDB -> filtrar_con_scan()",
        "Filtra registros en cada tabla con scan(); en Licitaciones consulta el GSI.",
        dyn.filtrar_con_scan,
    )
    ejecutar_paso(
        "8. DynamoDB -> filtrar_multiples_condiciones()",
        "Aplica filtros compuestos (AND) sobre atributos en las 3 tablas.",
        dyn.filtrar_multiples_condiciones,
    )
    ejecutar_paso(
        "9. DynamoDB -> eliminacion_condicional()",
        "Ejecuta borrado condicional en cada tabla; en Licitaciones localiza vía GSI.",
        dyn.eliminacion_condicional,
    )
    ejecutar_paso(
        "10. DynamoDB -> consultas_partiql()",
        "Ejecuta sentencias SQL PartiQL (SELECT ... WHERE) en las 3 tablas.",
        dyn.consultas_partiql,
    )

    # BLOQUE 2: RDS (MYSQL / MARIADB)
    ejecutar_paso(
        "11. RDS -> crear_bd_y_tablas_rds()",
        "Crea la base de datos 'datagob_rds', sus tablas relacionales e inserta datos.",
        rds.crear_bd_y_tablas_rds,
    )
    ejecutar_paso(
        "12. RDS -> ejecutar_consultas_rds_json()",
        "Ejecuta 3 consultas SQL (JOIN, GROUP BY, filtros) y devuelve resultado en JSON.",
        rds.ejecutar_consultas_rds_json,
    )

    # BLOQUE 3: INTEGRACIÓN HÍBRIDA JSON
    ejecutar_paso(
        "13. Integración -> generar_json_integrado()",
        "Consulta con filtros DynamoDB y RDS y une los datos por organismo_id en un JSON único.",
        integ.generar_json_integrado,
    )

    print(">>> EJECUCIÓN COMPLETA FINALIZADA <<<")


if __name__ == "__main__":
    main()