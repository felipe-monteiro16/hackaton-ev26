"""
Análise Epidemiológica - Dengue x Precipitação
Montes Claros/MG - 2019-2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configurações
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# Diretórios
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def load_sinan_data():
    """Carrega e faz análise exploratória inicial dos dados SINAN"""
    print("=" * 80)
    print("CARREGANDO DADOS SINAN")
    print("=" * 80)
    
    # Carregar dados
    df = pd.read_csv(DATA_DIR / "SINAN_EIXO_2.csv")
    
    print(f"\nTotal de registros: {len(df):,}")
    print(f"Período: {df['NU_ANO'].min()} - {df['NU_ANO'].max()}")
    print(f"\nColunas disponíveis:\n{df.columns.tolist()}")
    
    # Análise de municípios
    print("\n" + "=" * 80)
    print("ANÁLISE DE MUNICÍPIOS DE RESIDÊNCIA")
    print("=" * 80)
    municipios = df['ID_MN_RESI'].value_counts()
    print(f"\nTotal de municípios diferentes: {len(municipios)}")
    print(f"\nDistribuição dos 10 municípios com mais casos:")
    print(municipios.head(10))
    
    return df

def filter_montes_claros(df):
    """Filtra apenas casos de residentes em Montes Claros"""
    print("\n" + "=" * 80)
    print("FILTRANDO MONTES CLAROS")
    print("=" * 80)
    
    # Código IBGE de Montes Claros: 3143302
    # Mas nos dados parece estar truncado como 314330
    cod_montes_claros = 314330
    
    df_mc = df[df['ID_MN_RESI'] == cod_montes_claros].copy()
    
    print(f"\nCódigo utilizado: {cod_montes_claros}")
    print(f"Casos filtrados: {len(df_mc):,} de {len(df):,} ({len(df_mc)/len(df)*100:.1f}%)")
    print(f"Período: {df_mc['NU_ANO'].min()} - {df_mc['NU_ANO'].max()}")
    
    # Estatísticas por ano
    print("\nCasos por ano:")
    print(df_mc['NU_ANO'].value_counts().sort_index())
    
    return df_mc

def analyze_health_units(df_mc):
    """Analisa as unidades de saúde para mapeamento posterior"""
    print("\n" + "=" * 80)
    print("ANÁLISE DE UNIDADES DE SAÚDE")
    print("=" * 80)
    
    unidades = df_mc['ID_UNIDADE'].value_counts()
    print(f"\nTotal de unidades diferentes: {len(unidades)}")
    print(f"\nTop 20 unidades com mais notificações:")
    print(unidades.head(20))
    
    # Salvar lista de unidades únicas para posterior mapeamento
    unidades_df = pd.DataFrame({
        'ID_UNIDADE': unidades.index,
        'TOTAL_CASOS': unidades.values
    })
    
    output_file = OUTPUT_DIR / "unidades_saude_montes_claros.csv"
    unidades_df.to_csv(output_file, index=False)
    print(f"\n✓ Lista de unidades salva em: {output_file}")
    
    return unidades_df

def save_filtered_data(df_mc):
    """Salva dados filtrados para próximas etapas"""
    print("\n" + "=" * 80)
    print("SALVANDO DADOS PROCESSADOS")
    print("=" * 80)
    
    # Converter data de notificação para datetime
    df_mc['DT_NOTIFIC'] = pd.to_datetime(df_mc['DT_NOTIFIC'], format='%d/%m/%Y')
    
    # Ordenar por data
    df_mc = df_mc.sort_values('DT_NOTIFIC')
    
    # Salvar dados filtrados
    output_file = OUTPUT_DIR / "sinan_montes_claros_filtrado.csv"
    df_mc.to_csv(output_file, index=False)
    print(f"\n✓ Dados filtrados salvos em: {output_file}")
    print(f"  Total de registros: {len(df_mc):,}")
    
    # Estatísticas descritivas
    print("\nResumo dos dados filtrados:")
    print(f"  Data mais antiga: {df_mc['DT_NOTIFIC'].min()}")
    print(f"  Data mais recente: {df_mc['DT_NOTIFIC'].max()}")
    print(f"  Idade média: {df_mc['IDADE_ANOS'].mean():.1f} anos")
    print(f"  % Sexo Feminino: {(df_mc['CS_SEXO'] == 'F').sum() / len(df_mc) * 100:.1f}%")
    
    return df_mc

def main():
    """Pipeline principal de tratamento de dados"""
    print("\n" + "=" * 80)
    print("TRATAMENTO DE DADOS - SINAN MONTES CLAROS")
    print("=" * 80)
    
    # 1. Carregar dados brutos
    df_raw = load_sinan_data()
    
    # 2. Filtrar Montes Claros
    df_mc = filter_montes_claros(df_raw)
    
    # 3. Analisar unidades de saúde
    unidades = analyze_health_units(df_mc)
    
    # 4. Salvar dados processados
    df_final = save_filtered_data(df_mc)
    
    print("\n" + "=" * 80)
    print("✓ PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
    print("=" * 80)
    print("\nPRÓXIMOS PASSOS:")
    print("1. Mapear ID_UNIDADE para coordenadas geográficas ou bairros")
    print("2. Carregar e processar dados meteorológicos (INMET)")
    print("3. Cruzar dados de precipitação com casos por período")
    print("4. Criar modelo preditivo com lag temporal")
    print("=" * 80)
    
    return df_final

if __name__ == "__main__":
    df = main()
