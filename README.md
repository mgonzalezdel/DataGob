# ORDEN DE EJECUCIÓN DE ARCHIVOS Y COMANDOS

1. Creación de los contenedores
'''bash
docker compose up -d
'''

2. Creación DDL
'''bash
python3 creacionDDL.py
'''

3. Poblar la base de datos
'''bash
python3 poblar_datagob.py
'''

4. Testear el servicio de Redis (Opcional pero recomendado)
'''bash 
python3 test_redis.py
'''

5. Realización de actividades
'''bash
python3 actividades1_20.py
python3 actividades21_22.py
'''