# 🦟 Análise Epidemiológica: Dengue x Precipitação

Projeto de análise de correlação temporal entre índice pluviométrico e casos de doenças transmitidas pelo *Aedes aegypti* (dengue, chikungunya, zika) em Montes Claros/MG.

**Hackathon 2026** | **Prazo**: Março 2026

---

## 📋 Descrição do Projeto

Este projeto analisa dados epidemiológicos de 2019-2023 para identificar:
- ✅ Correlação entre precipitação e aumento de casos de dengue
- ✅ Lag temporal ideal (período entre chuva e aumento de casos)
- ✅ Padrões sazonais e picos epidêmicos
- ✅ Tendências temporais e áreas de risco

### Objetivo
Criar um sistema de alerta precoce baseado em dados meteorológicos para apoiar ações preventivas da vigilância epidemiológica.

---

## 🗂️ Estrutura do Projeto

```
hackaton-ev26/
├── data/                          # Dados brutos
│   ├── SINAN_EIXO_2.csv          # Casos de dengue/chikungunya/zika
│   ├── INMET_EIXO_2.csv          # Dados meteorológicos
│   └── DESCRIÇÃO_EIXO_2.txt      # Dicionário de dados
│
├── src/                           # Scripts de análise
│   ├── main.py                    # Tratamento inicial de dados
│   ├── correlacao_temporal.py     # Análise de correlação com lag
│   ├── visualizacoes_apresentacao.py  # Gráficos para apresentação
│   └── run_all.py                 # Pipeline completo
│
├── output/                        # Resultados gerados
│   ├── *.csv                      # Dados processados
│   ├── *.png                      # Visualizações
│   └── RESUMO_EXECUTIVO.md        # Resumo dos achados
│
└── README.md                      # Este arquivo
```

---

## 🚀 Como Executar

### 1. Preparar ambiente

```bash
# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências (já instaladas)
pip install pandas numpy matplotlib seaborn
```

### 2. Executar análise completa

```bash
# Opção 1: Pipeline completo (recomendado)
python src/run_all.py

# Opção 2: Scripts individuais
python src/main.py                           # Tratamento de dados
python src/correlacao_temporal.py            # Análise de correlação
python src/visualizacoes_apresentacao.py     # Visualizações adicionais
```

### 3. Ver resultados

Os arquivos gerados estarão em `output/`:
- **Visualizações**: 6 arquivos PNG
- **Dados processados**: CSVs prontos para análise
- **Resumo executivo**: `RESUMO_EXECUTIVO.md`

---

## 📊 Principais Resultados

### Insights Principais

🔍 **Correlação Temporal Identificada**
- Lag ótimo: **6 semanas**
- Correlação (r): **0.122** (fraca positiva)
- Interpretação: Após períodos de chuva intensa, observa-se tendência de aumento de casos em ~6 semanas

📈 **Picos Epidêmicos**
- Precipitação 6 semanas antes dos picos: **26% maior** que períodos normais
- 25% das semanas analisadas apresentaram picos epidêmicos

🗓️ **Sazonalidade**
- Meses com mais casos: **Janeiro (778/sem)**, Fevereiro, Abril
- Meses com mais chuva: **Novembro, Fevereiro, Dezembro**
- Padrão: chuvas em Nov-Dez → picos em Jan-Mar

⚠️ **Tendência Preocupante**
- 2023: **27.280 casos** (recorde histórico)
- Aumento de **65,6%** em relação a 2019

### Visualizações Geradas

1. **infografico_resumo.png** - Painel completo (USE NA APRESENTAÇÃO)
2. **analise_picos_epidemicos.png** - Identificação de picos
3. **sazonalidade_mensal.png** - Padrões mensais
4. **comparacao_anual.png** - Evolução ano a ano
5. **correlacao_temporal_precipitacao_casos.png** - Análise detalhada de lag
6. **heatmap_semanal.png** - Densidade temporal

---

## 🔬 Metodologia

### Dados Utilizados

**SINAN (Sistema de Informação de Agravos de Notificação)**
- 79.778 casos em Montes Claros (2019-2023)
- 255 unidades de saúde notificadoras
- Dados agregados por semana epidemiológica

**INMET (Instituto Nacional de Meteorologia)**
- 43.824 registros meteorológicos
- Período: 2019-2023
- Variáveis: precipitação, temperatura

### Pipeline de Análise

```mermaid
graph LR
    A[Dados Brutos] --> B[Filtrar Montes Claros]
    B --> C[Agregar por Semana]
    C --> D[Análise de Lag 0-6 semanas]
    D --> E[Identificar Melhor Correlação]
    E --> F[Visualizações]
    F --> G[Insights]
```

### Justificativa do Lag (6 semanas)

O lag de 6 semanas corresponde ao ciclo epidemiológico:
1. Ovo → Adulto do mosquito: ~7-14 dias
2. Incubação do vírus no mosquito: 8-12 dias
3. Incubação no humano: 3-7 dias
4. Tempo até notificação: ~7 dias

**Total**: ~28-42 dias ≈ **4-6 semanas**

---

## 🎯 Recomendações

### Sistema de Alerta Proposto

```
SE precipitação > 30mm/semana por 2+ semanas consecutivas
   ENTÃO intensificar ações em 4-6 semanas:
      • Campanhas educativas
      • Vistorias domiciliares
      • Eliminação de criadouros
      • Reforço de estoque de inseticidas
```

### Calendário Preventivo

| Período | Ação |
|---------|------|
| **Out-Dez** | Intensificar campanhas (período chuvoso) |
| **Jan-Mar** | Máxima vigilância (pico de casos esperado) |
| **Abr-Jun** | Manutenção de ações |
| **Jul-Set** | Planejamento e preparação |

---

## 📦 Dependências

```
python >= 3.10
pandas
numpy
matplotlib
seaborn
```

---

## 📝 Próximos Passos

Para aprimorar a análise:

1. **Modelo Preditivo**
   - Implementar regressão linear/ARIMA
   - Validar com dados de 2024
   - Calcular métricas (R², MAE, RMSE)

2. **Análise Geoespacial**
   - Mapear unidades de saúde
   - Criar mapa de calor por bairro
   - Identificar áreas de maior risco

3. **Variáveis Adicionais**
   - Incluir temperatura e umidade
   - Dados sociodemográficos
   - Densidade populacional

4. **Dashboard Interativo**
   - Streamlit/Dash para visualização
   - Atualização em tempo real
   - Sistema de alerta automatizado

---

## 👥 Autor

Desenvolvido para o Hackathon 2026

---

## 📄 Licença

MIT License - Ver arquivo [LICENSE](LICENSE)

---

## 📚 Referências

- SINAN - Sistema de Informação de Agravos de Notificação
- INMET - Instituto Nacional de Meteorologia
- Literatura sobre ciclo de vida do Aedes aegypti
- Estudos de correlação clima-dengue

---

**⚠️ NOTA**: Este é um protótipo desenvolvido em ambiente de hackathon. Para uso em produção, são necessárias validações adicionais e acompanhamento de especialistas em epidemiologia.