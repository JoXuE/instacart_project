import os
import pandas as pd
from mage_ai.io.snowflake import Snowflake
from mage_ai.io.config import ConfigKey  # Importar ConfigKey para usar las claves correctas

# Verifica que el decorador está correctamente importado
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader

# Configuración de conexión a Snowflake
def create_snowflake_connection():
    return {
        ConfigKey.SNOWFLAKE_ACCOUNT: os.getenv("SNOWFLAKE_ACCOUNT"),
        ConfigKey.SNOWFLAKE_USER: os.getenv("SNOWFLAKE_USER"),
        ConfigKey.SNOWFLAKE_PASSWORD: os.getenv("SNOWFLAKE_PASSWORD"),
        ConfigKey.SNOWFLAKE_DEFAULT_WH: os.getenv("SNOWFLAKE_WAREHOUSE"),
        ConfigKey.SNOWFLAKE_DEFAULT_DB: os.getenv("SNOWFLAKE_DATABASE"),
        ConfigKey.SNOWFLAKE_DEFAULT_SCHEMA: "RAW",  # Se mantiene RAW como esquema por defecto
    }

# Función para extraer datos de una tabla específica desde Snowflake
def extract_from_snowflake(query, config):
    print(f"Ejecutando query en Snowflake: {query}")
    with Snowflake.with_config(config) as loader:
        df = loader.load(query)
    print(f"Datos extraídos: {len(df)} registros.")
    return df

# Decorador @data_loader para que MageAI detecte la función
@data_loader
def load_from_snowflake(*args, **kwargs):
    """
    Extrae datos de varias tablas desde Snowflake y los devuelve como un diccionario de DataFrames.
    """
    config = create_snowflake_connection()

    tables = ["departments", "aisles", "products", "instacart_orders", "order_products"]
    
    data = {}
    for table in tables:
        try:
            data[table] = extract_from_snowflake(f'SELECT * FROM "{table.upper()}"', config)
        except Exception as e:
            print(f"Error al extraer datos de {table}: {e}")

    return data
