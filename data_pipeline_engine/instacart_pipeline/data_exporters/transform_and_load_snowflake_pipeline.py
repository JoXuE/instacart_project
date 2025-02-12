import os
import pandas as pd
from mage_ai.io.snowflake import Snowflake
from mage_ai.io.config import ConfigKey

# Verifica que el decorador está correctamente importado
if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def transform_and_load_to_snowflake(data, *args, **kwargs):
    """
    Transforma los datos extraídos de Snowflake en el esquema RAW,
    limpiando valores nulos, eliminando duplicados, ajustando tipos de datos
    y cargándolos en el esquema modelado bajo el Star-Schema.
    """

    # Configuración correcta de Snowflake usando las claves esperadas por MageAI
    snowflake_config = {
        ConfigKey.SNOWFLAKE_ACCOUNT: os.getenv("SNOWFLAKE_ACCOUNT"),
        ConfigKey.SNOWFLAKE_USER: os.getenv("SNOWFLAKE_USER"),
        ConfigKey.SNOWFLAKE_PASSWORD: os.getenv("SNOWFLAKE_PASSWORD"),
        ConfigKey.SNOWFLAKE_DEFAULT_WH: os.getenv("SNOWFLAKE_WAREHOUSE"),
        ConfigKey.SNOWFLAKE_DEFAULT_DB: os.getenv("SNOWFLAKE_DATABASE"),
        ConfigKey.SNOWFLAKE_DEFAULT_SCHEMA: os.getenv("SNOWFLAKE_SCHEMA"),
        "insecure_mode": True  
    }

    # Verificar que no haya valores `None` en la configuración antes de la conexión
    for key, value in snowflake_config.items():
        if value is None:
            raise ValueError(f"ERROR: La variable de entorno '{key.value}' no está definida.")

    print("Iniciando transformación de datos...")

    def handle_missing_values(df):
        """
        Maneja valores nulos en las columnas clave, imputando cuando sea necesario.
        """
        print("Manejo de valores faltantes...")
        if 'days_since_prior_order' in df.columns:
            df['days_since_prior_order'].fillna(df['days_since_prior_order'].median(), inplace=True)

        columnas_a_verificar = ['order_id', 'user_id', 'product_id']
        columnas_presentes = [col for col in columnas_a_verificar if col in df.columns]

        if columnas_presentes:
            df.dropna(subset=columnas_presentes, inplace=True)

        return df

    def drop_duplicates(df):
        """
        Elimina registros duplicados en las tablas.
        """
        print("🗑 Eliminando registros duplicados...")
        df.drop_duplicates(inplace=True)
        return df

    def generate_derived_columns(df, table_name):
        """
        Genera columnas derivadas según la tabla.
        """
        print(f"Generando columnas derivadas para {table_name}...")
        if 'order_hour_of_day' in df.columns:
            df['is_peak_hour'] = df['order_hour_of_day'].apply(lambda x: 1 if 10 <= x <= 18 else 0)
        return df

    def map_data_types(df, table_name):
        """
        Ajusta los tipos de datos de las columnas según el modelo definido.
        """
        print(f"🛠 Mapeando tipos de datos en {table_name}...")
        data_types = {
            "order_id": "int32",
            "user_id": "int32",
            "product_id": "int32",
            "order_dow": "int8",
            "order_hour_of_day": "int8",
            "days_since_prior_order": "float32"
        }
        for col, dtype in data_types.items():
            if col in df.columns:
                df[col] = df[col].astype(dtype)
        return df

    # Definir las tablas a procesar
    table_mappings = {
        "departments": "DIM_DEPARTMENTS",
        "aisles": "DIM_AISLES",
        "products": "DIM_PRODUCTS",
        "instacart_orders": "FACT_ORDERS",
        "order_products": "FACT_ORDER_PRODUCTS",
    }

    transformed_tables = {}

    # Aplicar transformaciones
    for table, df in data.items():
        print(f"Procesando tabla: {table}...")
        df = handle_missing_values(df)
        df = drop_duplicates(df)
        df = generate_derived_columns(df, table)
        df = map_data_types(df, table)
        transformed_tables[table_mappings[table]] = df

        print(f"Transformación completada para {table}. Total registros: {df.shape[0]}")

    # Conectar a Snowflake y cargar datos transformados
    with Snowflake.with_config(snowflake_config) as loader:
        for table, df in transformed_tables.items():
            print(f"Cargando datos en Snowflake: {table}...")
            loader.export(df, table, if_exists="replace")
            print(f"Datos cargados en {table}.")

    print("Proceso de transformación y carga completado con éxito.")
