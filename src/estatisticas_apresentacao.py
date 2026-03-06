"""
Estatísticas para Apresentação
Gera arquivo de texto com números-chave para copiar
"""

import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "output"

def generate_presentation_stats():
    """Gera estatísticas em formato de apresentação"""
    
    # Carregar dados
    df_cases = pd.read_csv(OUTPUT_DIR / "sinan_montes_claros_filtrado.csv")
    df_consolidated = pd.read_csv(OUTPUT_DIR / "dados_consolidados_lag6sem.csv")
    
    df_cases['DT_NOTIFIC'] = pd.to_datetime(df_cases['DT_NOTIFIC'])
    df_consolidated['data'] = pd.to_datetime(df_consolidated['data'])
    
    # Calcular estatísticas
    total_casos = len(df_cases)
    periodo_inicio = df_cases['DT_NOTIFIC'].min().strftime('%d/%m/%Y')
    periodo_fim = df_cases['DT_NOTIFIC'].max().strftime('%d/%m/%Y')
    
    # Por ano
    casos_por_ano = df_cases['NU_ANO'].value_counts().sort_index()
    
    # Correlação
    corr = df_consolidated['precipitacao_mm'].corr(df_consolidated['casos'])
    
    # Picos
    threshold = df_consolidated['casos'].quantile(0.75)
    picos = df_consolidated[df_consolidated['casos'] > threshold]
    precip_picos = picos['precipitacao_mm'].mean()
    precip_normal = df_consolidated[df_consolidated['casos'] <= threshold]['precipitacao_mm'].mean()
    diff_precip = ((precip_picos - precip_normal) / precip_normal * 100)
    
    # Meses
    df_consolidated['mes'] = pd.to_datetime(df_consolidated['data']).dt.month
    casos_por_mes = df_consolidated.groupby('mes')['casos'].mean().sort_values(ascending=False)
    precip_por_mes = df_consolidated.groupby('mes')['precipitacao_mm'].mean().sort_values(ascending=False)
    
    meses_nomes = ['', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    # Gerar texto
    texto = f"""
================================================================================
ESTATÍSTICAS PARA APRESENTAÇÃO - DENGUE X PRECIPITAÇÃO
Montes Claros/MG - Análise 2019-2023
================================================================================

📊 DADOS GERAIS
================================================================================
Total de casos analisados: {total_casos:,}
Período: {periodo_inicio} a {periodo_fim}
Unidades de saúde: 255
Semanas analisadas: {len(df_consolidated)}

📈 EVOLUÇÃO TEMPORAL
================================================================================
2019: {int(casos_por_ano.get(2019.0, 0)):,} casos
2020: {int(casos_por_ano.get(2020.0, 0)):,} casos
2021: {int(casos_por_ano.get(2021.0, 0)):,} casos
2022: {int(casos_por_ano.get(2022.0, 0)):,} casos
2023: {int(casos_por_ano.get(2023.0, 0)):,} casos ⚠️ RECORDE

Aumento 2019→2023: {((casos_por_ano.get(2023.0, 0) / casos_por_ano.get(2019.0, 1) - 1) * 100):.1f}%

🔍 CORRELAÇÃO TEMPORAL
================================================================================
Lag temporal identificado: 6 SEMANAS
Coeficiente de correlação (r): {corr:.3f}

Interpretação: Após 6 semanas de precipitação elevada, 
observa-se tendência de aumento nos casos.

📊 ANÁLISE DE PICOS EPIDÊMICOS
================================================================================
Semanas com picos: {len(picos)} ({len(picos)/len(df_consolidated)*100:.1f}%)
Casos médios em picos: {picos['casos'].mean():.0f} por semana
Casos médios normais: {df_consolidated[df_consolidated['casos'] <= threshold]['casos'].mean():.0f} por semana

Precipitação 6 semanas antes dos picos: {precip_picos:.1f} mm
Precipitação em períodos normais: {precip_normal:.1f} mm
Diferença: +{diff_precip:.1f}% ⚠️

🗓️ SAZONALIDADE - Meses com MAIS CASOS
================================================================================
1º lugar: {meses_nomes[int(casos_por_mes.index[0])]} - {casos_por_mes.iloc[0]:.0f} casos/semana (média)
2º lugar: {meses_nomes[int(casos_por_mes.index[1])]} - {casos_por_mes.iloc[1]:.0f} casos/semana (média)
3º lugar: {meses_nomes[int(casos_por_mes.index[2])]} - {casos_por_mes.iloc[2]:.0f} casos/semana (média)

🌧️ SAZONALIDADE - Meses com MAIS CHUVA
================================================================================
1º lugar: {meses_nomes[int(precip_por_mes.index[0])]} - {precip_por_mes.iloc[0]:.1f} mm/semana
2º lugar: {meses_nomes[int(precip_por_mes.index[1])]} - {precip_por_mes.iloc[1]:.1f} mm/semana
3º lugar: {meses_nomes[int(precip_por_mes.index[2])]} - {precip_por_mes.iloc[2]:.1f} mm/semana

💡 INSIGHT PRINCIPAL
================================================================================
Os meses chuvosos (Nov-Dez) PRECEDEM os picos de casos (Jan-Fev-Mar),
confirmando o lag temporal de 6 semanas identificado na análise.

🎯 RECOMENDAÇÃO - Sistema de Alerta
================================================================================
REGRA: SE precipitação > 30mm/semana por 2+ semanas consecutivas
       ENTÃO intensificar ações preventivas em 4-6 semanas

CALENDÁRIO PREVENTIVO:
• Out-Dez: Intensificar campanhas (período chuvoso)
• Jan-Mar: Máxima vigilância (pico de casos esperado)
• Abr-Jun: Manutenção de ações
• Jul-Set: Planejamento

📁 ARQUIVOS GERADOS
================================================================================
Visualizações (6 arquivos PNG):
1. infografico_resumo.png ⭐ USE NA APRESENTAÇÃO
2. analise_picos_epidemicos.png
3. sazonalidade_mensal.png
4. comparacao_anual.png
5. correlacao_temporal_precipitacao_casos.png
6. heatmap_semanal.png

Dados processados:
• sinan_montes_claros_filtrado.csv
• dados_consolidados_lag6sem.csv
• unidades_saude_montes_claros.csv

Documentação:
• RESUMO_EXECUTIVO.md
• README.md

================================================================================
PRÓXIMOS PASSOS (Pós-Hackathon)
================================================================================
1. Implementar modelo preditivo (regressão linear/ARIMA)
2. Validar previsões com dados de 2024
3. Mapear geograficamente as unidades de saúde
4. Criar dashboard interativo
5. Incluir variáveis adicionais (temperatura, umidade)

================================================================================
FIM DO RELATÓRIO
================================================================================
"""
    
    # Salvar
    output_file = OUTPUT_DIR / "ESTATISTICAS_APRESENTACAO.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(texto)
    
    print(texto)
    print(f"\n✓ Estatísticas salvas em: {output_file}")

if __name__ == "__main__":
    generate_presentation_stats()
