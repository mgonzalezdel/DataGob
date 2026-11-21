import os
from dotenv import load_dotenv

load_dotenv()

# Región por defecto en AWS Academy Learner Lab
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Configuración de la instancia RDS (MySQL / MariaDB)
RDS_CONFIG = {
    "host": os.getenv("RDS_HOST"),
    "port": int(os.getenv("RDS_PORT")),
    "user": os.getenv("RDS_USER", "admin"),
    "password": os.getenv("RDS_PASSWORD"),
    "database": "datagob_db",
}