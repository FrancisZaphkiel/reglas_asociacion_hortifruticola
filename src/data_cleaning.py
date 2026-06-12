import pandas as pd
import os

PROVINCE_TO_REGION = {
    "Provincia de Quillota": "Región de Valparaíso",
    "Provincia del Elquí": "Región de Coquimbo",
    "Provincia de Limarí": "Región de Coquimbo",
    "Provincia de Curicó": "Región del Maule",
    "Provincia de San Felipe de Aconcagua": "Región de Valparaíso",
    "Provincia de Cautín": "Región de La Araucanía",
    "Provincia de Diguillín": "Región de Ñuble",
    "Provincia de Melipilla": "Región Metropolitana de Santiago",
    "Provincia de Santiago": "Región Metropolitana de Santiago",
    "Provincia de Valparaíso": "Región de Valparaíso",
    "Provincia de Los Andes": "Región de Valparaíso",
    "Provincia de Petorca": "Región de Valparaíso",
    "Provincia de San Antonio": "Región de Valparaíso",
    "Provincia de Marga Marga": "Región de Valparaíso",
    "Provincia de Chacabuco": "Región Metropolitana de Santiago",
    "Provincia de Cordillera": "Región Metropolitana de Santiago",
    "Provincia de Maipo": "Región Metropolitana de Santiago",
    "Provincia de Talagante": "Región Metropolitana de Santiago",
    "Provincia de Choapa": "Región de Coquimbo",
    "Provincia de Talca": "Región del Maule",
    "Provincia de Linares": "Región del Maule",
    "Provincia de Cauquenes": "Región del Maule",
    "Provincia de Punilla": "Región de Ñuble",
    "Provincia de Itata": "Región de Ñuble",
    "Provincia de Concepción": "Región del Biobío",
    "Provincia de Biobío": "Región del Biobío",
    "Provincia de Arauco": "Región del Biobío",
    "Provincia de Malleco": "Región de La Araucanía",
}

def load_clean_and_sample(dataset_dir, sample_size=3000, random_state=42):
    """
    Carga los datasets de 2025 y 2026, los concatena, realiza un muestreo aleatorio
    y aplica la estandarización geográfica y de nulos.
    """
    file_2025 = os.path.join(dataset_dir, "2025.csv")
    file_2026 = os.path.join(dataset_dir, "2026.csv")
    
    if not os.path.exists(file_2025) or not os.path.exists(file_2026):
        raise FileNotFoundError(f"No se encontraron los archivos 2025.csv y 2026.csv en {dataset_dir}")
        
    df_2025 = pd.read_csv(file_2025, decimal=',')
    df_2026 = pd.read_csv(file_2026, decimal=',')
    
    df_combined = pd.concat([df_2025, df_2026], ignore_index=True)
    
    df_sampled = df_combined.sample(n=sample_size, random_state=random_state).copy()
    
    categorical_cols = ["Region", "Mercado", "Subsector", "Producto", "Variedad / Tipo", "Calidad", "Origen"]
    for col in categorical_cols:
        df_sampled[col] = df_sampled[col].fillna("Sin especificar").astype(str).str.strip()
        
    df_sampled["Origen"] = df_sampled["Origen"].replace(PROVINCE_TO_REGION)
    
    df_final = df_sampled[categorical_cols]
    
    return df_final
