import pandas as pd
import numpy as np

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer

BATCH_SIZE = 50000  # Tamaño del batch (ajústalo según la memoria disponible)

@transformer
def transform_clean_data(data, *args, **kwargs):
    """
    Transforma los datos brutos en datos limpios siguiendo el modelo Star-Schema en batches.
    """

    print("Iniciando transformación de datos en batches...")

    transformed_data = {}

    # --- 1. Transformar la tabla de hechos fact_orders en batches ---
    fact_orders_list = []
    for i in range(0, len(data['order_products']), BATCH_SIZE):
        batch = data['order_products'].iloc[i:i+BATCH_SIZE].copy()
        
        # Manejo de valores faltantes
        if 'days_since_prior_order' in batch.columns:
            batch.loc[:, "days_since_prior_order"] = batch["days_since_prior_order"].fillna(batch["days_since_prior_order"].median())

        # Manejo de valores nulos en 'add_to_cart_order', reemplazando con -1
        if "add_to_cart_order" in batch.columns:
            batch.loc[:, "add_to_cart_order"] = batch["add_to_cart_order"].fillna(-1)

        batch.drop_duplicates(inplace=True)

        # Renombrar columnas
        batch.rename(columns={
            "add_to_cart_order": "cart_order",
            "reordered": "is_reordered"
        }, inplace=True)

        fact_orders_list.append(batch)
    
    transformed_data["fact_orders"] = pd.concat(fact_orders_list, ignore_index=True)
    
    # --- 2. Transformar dimensiones sin batches (son más pequeñas) ---
    transformed_data["dim_products"] = data['products'][['product_id', 'product_name', 'aisle_id', 'department_id']].drop_duplicates()
    transformed_data["dim_departments"] = data['departments'][['department_id', 'department']].rename(columns={'department': 'department_name'})
    transformed_data["dim_aisles"] = data['aisles'][['aisle_id', 'aisle']].rename(columns={'aisle': 'aisle_name'})

    # Transformar dim_orders en batches
    dim_orders_list = []
    for i in range(0, len(data['instacart_orders']), BATCH_SIZE):
        batch = data['instacart_orders'].iloc[i:i+BATCH_SIZE].copy()
        batch.drop_duplicates(inplace=True)
        dim_orders_list.append(batch)

    transformed_data["dim_orders"] = pd.concat(dim_orders_list, ignore_index=True)

    # Transformar dim_users sin batches (no hay necesidad de dividir)
    transformed_data["dim_users"] = transformed_data["dim_orders"][['user_id']].drop_duplicates()

    print("Transformación por batches completada. Tablas generadas:", list(transformed_data.keys()))
    
    return transformed_data 
