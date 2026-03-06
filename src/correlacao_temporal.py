"""
Análise de Correlação Temporal: Precipitação x Casos de Doenças do Aedes
Com análise de lag temporal (2-4 semanas)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import timedelta
import warnings
warnings.filterwarnings('ignore')

# Configurações
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 10

# Diretórios
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def load_inmet_data():
    """Carrega e processa dados meteorológicos do INMET"""
    print("=" * 80)
    print("CARREGANDO DADOS METEOROLÓGICOS (INMET)")
    print("=" * 80)
    
    # Método robusto: ler linha por linha
    print("Lendo arquivo linha por linha...")
    data = []
    
    with open(DATA_DIR / "INMET_EIXO_2.csv", 'r', encoding='utf-8-sig') as f:
        # Ler cabeçalho
        header_line = f.readline().strip()
        # Remover BOM e aspas, depois dividir por ponto-e-vírgula
        header_line = header_line.replace('\ufeff', '').replace('"', '')
        headers = [h.strip() for h in header_line.split(';')]
        
        print(f"Cabeçalhos encontrados: {headers[:5]}...")
        
        # Ler dados
        line_count = 0
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Remover todas as aspas e dividir por ponto-e-vírgula
            parts = [p.strip() for p in line.replace('"', '').split(';')]
            
            if len(parts) == len(headers):
                data.append(parts)
                line_count += 1
            elif line_count < 10:  # Debug nas primeiras linhas
                print(f"AVISO: Linha {line_count} com {len(parts)} campos (esperado {len(headers)})")
    
    df = pd.DataFrame(data, columns=headers)
    print(f"✓ Carregadas {len(df):,} linhas")
    
    # Converter data
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
    
    # Converter chuva e temperatura (trocar vírgula por ponto)
    df['Chuva (mm)'] = df['Chuva (mm)'].str.replace(',', '.').replace('', '0')
    df['Chuva (mm)'] = pd.to_numeric(df['Chuva (mm)'], errors='coerce').fillna(0)
    
    df['Temp. Ins. (C)'] = df['Temp. Ins. (C)'].str.replace(',', '.')
    df['Temp. Ins. (C)'] = pd.to_numeric(df['Temp. Ins. (C)'], errors='coerce')
    
    # Remover linhas com data inválida
    df = df.dropna(subset=['Data'])
    
    print(f"✓ Total de registros válidos: {len(df):,}")
    print(f"✓ Período: {df['Data'].min()} a {df['Data'].max()}")
    
    return df

def aggregate_weather_daily(df_inmet):
    """Agrega dados meteorológicos por dia"""
    print("\n" + "=" * 80)
    print("AGREGANDO DADOS METEOROLÓGICOS POR DIA")
    print("=" * 80)
    
    # Agregar por dia
    df_daily = df_inmet.groupby('Data').agg({
        'Chuva (mm)': 'sum',  # Soma total de chuva no dia
        'Temp. Ins. (C)': 'mean',  # Temperatura média do dia
    }).reset_index()
    
    df_daily.columns = ['data', 'precipitacao_mm', 'temperatura_media']
    
    print(f"\nDias com dados: {len(df_daily):,}")
    print(f"Período: {df_daily['data'].min()} a {df_daily['data'].max()}")
    print(f"\nEstatísticas de precipitação diária:")
    print(df_daily['precipitacao_mm'].describe())
    
    return df_daily

def aggregate_weather_weekly(df_daily):
    """Agrega dados meteorológicos por semana epidemiológica"""
    print("\n" + "=" * 80)
    print("AGREGANDO DADOS POR SEMANA EPIDEMIOLÓGICA")
    print("=" * 80)
    
    # Adicionar semana epidemiológica
    df_daily['ano'] = df_daily['data'].dt.year
    df_daily['semana_epi'] = df_daily['data'].dt.isocalendar().week
    
    # Agregar por semana
    df_weekly = df_daily.groupby(['ano', 'semana_epi']).agg({
        'data': 'min',  # Primeira data da semana
        'precipitacao_mm': 'sum',  # Total de chuva na semana
        'temperatura_media': 'mean'  # Temperatura média da semana
    }).reset_index()
    
    # Criar identificador único de semana
    df_weekly['ano_semana'] = df_weekly['ano'].astype(str) + '_S' + df_weekly['semana_epi'].astype(str).str.zfill(2)
    
    print(f"\nSemanas com dados: {len(df_weekly):,}")
    print(f"Período: {df_weekly['ano'].min()}-S{df_weekly['semana_epi'].min():02d} a {df_weekly['ano'].max()}-S{df_weekly['semana_epi'].max():02d}")
    print(f"\nEstatísticas de precipitação semanal:")
    print(df_weekly['precipitacao_mm'].describe())
    
    return df_weekly

def load_cases_data():
    """Carrega dados de casos já filtrados"""
    print("\n" + "=" * 80)
    print("CARREGANDO DADOS DE CASOS")
    print("=" * 80)
    
    df = pd.read_csv(OUTPUT_DIR / "sinan_montes_claros_filtrado.csv")
    df['DT_NOTIFIC'] = pd.to_datetime(df['DT_NOTIFIC'])
    
    print(f"\nTotal de casos: {len(df):,}")
    print(f"Período: {df['DT_NOTIFIC'].min()} a {df['DT_NOTIFIC'].max()}")
    
    return df

def aggregate_cases_weekly(df_cases):
    """Agrega casos por semana epidemiológica"""
    print("\n" + "=" * 80)
    print("AGREGANDO CASOS POR SEMANA")
    print("=" * 80)
    
    # Adicionar semana epidemiológica
    df_cases['ano'] = df_cases['DT_NOTIFIC'].dt.year
    df_cases['semana_epi'] = df_cases['DT_NOTIFIC'].dt.isocalendar().week
    
    # Contar casos por semana
    df_weekly = df_cases.groupby(['ano', 'semana_epi']).size().reset_index(name='casos')
    
    # Criar identificador único
    df_weekly['ano_semana'] = df_weekly['ano'].astype(str) + '_S' + df_weekly['semana_epi'].astype(str).str.zfill(2)
    
    print(f"\nSemanas com casos: {len(df_weekly):,}")
    print(f"Total de casos: {df_weekly['casos'].sum():,}")
    print(f"\nEstatísticas de casos semanais:")
    print(df_weekly['casos'].describe())
    
    return df_weekly

def merge_data_with_lag(df_weather, df_cases, lag_weeks=0):
    """Cruza dados de clima e casos com lag temporal"""
    # Fazer cópia para não modificar original
    df_w = df_weather.copy()
    df_c = df_cases.copy()
    
    # Se houver lag, ajustar as semanas dos casos
    if lag_weeks > 0:
        # Criar coluna de data aproximada para facilitar o shift
        df_c['data_ref'] = pd.to_datetime(df_c['ano'].astype(str) + '-W' + df_c['semana_epi'].astype(str) + '-1', format='%Y-W%W-%w')
        df_c['data_ref'] = df_c['data_ref'] - timedelta(weeks=lag_weeks)
        df_c['ano'] = df_c['data_ref'].dt.year
        df_c['semana_epi'] = df_c['data_ref'].dt.isocalendar().week
        df_c['ano_semana'] = df_c['ano'].astype(str) + '_S' + df_c['semana_epi'].astype(str).str.zfill(2)
    
    # Merge
    df_merged = pd.merge(
        df_w[['ano', 'semana_epi', 'ano_semana', 'data', 'precipitacao_mm', 'temperatura_media']],
        df_c[['ano_semana', 'casos']],
        on='ano_semana',
        how='left'
    )
    
    # Preencher semanas sem casos com 0
    df_merged['casos'] = df_merged['casos'].fillna(0)
    
    return df_merged

def calculate_correlation(df_merged):
    """Calcula correlação entre precipitação e casos"""
    corr_precip = df_merged['precipitacao_mm'].corr(df_merged['casos'])
    corr_temp = df_merged['temperatura_media'].corr(df_merged['casos'])
    
    return corr_precip, corr_temp

def plot_correlation_analysis(df_weather, df_cases):
    """Gera gráficos de correlação com diferentes lags"""
    print("\n" + "=" * 80)
    print("GERANDO GRÁFICOS DE CORRELAÇÃO")
    print("=" * 80)
    
    # Testar diferentes lags (0 a 6 semanas)
    lags = range(0, 7)
    correlations_precip = []
    correlations_temp = []
    
    print("\nCalculando correlações para diferentes lags...")
    for lag in lags:
        df_merged = merge_data_with_lag(df_weather, df_cases, lag)
        corr_p, corr_t = calculate_correlation(df_merged)
        correlations_precip.append(corr_p)
        correlations_temp.append(corr_t)
        print(f"  Lag {lag} semanas: Precipitação={corr_p:.3f}, Temperatura={corr_t:.3f}")
    
    # Encontrar melhor lag
    best_lag = lags[np.argmax(correlations_precip)]
    best_corr = max(correlations_precip)
    
    print(f"\n✓ Melhor correlação: lag de {best_lag} semanas (r={best_corr:.3f})")
    
    # Criar figura com múltiplos gráficos
    fig = plt.figure(figsize=(18, 12))
    
    # 1. Gráfico de correlação vs lag
    ax1 = plt.subplot(3, 2, 1)
    ax1.plot(lags, correlations_precip, 'o-', linewidth=2, markersize=8, label='Precipitação', color='#2E86AB')
    ax1.plot(lags, correlations_temp, 's-', linewidth=2, markersize=8, label='Temperatura', color='#A23B72')
    ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax1.axvline(x=best_lag, color='red', linestyle='--', alpha=0.5, label=f'Melhor lag: {best_lag}sem')
    ax1.set_xlabel('Lag (semanas)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Correlação (r)', fontsize=12, fontweight='bold')
    ax1.set_title('Correlação vs Lag Temporal', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Série temporal comparativa (sem lag)
    df_merged_0 = merge_data_with_lag(df_weather, df_cases, 0)
    df_merged_0 = df_merged_0.sort_values('data')
    
    ax2 = plt.subplot(3, 2, 2)
    ax2_twin = ax2.twinx()
    
    ax2.bar(df_merged_0['data'], df_merged_0['precipitacao_mm'], alpha=0.6, color='#2E86AB', label='Precipitação (mm)')
    ax2_twin.plot(df_merged_0['data'], df_merged_0['casos'], color='#E63946', linewidth=2, label='Casos', marker='o', markersize=3)
    
    ax2.set_xlabel('Data', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Precipitação (mm)', fontsize=12, fontweight='bold', color='#2E86AB')
    ax2_twin.set_ylabel('Casos', fontsize=12, fontweight='bold', color='#E63946')
    ax2.set_title('Série Temporal: Precipitação vs Casos (sem lag)', fontsize=14, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='#2E86AB')
    ax2_twin.tick_params(axis='y', labelcolor='#E63946')
    ax2.legend(loc='upper left')
    ax2_twin.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 3. Série temporal com melhor lag
    df_merged_best = merge_data_with_lag(df_weather, df_cases, best_lag)
    df_merged_best = df_merged_best.sort_values('data')
    
    ax3 = plt.subplot(3, 2, 3)
    ax3_twin = ax3.twinx()
    
    ax3.bar(df_merged_best['data'], df_merged_best['precipitacao_mm'], alpha=0.6, color='#2E86AB', label='Precipitação (mm)')
    ax3_twin.plot(df_merged_best['data'], df_merged_best['casos'], color='#E63946', linewidth=2, label='Casos', marker='o', markersize=3)
    
    ax3.set_xlabel('Data', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Precipitação (mm)', fontsize=12, fontweight='bold', color='#2E86AB')
    ax3_twin.set_ylabel('Casos', fontsize=12, fontweight='bold', color='#E63946')
    ax3.set_title(f'Série Temporal com Lag Ótimo ({best_lag} semanas) - r={best_corr:.3f}', fontsize=14, fontweight='bold')
    ax3.tick_params(axis='y', labelcolor='#2E86AB')
    ax3_twin.tick_params(axis='y', labelcolor='#E63946')
    ax3.legend(loc='upper left')
    ax3_twin.legend(loc='upper right')
    ax3.grid(True, alpha=0.3)
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 4. Scatter plot (melhor lag)
    ax4 = plt.subplot(3, 2, 4)
    scatter = ax4.scatter(df_merged_best['precipitacao_mm'], df_merged_best['casos'], 
                          c=df_merged_best['ano'], cmap='viridis', alpha=0.6, s=100, edgecolors='black', linewidth=0.5)
    
    # Linha de tendência
    z = np.polyfit(df_merged_best['precipitacao_mm'], df_merged_best['casos'], 1)
    p = np.poly1d(z)
    ax4.plot(df_merged_best['precipitacao_mm'].sort_values(), p(df_merged_best['precipitacao_mm'].sort_values()), 
             "r--", linewidth=2, label=f'Tendência (r={best_corr:.3f})')
    
    ax4.set_xlabel('Precipitação (mm/semana)', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Casos (semana)', fontsize=12, fontweight='bold')
    ax4.set_title(f'Dispersão: Precipitação vs Casos (lag {best_lag} semanas)', fontsize=14, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax4, label='Ano')
    
    # 5. Análise por ano (melhor lag)
    ax5 = plt.subplot(3, 2, 5)
    for ano in sorted(df_merged_best['ano'].unique()):
        if ano >= 2019 and ano <= 2023:  # Foco nos anos principais
            df_ano = df_merged_best[df_merged_best['ano'] == ano].sort_values('semana_epi')
            ax5.plot(df_ano['semana_epi'], df_ano['casos'], marker='o', linewidth=2, label=str(int(ano)), markersize=4)
    
    ax5.set_xlabel('Semana Epidemiológica', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Casos', fontsize=12, fontweight='bold')
    ax5.set_title('Casos por Semana - Comparação Anual', fontsize=14, fontweight='bold')
    ax5.legend(title='Ano')
    ax5.grid(True, alpha=0.3)
    
    # 6. Precipitação por ano
    ax6 = plt.subplot(3, 2, 6)
    for ano in sorted(df_merged_best['ano'].unique()):
        if ano >= 2019 and ano <= 2023:
            df_ano = df_merged_best[df_merged_best['ano'] == ano].sort_values('semana_epi')
            ax6.plot(df_ano['semana_epi'], df_ano['precipitacao_mm'], marker='s', linewidth=2, label=str(int(ano)), markersize=4, alpha=0.7)
    
    ax6.set_xlabel('Semana Epidemiológica', fontsize=12, fontweight='bold')
    ax6.set_ylabel('Precipitação (mm)', fontsize=12, fontweight='bold')
    ax6.set_title('Precipitação por Semana - Comparação Anual', fontsize=14, fontweight='bold')
    ax6.legend(title='Ano')
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Salvar
    output_file = OUTPUT_DIR / "correlacao_temporal_precipitacao_casos.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Gráfico salvo em: {output_file}")
    plt.close()
    
    return best_lag, best_corr, df_merged_best

def plot_heatmap_analysis(df_merged_best):
    """Gera mapa de calor semanal"""
    print("\n" + "=" * 80)
    print("GERANDO MAPA DE CALOR SEMANAL")
    print("=" * 80)
    
    # Preparar dados em formato de matriz (ano x semana)
    pivot_casos = df_merged_best.pivot_table(values='casos', index='ano', columns='semana_epi', fill_value=0)
    pivot_precip = df_merged_best.pivot_table(values='precipitacao_mm', index='ano', columns='semana_epi', fill_value=0)
    
    # Criar figura
    fig, axes = plt.subplots(2, 1, figsize=(20, 10))
    
    # Mapa de calor - Casos
    sns.heatmap(pivot_casos, annot=False, cmap='YlOrRd', cbar_kws={'label': 'Casos'}, 
                ax=axes[0], linewidths=0.5, linecolor='white')
    axes[0].set_title('Mapa de Calor: Casos por Semana Epidemiológica', fontsize=16, fontweight='bold')
    axes[0].set_xlabel('Semana Epidemiológica', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Ano', fontsize=12, fontweight='bold')
    
    # Mapa de calor - Precipitação
    sns.heatmap(pivot_precip, annot=False, cmap='Blues', cbar_kws={'label': 'Precipitação (mm)'}, 
                ax=axes[1], linewidths=0.5, linecolor='white')
    axes[1].set_title('Mapa de Calor: Precipitação por Semana Epidemiológica', fontsize=16, fontweight='bold')
    axes[1].set_xlabel('Semana Epidemiológica', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Ano', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    
    output_file = OUTPUT_DIR / "heatmap_semanal.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Mapa de calor salvo em: {output_file}")
    plt.close()

def save_merged_data(df_merged, best_lag):
    """Salva dados consolidados para uso no modelo"""
    output_file = OUTPUT_DIR / f"dados_consolidados_lag{best_lag}sem.csv"
    df_merged.to_csv(output_file, index=False)
    print(f"\n✓ Dados consolidados salvos em: {output_file}")

def main():
    """Pipeline principal de análise de correlação"""
    print("\n" + "=" * 80)
    print("ANÁLISE DE CORRELAÇÃO TEMPORAL: PRECIPITAÇÃO x CASOS")
    print("=" * 80)
    
    # 1. Carregar dados meteorológicos
    df_inmet = load_inmet_data()
    
    # 2. Agregar dados meteorológicos
    df_weather_daily = aggregate_weather_daily(df_inmet)
    df_weather_weekly = aggregate_weather_weekly(df_weather_daily)
    
    # 3. Carregar dados de casos
    df_cases_raw = load_cases_data()
    
    # 4. Agregar casos por semana
    df_cases_weekly = aggregate_cases_weekly(df_cases_raw)
    
    # 5. Análise de correlação com gráficos
    best_lag, best_corr, df_merged_best = plot_correlation_analysis(df_weather_weekly, df_cases_weekly)
    
    # 6. Gerar mapas de calor
    plot_heatmap_analysis(df_merged_best)
    
    # 7. Salvar dados consolidados
    save_merged_data(df_merged_best, best_lag)
    
    print("\n" + "=" * 80)
    print("✓ ANÁLISE DE CORRELAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 80)
    print(f"\nRESULTADOS PRINCIPAIS:")
    print(f"  • Melhor lag temporal: {best_lag} semanas")
    print(f"  • Correlação (Precipitação vs Casos): r = {best_corr:.3f}")
    print(f"\nINTERPRETAÇÃO:")
    if best_corr > 0.5:
        print(f"  • Correlação FORTE positiva detectada!")
    elif best_corr > 0.3:
        print(f"  • Correlação MODERADA positiva detectada")
    elif best_corr > 0.1:
        print(f"  • Correlação FRACA positiva detectada")
    else:
        print(f"  • Correlação muito fraca ou inexistente")
    
    print(f"\n  Isso significa que após {best_lag} semanas de chuva,")
    print(f"  observa-se aumento nos casos de doenças do Aedes aegypti.")
    print("=" * 80)
    
    return df_merged_best, best_lag

if __name__ == "__main__":
    df, lag = main()
