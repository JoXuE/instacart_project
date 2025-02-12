import pymysql
import pandas as pd
import os
import sys
from pathlib import Path


# Verificar que las variables de entorno están definidas
required_env_vars = ["MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE"]
for var in required_env_vars:
    if not os.getenv(var):
        print(f"ERROR: La variable de entorno '{var}' no está definida.")
        sys.exit(1)

# Configuración de la conexión a MySQL
db_config = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
}

# Detectar dinámicamente la ruta del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent  # Ajusta según la estructura de tu proyecto
DATA_DIR = BASE_DIR / "data"
SQL_SCRIPT_PATH = BASE_DIR / "scripts" / "instacart_schema.sql"


# Función para ejecutar el script SQL y recrear la base de datos
def execute_sql_script():
    print("Ejecutando script SQL para recrear la base de datos...")
    try:
        connection = pymysql.connect(host=db_config["host"],
                                     user=db_config["user"],
                                     password=db_config["password"])
        cursor = connection.cursor()

        with open(SQL_SCRIPT_PATH, "r") as f:
            sql_script = f.read().strip()

        if not sql_script:
            raise ValueError("El script SQL está vacío.")

        statements = sql_script.split(";")
        for statement in statements:
            if statement.strip():
                cursor.execute(statement)

        connection.commit()
        print("Base de datos recreada exitosamente.")
    except Exception as e:
        print(f"Error ejecutando el script SQL: {e}")
    finally:
        cursor.close()
        connection.close()


# Función para detectar automáticamente el delimitador ("," o ";")
def detect_delimiter(file_path):
    with open(file_path, "r") as f:
        first_line = f.readline()
        return ";" if ";" in first_line else ","


# Función para cargar CSV en MySQL
def load_csv_to_mysql(file_name, table_name, connection, batch_size=10000):
    file_path = DATA_DIR / file_name

    # Detectar delimitador y cargar CSV correctamente
    delimiter = detect_delimiter(file_path)
    df = pd.read_csv(file_path, sep=delimiter)

    # Eliminar espacios en los nombres de las columnas
    df.columns = df.columns.str.strip()

    cursor = connection.cursor()

    # Construir la consulta SQL de inserción con IGNORE para evitar errores de duplicados
    columns = ", ".join(df.columns)
    values = ", ".join(["%s"] * len(df.columns))
    insert_query = f"INSERT IGNORE INTO {table_name} ({columns}) VALUES ({values})"

    # Crear tuplas para los datos, reemplazando valores NaN con None
    data_tuples = [
        tuple(None if pd.isna(x) else x for x in row)
        for row in df.itertuples(index=False, name=None)
    ]

    # Desactivar restricciones de claves foráneas antes de la inserción
    cursor.execute("SET FOREIGN_KEY_CHECKS=0;")

    # Insertar los datos en lotes
    total_rows = len(data_tuples)
    for i in range(0, total_rows, batch_size):
        batch = data_tuples[i:i + batch_size]
        cursor.executemany(insert_query, batch)
        connection.commit()
        print(f"Insertados {i + len(batch)} de {total_rows} registros en {table_name}...")

    # Reactivar restricciones de claves foráneas
    cursor.execute("SET FOREIGN_KEY_CHECKS=1;")

    print(f"Todos los datos insertados en {table_name}")



# Ejecutar el script SQL antes de la carga de datos
execute_sql_script()

# Conectar a MySQL y cargar los datos
try:
    connection = pymysql.connect(**db_config)
    print("Conexión a MySQL exitosa")

    # Cargar los archivos CSV en MySQL
    load_csv_to_mysql("departments.csv", "departments", connection)
    load_csv_to_mysql("aisles.csv", "aisles", connection)
    load_csv_to_mysql("products.csv", "products", connection)
    load_csv_to_mysql("instacart_orders.csv", "instacart_orders", connection)
    load_csv_to_mysql("order_products.csv", "order_products", connection, batch_size=100000)

finally:
    connection.close()
    print("Conexión cerrada")
