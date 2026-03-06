"""
Visualizações Adicionais para Apresentação
Foco em impacto visual e insights claros
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configurações
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 11

# Diretórios
OUTPUT_DIR = Path(__file__).parent.parent / "output"

def load_consolidated_data():
    """Carrega dados já consolidados"""
    df = pd.read_csv(OUTPUT_DIR / "dados_consolidados_lag6sem.csv")
    df['data'] = pd.to_datetime(df['data'])
    return df

def plot_epidemic_peaks(df):
    """Identifica e visualiza picos epidêmicos vs precipitação"""
    print("=" * 80)
    print("ANÁLISE DE PICOS EPIDÊMICOS")
    print("=" * 80)
    
    # Identificar picos (acima do percentil 75)
    threshold = df['casos'].quantile(0.75)
    df['pico_epidemico'] = df['casos'] > threshold
    
    fig, axes = plt.subplots(3, 1, figsize=(16, 12))
    
    # 1. Casos com destaque para picos
    ax1 = axes[0]
    ax1.fill_between(df['data'], 0, df['casos'], where=df['pico_epidemico'], 
                      alpha=0.7, color='#E63946', label=f'Picos (> {threshold:.0f} casos)')
    ax1.fill_between(df['data'], 0, df['casos'], where=~df['pico_epidemico'], 
                      alpha=0.4, color='#457B9D', label='Normal')
    ax1.set_ylabel('Casos Semanais', fontsize=13, fontweight='bold')
    ax1.set_title('Identificação de Picos Epidêmicos', fontsize=15, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # 2. Precipitação (6 semanas antes dos casos)
    ax2 = axes[1]
    ax2.bar(df['data'], df['precipitacao_mm'], alpha=0.7, color='#2E86AB', width=5)
    ax2.axhline(y=df['precipitacao_mm'].quantile(0.75), color='red', linestyle='--', 
                label=f"75º percentil ({df['precipitacao_mm'].quantile(0.75):.1f} mm)", linewidth=2)
    ax2.set_ylabel('Precipitação (mm)', fontsize=13, fontweight='bold')
    ax2.set_title('Precipitação Semanal (com lag de 6 semanas)', fontsize=15, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    # 3. Comparação normalizada (0-1)
    ax3 = axes[2]
    df['casos_norm'] = (df['casos'] - df['casos'].min()) / (df['casos'].max() - df['casos'].min())
    df['precip_norm'] = (df['precipitacao_mm'] - df['precipitacao_mm'].min()) / (df['precipitacao_mm'].max() - df['precipitacao_mm'].min())
    
    ax3.plot(df['data'], df['casos_norm'], linewidth=3, color='#E63946', label='Casos (normalizado)', alpha=0.8)
    ax3.plot(df['data'], df['precip_norm'], linewidth=2, color='#2E86AB', label='Precipitação (normalizado)', alpha=0.7, linestyle='--')
    ax3.fill_between(df['data'], 0, 1, where=df['pico_epidemico'], alpha=0.1, color='red', label='Períodos de pico')
    ax3.set_xlabel('Data', fontsize=13, fontweight='bold')
    ax3.set_ylabel('Valor Normalizado (0-1)', fontsize=13, fontweight='bold')
    ax3.set_title('Comparação Normalizada: Precipitação vs Casos', fontsize=15, fontweight='bold')
    ax3.legend(fontsize=11)
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim([0, 1])
    
    plt.tight_layout()
    output_file = OUTPUT_DIR / "analise_picos_epidemicos.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Gráfico de picos salvos em: {output_file}")
    plt.close()
    
    # Estatísticas dos picos
    picos = df[df['pico_epidemico']]
    print(f"\nTotal de semanas com picos: {len(picos)} ({len(picos)/len(df)*100:.1f}%)")
    print(f"Média de casos em picos: {picos['casos'].mean():.0f}")
    print(f"Média de precipitação 6 semanas antes dos picos: {picos['precipitacao_mm'].mean():.1f} mm")
    
    normais = df[~df['pico_epidemico']]
    print(f"\nMédia de precipitação em períodos normais: {normais['precipitacao_mm'].mean():.1f} mm")
    print(f"Diferença: {((picos['precipitacao_mm'].mean() - normais['precipitacao_mm'].mean()) / normais['precipitacao_mm'].mean() * 100):.1f}%")

def plot_monthly_analysis(df):
    """Análise mensal para identificar sazonalidade"""
    print("\n" + "=" * 80)
    print("ANÁLISE MENSAL E SAZONALIDADE")
    print("=" * 80)
    
    # Adicionar mês
    df['mes'] = df['data'].dt.month
    df['nome_mes'] = df['data'].dt.strftime('%b')
    
    # Agregar por mês
    monthly = df.groupby('mes').agg({
        'casos': 'mean',
        'precipitacao_mm': 'mean'
    }).reset_index()
    
    meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Casos por mês
    ax1 = axes[0]
    bars1 = ax1.bar(monthly['mes'], monthly['casos'], alpha=0.8, color='#E63946', edgecolor='black', linewidth=1.5)
    ax1.set_xticks(range(1, 13))
    ax1.set_xticklabels(meses_nomes)
    ax1.set_ylabel('Casos Médios por Semana', fontsize=13, fontweight='bold')
    ax1.set_title('Sazonalidade: Casos Médios por Mês', fontsize=15, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Adicionar valores nas barras
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.0f}',
                ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # Precipitação por mês
    ax2 = axes[1]
    bars2 = ax2.bar(monthly['mes'], monthly['precipitacao_mm'], alpha=0.8, color='#2E86AB', edgecolor='black', linewidth=1.5)
    ax2.set_xticks(range(1, 13))
    ax2.set_xticklabels(meses_nomes)
    ax2.set_xlabel('Mês', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Precipitação Média (mm)', fontsize=13, fontweight='bold')
    ax2.set_title('Sazonalidade: Precipitação Média por Mês', fontsize=15, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Adicionar valores nas barras
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    plt.tight_layout()
    output_file = OUTPUT_DIR / "sazonalidade_mensal.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Gráfico de sazonalidade salvo em: {output_file}")
    plt.close()
    
    # Identificar meses de maior risco
    print(f"\nMeses com MAIS casos:")
    top_casos = monthly.nlargest(3, 'casos')
    for _, row in top_casos.iterrows():
        print(f"  {meses_nomes[int(row['mes'])-1]}: {row['casos']:.0f} casos/semana (média)")
    
    print(f"\nMeses com MAIS chuva:")
    top_precip = monthly.nlargest(3, 'precipitacao_mm')
    for _, row in top_precip.iterrows():
        print(f"  {meses_nomes[int(row['mes'])-1]}: {row['precipitacao_mm']:.1f} mm/semana (média)")

def plot_year_comparison(df):
    """Comparação detalhada entre anos"""
    print("\n" + "=" * 80)
    print("COMPARAÇÃO ENTRE ANOS")
    print("=" * 80)
    
    # Agregar por ano
    yearly = df.groupby('ano').agg({
        'casos': 'sum',
        'precipitacao_mm': 'sum'
    }).reset_index()
    
    # Filtrar anos principais (2019-2023)
    yearly = yearly[(yearly['ano'] >= 2019) & (yearly['ano'] <= 2023)]
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Total de casos por ano
    ax1 = axes[0]
    bars = ax1.bar(yearly['ano'].astype(str), yearly['casos'], 
                   color=['#457B9D', '#457B9D', '#457B9D', '#457B9D', '#E63946'],
                   alpha=0.8, edgecolor='black', linewidth=2)
    ax1.set_xlabel('Ano', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Total de Casos', fontsize=13, fontweight='bold')
    ax1.set_title('Total de Casos por Ano', fontsize=15, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Adicionar valores
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    # Precipitação total por ano
    ax2 = axes[1]
    bars2 = ax2.bar(yearly['ano'].astype(str), yearly['precipitacao_mm'], 
                    color='#2E86AB', alpha=0.8, edgecolor='black', linewidth=2)
    ax2.set_xlabel('Ano', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Precipitação Total (mm)', fontsize=13, fontweight='bold')
    ax2.set_title('Precipitação Total por Ano', fontsize=15, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Adicionar valores
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.0f}',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    plt.tight_layout()
    output_file = OUTPUT_DIR / "comparacao_anual.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Gráfico de comparação anual salvo em: {output_file}")
    plt.close()
    
    # Estatísticas
    print("\nResumo anual:")
    for _, row in yearly.iterrows():
        print(f"  {int(row['ano'])}: {int(row['casos']):,} casos | {row['precipitacao_mm']:.0f} mm de chuva")
    
    print(f"\nAumento de 2019 para 2023: {((yearly[yearly['ano']==2023]['casos'].values[0] / yearly[yearly['ano']==2019]['casos'].values[0] - 1) * 100):.1f}%")

def create_summary_infographic(df):
    """Cria infográfico resumido com estatísticas principais"""
    print("\n" + "=" * 80)
    print("GERANDO INFOGRÁFICO RESUMO")
    print("=" * 80)
    
    # Calcular estatísticas
    total_casos = df['casos'].sum()
    total_semanas = len(df)
    media_casos = df['casos'].mean()
    max_casos = df['casos'].max()
    semana_max = df[df['casos'] == max_casos]['data'].values[0]
    
    # Correlação
    corr = df['precipitacao_mm'].corr(df['casos'])
    
    fig = plt.figure(figsize=(16, 10))
    
    # Criar layout com GridSpec
    from matplotlib.gridspec import GridSpec
    gs = GridSpec(3, 3, figure=fig, hspace=0.4, wspace=0.3)
    
    # Título principal
    fig.suptitle('ANÁLISE EPIDEMIOLÓGICA: DENGUE X PRECIPITAÇÃO\nMontes Claros/MG (2019-2023)', 
                 fontsize=18, fontweight='bold', y=0.98)
    
    # Box 1: Total de casos
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.text(0.5, 0.6, f'{int(total_casos):,}', ha='center', va='center', 
             fontsize=40, fontweight='bold', color='#E63946')
    ax1.text(0.5, 0.3, 'Total de Casos', ha='center', va='center', 
             fontsize=14, fontweight='bold')
    ax1.text(0.5, 0.1, f'({total_semanas} semanas)', ha='center', va='center', 
             fontsize=11, style='italic', color='gray')
    ax1.axis('off')
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    
    # Box 2: Média semanal
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.text(0.5, 0.6, f'{media_casos:.0f}', ha='center', va='center', 
             fontsize=40, fontweight='bold', color='#457B9D')
    ax2.text(0.5, 0.3, 'Média Semanal', ha='center', va='center', 
             fontsize=14, fontweight='bold')
    ax2.text(0.5, 0.1, 'casos por semana', ha='center', va='center', 
             fontsize=11, style='italic', color='gray')
    ax2.axis('off')
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    
    # Box 3: Pico máximo
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.text(0.5, 0.6, f'{int(max_casos):,}', ha='center', va='center', 
             fontsize=40, fontweight='bold', color='#E63946')
    ax3.text(0.5, 0.3, 'Pico Máximo', ha='center', va='center', 
             fontsize=14, fontweight='bold')
    ax3.text(0.5, 0.1, pd.to_datetime(semana_max).strftime('%d/%m/%Y'), 
             ha='center', va='center', fontsize=11, style='italic', color='gray')
    ax3.axis('off')
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    
    # Gráfico principal: Série temporal
    ax4 = fig.add_subplot(gs[1:, :])
    ax4_twin = ax4.twinx()
    
    # Precipitação em barras
    ax4.bar(df['data'], df['precipitacao_mm'], alpha=0.5, color='#2E86AB', 
            label='Precipitação (mm)', width=5)
    
    # Casos em linha
    ax4_twin.plot(df['data'], df['casos'], color='#E63946', linewidth=3, 
                  label='Casos', marker='o', markersize=4, markevery=10)
    ax4_twin.fill_between(df['data'], 0, df['casos'], alpha=0.2, color='#E63946')
    
    ax4.set_xlabel('Data', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Precipitação (mm)', fontsize=14, fontweight='bold', color='#2E86AB')
    ax4_twin.set_ylabel('Casos', fontsize=14, fontweight='bold', color='#E63946')
    ax4.set_title(f'Correlação Temporal (Lag: 6 semanas | r = {corr:.3f})', 
                  fontsize=15, fontweight='bold', pad=20)
    
    ax4.tick_params(axis='y', labelcolor='#2E86AB', labelsize=11)
    ax4_twin.tick_params(axis='y', labelcolor='#E63946', labelsize=11)
    ax4.tick_params(axis='x', labelsize=10, rotation=45)
    
    # Legendas
    lines1, labels1 = ax4.get_legend_handles_labels()
    lines2, labels2 = ax4_twin.get_legend_handles_labels()
    ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=12)
    
    ax4.grid(True, alpha=0.3)
    
    # Adicionar texto com insight
    insight_text = (
        f"INSIGHT: Após períodos de alta precipitação, observa-se aumento nos casos\n"
        f"de doenças do Aedes aegypti após aproximadamente 6 semanas.\n"
        f"Este lag temporal corresponde ao ciclo reprodutivo do mosquito."
    )
    fig.text(0.5, 0.02, insight_text, ha='center', fontsize=11, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
             style='italic')
    
    plt.tight_layout(rect=[0, 0.06, 1, 0.96])
    output_file = OUTPUT_DIR / "infografico_resumo.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Infográfico resumo salvo em: {output_file}")
    plt.close()

def main():
    """Executa todas as visualizações adicionais"""
    print("\n" + "=" * 80)
    print("GERANDO VISUALIZAÇÕES PARA APRESENTAÇÃO")
    print("=" * 80)
    
    # Carregar dados
    df = load_consolidated_data()
    
    # Gerar visualizações
    plot_epidemic_peaks(df)
    plot_monthly_analysis(df)
    plot_year_comparison(df)
    create_summary_infographic(df)
    
    print("\n" + "=" * 80)
    print("✓ TODAS AS VISUALIZAÇÕES FORAM GERADAS COM SUCESSO!")
    print("=" * 80)
    print("\nArquivos gerados em output/:")
    print("  1. correlacao_temporal_precipitacao_casos.png")
    print("  2. heatmap_semanal.png")
    print("  3. analise_picos_epidemicos.png")
    print("  4. sazonalidade_mensal.png")
    print("  5. comparacao_anual.png")
    print("  6. infografico_resumo.png")
    print("=" * 80)

if __name__ == "__main__":
    main()
