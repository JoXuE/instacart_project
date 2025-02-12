import os
import pandas as pd
from mage_ai.io.snowflake import Snowflake
from mage_ai.io.config import ConfigKey

# Verifica que el decorador está correctamente importado
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader

# Función para obtener la configuración de Snowflake
def create_snowflake_connection():
    return {
        ConfigKey.SNOWFLAKE_ACCOUNT: os.getenv("SNOWFLAKE_ACCOUNT"),
        ConfigKey.SNOWFLAKE_USER: os.getenv("SNOWFLAKE_USER"),
        ConfigKey.SNOWFLAKE_PASSWORD: os.getenv("SNOWFLAKE_PASSWORD"),
        ConfigKey.SNOWFLAKE_DEFAULT_WH: os.getenv("SNOWFLAKE_WAREHOUSE"),
        ConfigKey.SNOWFLAKE_DEFAULT_DB: os.getenv("SNOWFLAKE_DATABASE"),
        ConfigKey.SNOWFLAKE_DEFAULT_SCHEMA: "RAW",
    }

# Función para extraer datos en batches desde Snowflake
def extract_from_snowflake_in_batches(table_name, batch_size=100000):
    config = create_snowflake_connection()
    offset = 0
    batch_data = []
    
    while True:
        query = f"SELECT * FROM {table_name} LIMIT {batch_size} OFFSET {offset};"
        print(f"Ejecutando batch: {offset} - {offset + batch_size} en {table_name}")
        
        with Snowflake.with_config(config) as loader:
            df = loader.load(query)
        
        if df.empty:
            break  # Si no hay más datos, salir del loop
        
        batch_data.append(df)
        offset += batch_size  # Mover el offset para el próximo batch

    # Unir todos los batches en un solo DataFrame
    return pd.concat(batch_data, ignore_index=True) if batch_data else pd.DataFrame()

# Decorador @data_loader para que MageAI detecte la función
@data_loader
def load_from_snowflake(*args, **kwargs):
    """
    Extrae datos de varias tablas desde Snowflake en batches y los devuelve como un diccionario de DataFrames.
    """
    data = {
        "departments": extract_from_snowflake_in_batches("departments", batch_size=50000),
        "aisles": extract_from_snowflake_in_batches("aisles", batch_size=50000),
        "products": extract_from_snowflake_in_batches("products", batch_size=50000),
        "instacart_orders": extract_from_snowflake_in_batches("instacart_orders", batch_size=50000),
        "order_products": extract_from_snowflake_in_batches("order_products", batch_size=50000),
    }

    return data
