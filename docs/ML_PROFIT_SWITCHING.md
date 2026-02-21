# Módulo de Machine Learning — Profit-Switching Inteligente

**Autor:** HyperMine Core Team  
**Versão:** 1.0  
**Data:** Fevereiro 2026

---

## Sumário

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema ML](#arquitetura-do-sistema-ml)
3. [Pipeline de Dados](#pipeline-de-dados)
4. [Modelos de Machine Learning](#modelos-de-machine-learning)
5. [Feature Engineering](#feature-engineering)
6. [Decision Engine com Hysteresis](#decision-engine-com-hysteresis)
7. [APIs de Dados Utilizadas](#apis-de-dados-utilizadas)
8. [Configuração e Uso](#configuração-e-uso)
9. [Estratégias de Profit-Switching](#estratégias-de-profit-switching)
10. [Métricas e Monitoramento](#métricas-e-monitoramento)
11. [Limitações e Considerações](#limitações-e-considerações)

---

## Visão Geral

O módulo de Machine Learning do HyperMine Core implementa um sistema completo de **profit-switching inteligente** que analisa dados de mercado em tempo real, prevê a lucratividade futura de cada moeda e troca automaticamente o algoritmo de mineração para maximizar o retorno financeiro.

Diferente de profit-switchers tradicionais que apenas comparam a lucratividade instantânea, o HyperMine Core utiliza **modelos preditivos** (XGBoost, LightGBM, Random Forest) em ensemble para antecipar tendências de preço, dificuldade e volume, tomando decisões mais inteligentes sobre quando e para qual moeda trocar.

### Diferencial Competitivo

| Característica | Profit-Switchers Tradicionais | HyperMine Core ML |
|:---|:---|:---|
| Base de decisão | Lucratividade instantânea | Predição de lucratividade futura |
| Modelos | Nenhum | XGBoost + LightGBM + Random Forest (ensemble) |
| Features | Preço × Hashrate | 24+ features (mercado, rede, temporal, hardware) |
| Hysteresis | Simples ou nenhuma | Multi-camada (tempo, frequência, threshold) |
| Re-treinamento | N/A | Automático a cada 24h |
| Hardware-aware | Genérico | Perfil específico do hardware do usuário |

---

## Arquitetura do Sistema ML

```
┌─────────────────────────────────────────────────────────────┐
│                    PROFIT SWITCHER ENGINE                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │ Data Collector│───▶│   Feature    │───▶│ ML Predictor │   │
│  │              │    │  Engineer    │    │  (Ensemble)  │   │
│  └──────────────┘    └──────────────┘    └──────┬───────┘   │
│         │                                        │           │
│         │  ┌─────────────────────────────────────┘           │
│         │  │                                                  │
│         ▼  ▼                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │  Historical  │    │  Decision    │───▶│   Executor   │   │
│  │   Storage    │    │   Engine     │    │ (Miner Ctrl) │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Componentes

1. **Data Collector** — Coleta dados de múltiplas APIs (CoinGecko, WhatToMine, MinerStat) a cada 5 minutos.
2. **Feature Engineer** — Transforma dados brutos em 24+ features numéricas otimizadas para ML.
3. **ML Predictor** — Ensemble de 3 modelos (XGBoost 40%, LightGBM 35%, Random Forest 25%) que prevê lucratividade.
4. **Decision Engine** — Motor de decisão com hysteresis multi-camada para evitar trocas excessivas.
5. **Executor** — Envia comandos de troca ao minerador via Unix Socket ou arquivo JSON.
6. **Historical Storage** — Armazena dados históricos em CSV para re-treinamento contínuo.

---

## Pipeline de Dados

### Fontes de Dados

| API | Dados Coletados | Frequência | Rate Limit |
|:---|:---|:---|:---|
| CoinGecko | Preço, volume 24h, market cap, variação 24h | 5 min | 30 req/min (free) |
| WhatToMine | Dificuldade, nethash, block reward, block time | 5 min | 10 req/min |
| MinerStat | Hashrates de referência, dados de pools | 15 min | 20 req/min |

### Fluxo de Dados

```
APIs → Raw JSON → DataFrame → Feature Engineering → Scaled Features → ML Prediction → Decision → Action
                      │                                                                    │
                      └──── Historical CSV ◄────────────────────────────────────────────────┘
```

---

## Modelos de Machine Learning

### Ensemble Ponderado

O sistema utiliza um ensemble de 3 modelos com pesos otimizados:

| Modelo | Peso | Força | Fraqueza |
|:---|:---|:---|:---|
| **XGBoost** | 40% | Melhor performance geral, captura não-linearidades | Pode overfittar com poucos dados |
| **LightGBM** | 35% | Rápido, eficiente em memória, bom com features categóricas | Sensível a outliers |
| **Random Forest** | 25% | Robusto, resistente a overfitting | Menos preciso em séries temporais |

### Hiperparâmetros

```python
XGBRegressor(
    objective="reg:squarederror",
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    random_state=42
)

LGBMRegressor(
    objective="regression",
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    random_state=42
)

RandomForestRegressor(
    n_estimators=200,
    max_depth=8,
    random_state=42
)
```

### Re-treinamento Automático

O sistema re-treina automaticamente a cada 24 horas quando há pelo menos 100 pontos de dados históricos. O re-treinamento utiliza **TimeSeriesSplit** com 3 folds para respeitar a natureza temporal dos dados.

---

## Feature Engineering

### 24 Features Utilizadas

| # | Feature | Tipo | Descrição |
|:---|:---|:---|:---|
| 1 | `price_usd` | Mercado | Preço atual em USD |
| 2 | `volume_24h_usd` | Mercado | Volume de negociação 24h |
| 3 | `market_cap_usd` | Mercado | Capitalização de mercado |
| 4 | `price_change_24h_pct` | Mercado | Variação de preço 24h (%) |
| 5 | `network_difficulty` | Rede | Dificuldade atual da rede |
| 6 | `network_hashrate` | Rede | Hashrate total da rede |
| 7 | `block_reward` | Rede | Recompensa por bloco |
| 8 | `block_time_sec` | Rede | Tempo médio de bloco |
| 9 | `hour_of_day` | Temporal | Hora do dia (0-23) |
| 10 | `day_of_week` | Temporal | Dia da semana (0-6) |
| 11 | `is_weekend` | Temporal | Fim de semana (0/1) |
| 12 | `price_to_volume_ratio` | Derivada | Preço / Volume |
| 13 | `log_market_cap` | Derivada | log(1 + market_cap) |
| 14 | `log_volume` | Derivada | log(1 + volume) |
| 15 | `log_difficulty` | Derivada | log(1 + difficulty) |
| 16 | `log_nethash` | Derivada | log(1 + nethash) |
| 17 | `blocks_per_day` | Derivada | 86400 / block_time |
| 18 | `user_hashrate` | Hardware | Hashrate do hardware do usuário |
| 19 | `user_power_watts` | Hardware | Consumo do hardware |
| 20 | `energy_cost_per_day` | Custo | Custo diário de energia |
| 21 | `estimated_coins_per_day` | Receita | Moedas estimadas/dia |
| 22 | `estimated_revenue_usd` | Receita | Receita estimada/dia |
| 23 | `revenue_per_watt` | Eficiência | Receita por Watt |
| 24 | `profit_per_watt` | Eficiência | Lucro por Watt |

---

## Decision Engine com Hysteresis

O Decision Engine implementa **hysteresis multi-camada** para evitar trocas excessivas que desperdiçam tempo de setup e shares:

### Camadas de Proteção

1. **Tempo Mínimo de Mineração:** 10 minutos em cada moeda antes de permitir troca.
2. **Limite de Trocas por Hora:** Máximo de 3 trocas por hora.
3. **Threshold de Melhoria:** A nova moeda deve ser pelo menos 5% mais lucrativa que a atual.

### Fluxo de Decisão

```
Nova predição disponível
    │
    ├── Moeda atual é a melhor? → HOLD
    │
    ├── Tempo mínimo não atingido? → HOLD
    │
    ├── Limite de trocas/hora atingido? → HOLD
    │
    ├── Melhoria < 5%? → HOLD
    │
    └── Todas as condições satisfeitas → SWITCH
```

---

## Configuração e Uso

### Instalação

```bash
cd src/ml
pip install -r requirements.txt
```

### Execução

```bash
# Modo contínuo (padrão)
python profit_switcher.py --config hardware_profiles/acer_nitro5_gtx1650.json

# Ciclo único (debug)
python profit_switcher.py --single --energy-cost 0.16

# Intervalo personalizado
python profit_switcher.py --interval 600  # 10 minutos
```

### Parâmetros

| Parâmetro | Padrão | Descrição |
|:---|:---|:---|
| `--config` | Nenhum | Caminho para perfil de hardware JSON |
| `--energy-cost` | 0.16 | Custo de energia em USD/kWh |
| `--interval` | 300 | Intervalo de coleta em segundos |
| `--single` | False | Executar apenas um ciclo |

---

## Estratégias de Profit-Switching

### Estratégia 1: Máximo Lucro Instantâneo (Padrão)
Troca para a moeda com maior lucro previsto no momento, respeitando hysteresis.

### Estratégia 2: Acumulação Especulativa
Minera moedas com baixo preço atual mas alto potencial de valorização (baseado em volume crescente e market cap baixo).

### Estratégia 3: Dual Mining (GPU + CPU)
Minera simultaneamente uma moeda GPU (ex: ERG) e uma moeda CPU (ex: XMR) para maximizar o uso do hardware.

### Estratégia 4: Eficiência Energética
Prioriza moedas com melhor relação lucro/Watt, ideal para regiões com energia cara.

---

## Métricas e Monitoramento

### Métricas do Modelo

| Métrica | Descrição | Meta |
|:---|:---|:---|
| RMSE | Erro quadrático médio | < 0.01 USD |
| MAE | Erro absoluto médio | < 0.005 USD |
| R² | Coeficiente de determinação | > 0.85 |

### Logs

Todos os logs são salvos em `data/profit_switcher.log` com formato:
```
2026-02-21 12:00:00 [ProfitSwitcher] INFO: [SWITCH] ergo | Lucro previsto: $0.0412/dia | Troca: flux → ergo (melhoria de 8.3%)
```

---

## Limitações e Considerações

### Limitações Técnicas

1. **Dados históricos necessários:** O modelo ML precisa de pelo menos 100 pontos de dados (≈8 horas de coleta) para começar a treinar. Até lá, usa estimativa direta.
2. **Rate limits das APIs:** CoinGecko free tier limita a 30 requests/minuto. O sistema respeita esses limites automaticamente.
3. **Latência de troca:** Cada troca de algoritmo leva 5-30 segundos para estabilizar o hashrate.
4. **VRAM limitada (4GB):** Algumas moedas com DAG crescente podem se tornar incompatíveis ao longo do tempo.

### Considerações Financeiras

1. **Volatilidade:** Preços de criptomoedas são extremamente voláteis. Lucros passados não garantem lucros futuros.
2. **Dificuldade crescente:** A dificuldade de rede tende a aumentar com o tempo, reduzindo a receita por hashrate.
3. **Custo de energia:** É o maior fator de custo para mineradores domésticos. Considere horários de tarifa reduzida.
4. **Desgaste do hardware:** Mineração contínua acelera o desgaste de GPU e ventiladores. Monitore temperaturas.

### Aviso Legal

> Este software é fornecido "como está", sem garantias de qualquer tipo. A mineração de criptomoedas envolve riscos financeiros significativos. O usuário é responsável por suas próprias decisões de investimento e deve considerar os custos de energia, desgaste de hardware e volatilidade do mercado antes de iniciar a mineração.
