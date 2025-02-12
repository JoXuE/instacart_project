import os
from mage_ai.io.snowflake import Snowflake
from mage_ai.io.config import ConfigKey  

# Verifica que el decorador está correctamente importado
if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def mysql_to_snowflake(data, *args, **kwargs):
    """
    Exporta datos desde MySQL a Snowflake en el esquema RAW.
    """

    # Mapeo de nombres de tablas entre MySQL y Snowflake
    table_mappings = {
        "departments": "DEPARTMENTS",
        "aisles": "AISLES",
        "products": "PRODUCTS",
        "instacart_orders": "INSTACART_ORDERS",
        "order_products": "ORDER_PRODUCTS",
    }

    # Configuración correcta de Snowflake usando las claves esperadas por MageAI
    snowflake_config = {
        ConfigKey.SNOWFLAKE_ACCOUNT: os.getenv("SNOWFLAKE_ACCOUNT"),
        ConfigKey.SNOWFLAKE_USER: os.getenv("SNOWFLAKE_USER"),
        ConfigKey.SNOWFLAKE_PASSWORD: os.getenv("SNOWFLAKE_PASSWORD"),
        ConfigKey.SNOWFLAKE_DEFAULT_WH: os.getenv("SNOWFLAKE_WAREHOUSE"),
        ConfigKey.SNOWFLAKE_DEFAULT_DB: os.getenv("SNOWFLAKE_DATABASE"),
        ConfigKey.SNOWFLAKE_DEFAULT_SCHEMA: os.getenv("SNOWFLAKE_SCHEMA"), 
    }

    # Verificar que no haya valores `None` en la configuración antes de la conexión
    for key, value in snowflake_config.items():
        if value is None:
            raise ValueError(f"ERROR: La variable de entorno '{key.value}' no está definida.")

    # Conectar a Snowflake usando la misma configuración que el Data Loader
    with Snowflake.with_config(snowflake_config) as loader:
        for table, target_table in table_mappings.items():
            print(f"Exportando datos de {table} a {target_table} en Snowflake...")
            loader.export(data[table], target_table, if_exists="replace")
            print(f"Datos exportados a {target_table}.")
