#!/usr/bin/env python3
"""
Consultas extras via Gemini para cobrir os tópicos que falharam em Perplexity/OpenRouter.
"""

import os
from google import genai

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_KEY)

queries = [
    {
        "title": "Mercado Atual de Mineração GPU/CPU — Todas as Moedas Mineráveis",
        "filename": "/home/ubuntu/quadruple_check_results/01_gemini_mercado_atual.md",
        "prompt": """Faça uma análise COMPLETA de TODAS as criptomoedas que podem ser mineradas por GPU e CPU em 2025-2026.

Para cada moeda, informe em formato de tabela:
- Nome e símbolo
- Algoritmo de mineração
- Hardware recomendado (GPU/CPU/ASIC)
- Se é viável minerar com GPU GTX 1650 (4GB VRAM)

Organize em categorias:
1. TOP 10 moedas mais lucrativas para GPU mining
2. TOP 5 moedas para CPU mining
3. Moedas que migraram para PoS ou morreram em 2024-2026
4. Moedas emergentes de 2025-2026
5. Moedas dominadas por ASIC (não vale a pena com GPU)

Seja EXAUSTIVO. Responda em português brasileiro."""
    },
    {
        "title": "Design Completo do Módulo ML para Profit-Switching",
        "filename": "/home/ubuntu/quadruple_check_results/02_gemini_ml_design.md",
        "prompt": """Projete um módulo completo de Machine Learning para profit-switching automático em mineração de criptomoedas.

O módulo deve decidir em tempo real qual moeda é mais lucrativa para minerar com base em dados de mercado.

ENTREGUE:

1. ARQUITETURA DO SISTEMA:
- Componentes: Data Collector, Feature Engineer, ML Predictor, Decision Engine, Executor
- Fluxo de dados entre componentes
- Frequência de coleta e predição

2. FEATURES DO MODELO (variáveis de entrada):
- Preço atual e histórico (24h, 7d, 30d)
- Dificuldade da rede e tendência
- Hashrate da rede
- Block reward
- Volume de negociação
- Custo de energia local
- Hashrate do hardware do usuário por algoritmo
- Tempo de troca de algoritmo (overhead)
- Taxas de pool

3. MODELO DE ML RECOMENDADO:
- XGBoost ou LightGBM para predição de lucratividade
- Random Forest como fallback
- Ensemble de modelos para robustez
- Métricas: RMSE, MAE, R², Sharpe Ratio

4. CÓDIGO PYTHON COMPLETO para:
a) Coleta de dados via CoinGecko API e WhatToMine API
b) Feature engineering
c) Treinamento do modelo
d) Predição em tempo real
e) Decisão de switching com hysteresis (evitar trocas muito frequentes)

5. INTEGRAÇÃO com minerador C++/Rust:
- Comunicação via Unix socket ou arquivo JSON
- Formato da mensagem de switching
- Timeout e fallback

Dê código COMPLETO e FUNCIONAL em Python. Responda em português brasileiro."""
    },
    {
        "title": "Análise de Viabilidade — GTX 1650 Laptop para Cada Moeda",
        "filename": "/home/ubuntu/quadruple_check_results/06_gemini_viabilidade_gtx1650.md",
        "prompt": """Crie uma tabela COMPLETA de viabilidade de mineração para CADA moeda minerável com uma GTX 1650 (4GB GDDR5, laptop, ~50W TDP).

Para CADA moeda viável, calcule:

| Moeda | Algoritmo | Hashrate GTX 1650 | Consumo (W) | Receita/dia (USD) | Custo Energia/dia (USD) | Lucro/dia (USD) | Viável? |

Considere:
- Custo energia: $0.16/kWh (Brasil)
- Consumo total sistema: 120W (GPU + CPU + outros)
- Preços de fevereiro 2026

Inclua TODAS as moedas possíveis:
ETC, ERG, RVN, KAS, ALPH, CFX, NEXA, CLORE, NEOX, FLUX, XMR (CPU), RTM (CPU), VRSC (CPU), FIRO, DNX, RXD, IRON, XNA, ZEPH, DERO, WOW, XHV, OCTA, NEOXA, MWC, SERO, QRL, XEL, BEAM, GRIN, BTG, VTC, AION

Depois faça um RANKING das TOP 10 mais lucrativas para este hardware.

Responda em português brasileiro com tabelas detalhadas."""
    }
]

for q in queries:
    print(f"\n{'='*60}")
    print(f"Consultando: {q['title']}")
    print(f"{'='*60}")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=q["prompt"]
        )
        result = response.text if hasattr(response, 'text') else str(response)
        
        with open(q["filename"], "w") as f:
            f.write(f"# {q['title']}\n\n**Fonte:** Google Gemini 2.5 Flash\n**Data:** Fevereiro 2026\n\n---\n\n")
            f.write(result)
        
        print(f"✅ Salvo: {q['filename']} ({len(result)} chars)")
    except Exception as e:
        print(f"❌ Erro: {e}")

print("\n=== Consultas extras concluídas ===")
