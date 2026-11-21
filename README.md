# ORDEN DE EJECUCIÓN DE ARCHIVOS Y COMANDOS

---

## TAREA 1: Redis y MariaDB (Entorno Local)

*(Ejecutar dentro de la carpeta de la primera práctica)*

1. Creación de los contenedores
```bash
docker compose up -d
```

2. Creación DDL
```bash
python3 creacionDDL.py
```

3. Poblar la base de datos
```bash
python3 poblar_datagob.py
```

4. Testear el servicio de Redis (Opcional pero recomendado)
```bash
python3 test_redis.py
```

5. Realización de actividades
```bash
python3 actividades1_20.py
python3 actividades21_22.py
```

---

## TAREA 2: AWS DynamoDB y RDS (Laboratorio AWS Academy)

*(Ejecutar dentro de la carpeta de la práctica de AWS)*

1. Instalación de dependencias
```bash
pip install boto3 pymysql
```

2. Configuración de credenciales temporales de AWS Academy (pegar credenciales de *AWS Details -> Show*)
```bash
mkdir -p ~/.aws && nano ~/.aws/credentials
```
*(En Windows PowerShell)*:
```powershell
New-Item -Path "$HOME\.aws\credentials" -ItemType File -Force; notepad "$HOME\.aws\credentials"
```

3. Definición del Endpoint de la instancia RDS (si no se edita directamente en `config_aws.py`)
```bash
export RDS_HOST="..."
```
*(En Windows PowerShell)*
```powershell
$env:RDS_HOST="..."
```

4. Ejecución del orquestador completo (DynamoDB, RDS e integración JSON)
```bash
python3 main.py
```