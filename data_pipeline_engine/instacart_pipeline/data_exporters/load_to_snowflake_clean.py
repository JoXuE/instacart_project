import os
import pandas as pd
from mage_ai.io.snowflake import Snowflake
from mage_ai.io.config import ConfigKey

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def load_to_snowflake_clean(data, *args, **kwargs):
    """
    Carga los datos transformados en el esquema CLEAN de Snowflake en batches de manera correcta.
    """

    # 🔹 Configuración de Snowflake
    snowflake_config = {
        ConfigKey.SNOWFLAKE_ACCOUNT: os.getenv("SNOWFLAKE_ACCOUNT"),
        ConfigKey.SNOWFLAKE_USER: os.getenv("SNOWFLAKE_USER"),
        ConfigKey.SNOWFLAKE_PASSWORD: os.getenv("SNOWFLAKE_PASSWORD"),
        ConfigKey.SNOWFLAKE_DEFAULT_WH: os.getenv("SNOWFLAKE_WAREHOUSE"),
        ConfigKey.SNOWFLAKE_DEFAULT_DB: os.getenv("SNOWFLAKE_DATABASE"),
        ConfigKey.SNOWFLAKE_DEFAULT_SCHEMA: "CLEAN",
    }

    # 🔹 Mapeo de tablas para carga en Snowflake
    table_mappings = {
        "fact_orders": "FACT_ORDERS",
        "dim_products": "DIM_PRODUCTS",
        "dim_departments": "DIM_DEPARTMENTS",
        "dim_aisles": "DIM_AISLES",
        "dim_users": "DIM_USERS",
        "dim_orders": "DIM_ORDERS"
    }

    # 🔹 Tamaño del batch
    BATCH_SIZE = 100000  # Número de filas por batch

    # Conectar a Snowflake y exportar las tablas
    with Snowflake.with_config(snowflake_config) as loader:
        for table, target_table in table_mappings.items():
            if table in data:
                df_to_export = data[table].copy()  # Crear copia para evitar modificaciones en el original
                
                # Asegurar que no haya duplicados antes de exportar
                df_to_export.drop_duplicates(inplace=True)

                print(f"Cargando datos en {target_table} en batches...")

                #  Dividir en batches y exportar
                total_rows = len(df_to_export)
                for i in range(0, total_rows, BATCH_SIZE):
                    batch_df = df_to_export.iloc[i:i + BATCH_SIZE].copy() 
                    
                    # Resetear el índice antes de exportar para evitar errores en Snowflake
                    batch_df.reset_index(drop=True, inplace=True)

                    print(f"Insertando {len(batch_df)} registros en {target_table} (Batch {i // BATCH_SIZE + 1})...")

                    loader.export(batch_df, target_table, if_exists="append")  # Se usa "append" para evitar sobreescrituras

                print(f" Exportación finalizada para {target_table} con {total_rows} registros.")

            else:
                print(f"Advertencia: La tabla '{table}' no está en los datos transformados.")

    print("Proceso de carga finalizado con éxito.")
