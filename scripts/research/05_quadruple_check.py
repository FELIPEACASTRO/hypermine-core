#!/usr/bin/env python3
"""
Quádruplo Check — Consulta a múltiplos conectores de IA para validação final.
Inclui: Gemini, Perplexity (Sonar), e OpenRouter para perspectivas diversas.
Foco: gaps finais, ML para profit-switching, e moedas faltantes.
"""

import os
import json
import requests
from google import genai

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
SONAR_KEY = os.environ.get("SONAR_API_KEY", "")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")

os.makedirs("/home/ubuntu/quadruple_check_results", exist_ok=True)

# ==================== PERPLEXITY (SONAR) ====================
def call_perplexity(prompt, filename, role_title):
    print(f"\n{'='*60}")
    print(f"[PERPLEXITY] Consultando: {role_title}")
    print(f"{'='*60}")
    try:
        headers = {
            "Authorization": f"Bearer {SONAR_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "sonar-pro",
            "messages": [
                {"role": "system", "content": "Você é um especialista sênior em mineração de criptomoedas e machine learning. Responda em português brasileiro com máxima profundidade técnica."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 8000
        }
        resp = requests.post("https://api.perplexity.ai/chat/completions", headers=headers, json=data, timeout=120)
        resp.raise_for_status()
        result = resp.json()["choices"][0]["message"]["content"]
        
        with open(filename, "w") as f:
            f.write(f"# {role_title}\n\n**Fonte:** Perplexity Sonar Pro (com acesso web em tempo real)\n**Data:** Fevereiro 2026\n\n---\n\n")
            f.write(result)
        
        print(f"✅ Salvo: {filename} ({len(result)} chars)")
        return result
    except Exception as e:
        print(f"❌ Erro Perplexity: {e}")
        with open(filename, "w") as f:
            f.write(f"# ERRO: {role_title}\n\n{str(e)}")
        return ""

# ==================== OPENROUTER ====================
def call_openrouter(prompt, filename, role_title):
    print(f"\n{'='*60}")
    print(f"[OPENROUTER] Consultando: {role_title}")
    print(f"{'='*60}")
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "google/gemini-2.5-flash-preview",
            "messages": [
                {"role": "system", "content": "Você é um especialista sênior em mineração de criptomoedas, machine learning e otimização de performance. Responda em português brasileiro com máxima profundidade técnica."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 8000
        }
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=180)
        resp.raise_for_status()
        result = resp.json()["choices"][0]["message"]["content"]
        
        with open(filename, "w") as f:
            f.write(f"# {role_title}\n\n**Fonte:** OpenRouter (Gemini 2.5 Flash)\n**Data:** Fevereiro 2026\n\n---\n\n")
            f.write(result)
        
        print(f"✅ Salvo: {filename} ({len(result)} chars)")
        return result
    except Exception as e:
        print(f"❌ Erro OpenRouter: {e}")
        with open(filename, "w") as f:
            f.write(f"# ERRO: {role_title}\n\n{str(e)}")
        return ""

# ==================== GEMINI ====================
def call_gemini(prompt, filename, role_title):
    print(f"\n{'='*60}")
    print(f"[GEMINI] Consultando: {role_title}")
    print(f"{'='*60}")
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        result = response.text if hasattr(response, 'text') else str(response)
        
        with open(filename, "w") as f:
            f.write(f"# {role_title}\n\n**Fonte:** Google Gemini 2.5 Flash\n**Data:** Fevereiro 2026\n\n---\n\n")
            f.write(result)
        
        print(f"✅ Salvo: {filename} ({len(result)} chars)")
        return result
    except Exception as e:
        print(f"❌ Erro Gemini: {e}")
        with open(filename, "w") as f:
            f.write(f"# ERRO: {role_title}\n\n{str(e)}")
        return ""

# ==================== CONSULTAS ====================

# 1. PERPLEXITY — Dados em tempo real sobre moedas mineráveis em 2026
call_perplexity(
    """Faça uma análise COMPLETA e ATUALIZADA (fevereiro 2026) de TODAS as criptomoedas que podem ser mineradas por GPU e CPU atualmente.

Para cada moeda, informe:
- Nome e símbolo
- Algoritmo de mineração
- Hardware recomendado (GPU/CPU/ASIC)
- Hashrate típico de uma GTX 1650 (se disponível)
- Lucratividade estimada diária com GTX 1650
- Se ainda é viável minerar com GPU ou se ASICs dominaram

Também informe:
1. Quais moedas NOVAS surgiram em 2025-2026 para mineração GPU/CPU?
2. Quais moedas MORRERAM ou migraram para PoS em 2025-2026?
3. Qual o estado atual do mercado de mineração GPU em fevereiro 2026?
4. Quais são as TOP 10 moedas mais lucrativas para GPU mining AGORA?

Seja EXAUSTIVO e use dados REAIS e ATUALIZADOS.""",
    "/home/ubuntu/quadruple_check_results/01_perplexity_mercado_atual.md",
    "Análise de Mercado em Tempo Real — Moedas Mineráveis (Fev 2026)"
)

# 2. PERPLEXITY — ML para profit-switching em mineração
call_perplexity(
    """Quero criar um módulo de Machine Learning para um software de mineração de criptomoedas que faça profit-switching automático e inteligente.

O módulo deve:
1. Coletar dados em tempo real de APIs (preço, dificuldade, hashrate da rede, block reward)
2. Usar ML para PREVER qual moeda será mais lucrativa nas próximas horas/dias
3. Trocar automaticamente o algoritmo de mineração para maximizar lucro
4. Considerar custo de energia, tempo de troca de algoritmo, e taxas de pool

Perguntas específicas:
1. Quais modelos de ML são mais adequados para previsão de lucratividade de mineração?
2. Quais features/variáveis devem alimentar o modelo?
3. Quais APIs fornecem dados em tempo real de dificuldade, preço e hashrate?
4. Como implementar isso em Python/Rust para rodar junto com o minerador?
5. Existem projetos open-source que já fazem isso? Quais?
6. Qual a arquitetura ideal para um sistema de profit-switching com ML?

Dê exemplos de código e arquitetura detalhada.""",
    "/home/ubuntu/quadruple_check_results/02_perplexity_ml_profit_switching.md",
    "Arquitetura ML para Profit-Switching Inteligente"
)

# 3. GEMINI — Quádruplo check de gaps técnicos
call_gemini(
    """Você é um comitê de 5 especialistas fazendo um QUÁDRUPLO CHECK em um projeto de mineração de criptomoedas chamado HyperMine Core.

O projeto atualmente tem:
- Linguagens: C++20 + Rust + CUDA + Assembly x86-64
- 42+ algoritmos: SHA-256, Scrypt, Ethash, Etchash, RandomX, KawPow, Autolykos2, kHeavyHash, Blake3, Equihash, CryptoNight, X11, X16R, ProgPow, GhostRider, FishHash, NexaPow, Octopus, cuckAToo31, BeamHash, ZelHash, Verthash, MTP, Lyra2REv3, Skein, Qubit, Tribus, NeoScrypt, Groestl, Keccak, JH, BLAKE2s, Argon2d, YescryptR32, CryptoNightR, RandomARQ, RandomSFX, Eaglesong, Cuckatoo32, CuckooCycle, Cuckoo29
- 23 moedas configuradas: BTC, XMR, LTC, ETC, RVN, ZEC, ERG, DOGE, DASH, RTM, FIRO, KAS, ALPH, CFX, NEXA, CLORE, NEOX, FLUX, NEOXA, VRSC, QRL, XEL, SERO

IDENTIFIQUE TODOS OS GAPS RESTANTES:
1. Moedas mineráveis por GPU em 2025-2026 que AINDA faltam
2. Moedas mineráveis por CPU que AINDA faltam
3. Algoritmos que existem mas não estão na lista
4. Problemas técnicos na escolha de linguagens
5. Funcionalidades que mineradores concorrentes (XMRig, T-Rex, lolMiner, TeamRedMiner, Gminer, NBMiner, SRBMiner) têm e que faltam
6. Moedas na lista que NÃO deveriam estar (ex: dominadas por ASIC)
7. Novas tendências em mineração 2025-2026 não cobertas

Seja IMPIEDOSO e EXAUSTIVO. Liste TUDO que falta.
Responda em português brasileiro.""",
    "/home/ubuntu/quadruple_check_results/03_gemini_quadruplo_check.md",
    "Quádruplo Check — Comitê de 5 Especialistas"
)

# 4. OPENROUTER — Design do módulo ML
call_openrouter(
    """Projete um módulo completo de Machine Learning para profit-switching em mineração de criptomoedas.

REQUISITOS:
- Deve rodar em Python 3.11+ com integração via FFI com o minerador em C++/Rust
- Deve coletar dados de múltiplas APIs (CoinGecko, WhatToMine, minerstat)
- Deve usar modelos de ML para prever lucratividade futura (próximas 1-24h)
- Deve considerar: preço da moeda, dificuldade da rede, hashrate da rede, block reward, taxas de pool, custo de energia, tempo de troca de algoritmo
- Deve funcionar para um Acer Nitro 5 com GTX 1650 e Intel Core i5

ENTREGUE:
1. Arquitetura completa do módulo (diagrama de componentes)
2. Código Python completo e funcional para:
   a. Coleta de dados via APIs
   b. Feature engineering
   c. Treinamento do modelo (XGBoost ou LightGBM)
   d. Predição em tempo real
   e. Decisão de switching
3. Esquema de dados (quais features, como normalizar)
4. Pipeline de treinamento e re-treinamento
5. Integração com o minerador (como comunicar a decisão)
6. Métricas de avaliação do modelo

Dê código COMPLETO e FUNCIONAL em Python.
Responda em português brasileiro.""",
    "/home/ubuntu/quadruple_check_results/04_openrouter_ml_design.md",
    "Design Completo do Módulo ML — Profit Switching"
)

# 5. GEMINI — Projeção financeira detalhada para GTX 1650
call_gemini(
    """Você é um analista financeiro especializado em mineração de criptomoedas. Crie uma PROJEÇÃO DE LUCRO DETALHADA para 1 ano (365 dias) de mineração com o seguinte hardware:

HARDWARE:
- Notebook Acer Nitro 5
- CPU: Intel Core i5-9300H (4 cores, 8 threads, 2.4-4.1 GHz)
- GPU: NVIDIA GeForce GTX 1650 (4GB GDDR5, 896 CUDA cores, ~50W TDP laptop)
- RAM: 16GB DDR4
- Consumo total do sistema: ~120W durante mineração

DADOS DE HASHRATE DA GTX 1650:
- Etchash (ETC): 15.82-18.1 MH/s, 48-66W
- KAWPOW (RVN): 7.15-8.1 MH/s, 66W
- Autolykos2 (ERG): 36 MH/s, ~50W
- kHeavyHash (KAS): 200 MH/s, ~50W
- Blake3 (ALPH): 450 MH/s, ~50W
- Octopus (CFX): 8.9 MH/s, 50W
- RandomX (XMR, CPU): ~2.5 kH/s, ~45W

CUSTO DE ENERGIA NO BRASIL:
- Tarifa média residencial: R$0.88/kWh (~$0.16/kWh)
- Considerar bandeira verde (sem adicional)

CRIE UMA TABELA com projeção MENSAL (12 meses) contendo:
- Receita bruta em USD e BRL para cada moeda
- Custo de energia em USD e BRL
- Lucro líquido em USD e BRL
- Cenário otimista (preços sobem 50%)
- Cenário realista (preços estáveis)
- Cenário pessimista (preços caem 30%)

CONSIDERE:
- Aumento médio de dificuldade de 5% ao mês
- Variação de preço das moedas
- Desgaste do hardware (redução de 2% no hashrate após 6 meses)
- Custo de manutenção (pasta térmica, cooling pad)
- Profit-switching com ML (ganho estimado de 15-25% vs mineração fixa)

Use preços atuais de fevereiro 2026:
- ETC: ~$18
- ERG: ~$0.30
- RVN: ~$0.006
- KAS: ~$0.031
- ALPH: ~$0.50
- CFX: ~$0.08
- XMR: ~$230

Responda em português brasileiro com tabelas detalhadas.""",
    "/home/ubuntu/quadruple_check_results/05_gemini_projecao_financeira.md",
    "Projeção Financeira Detalhada — 1 Ano de Mineração"
)

print("\n\n" + "="*60)
print("=== QUÁDRUPLO CHECK COMPLETO ===")
print("="*60)
print(f"Resultados em: /home/ubuntu/quadruple_check_results/")

# Listar resultados
for f in sorted(os.listdir("/home/ubuntu/quadruple_check_results")):
    path = os.path.join("/home/ubuntu/quadruple_check_results", f)
    size = os.path.getsize(path)
    print(f"  {f}: {size:,} bytes")
