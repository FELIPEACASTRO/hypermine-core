#!/usr/bin/env python3
"""
Triple Check — Consulta a múltiplos especialistas via Gemini para validação final.
Foco: gaps, lacunas, moedas faltantes, e projeção para GTX 1650 laptop.
"""

import os
import json
from google import genai

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_KEY)

# Ler o README atual do projeto
with open("/home/ubuntu/hypermine-core/README.md", "r") as f:
    readme_content = f.read()[:8000]

# Ler lista de moedas
coins = os.listdir("/home/ubuntu/hypermine-core/coins/")
coins_list = ", ".join([c.replace(".toml", "").upper() for c in sorted(coins)])

queries = [
    {
        "role": "Analista de Mercado Crypto — Triple Check de Moedas",
        "prompt": f"""Você é um analista sênior de mercado de criptomoedas com 10 anos de experiência em mineração.

CONTEXTO: O projeto HyperMine Core atualmente suporta as seguintes moedas: {coins_list}

TAREFA: Faça um triple check completo e identifique:
1. TODAS as moedas mineráveis por GPU que estão FALTANDO e que são relevantes em 2025-2026
2. TODAS as moedas mineráveis por CPU que estão FALTANDO
3. Moedas que foram descontinuadas ou não são mais mineráveis
4. Moedas emergentes que devem ser adicionadas urgentemente
5. Gaps e lacunas na cobertura de algoritmos

Seja EXAUSTIVO. Liste TODAS as moedas faltantes com: nome, símbolo, algoritmo, hardware (CPU/GPU), e justificativa.
Responda em português brasileiro."""
    },
    {
        "role": "Engenheiro de Performance — Triple Check de Otimizações para GTX 1650",
        "prompt": f"""Você é um engenheiro de performance especializado em mineração de criptomoedas com GPUs de baixo consumo.

CONTEXTO: O usuário possui um notebook Acer Nitro 5 com:
- CPU: Intel Core i5 (provavelmente i5-9300H, 4 cores/8 threads)
- GPU: NVIDIA GeForce GTX 1650 (4GB GDDR5, 896 CUDA cores, ~50W TDP laptop)
- RAM: Provavelmente 8-16GB DDR4
- É um NOTEBOOK, não desktop

TAREFA:
1. Quais são as MELHORES moedas para minerar com GTX 1650 laptop em 2025-2026?
2. Quais otimizações específicas são necessárias para notebook (thermal throttling, power limit)?
3. Quais algoritmos NÃO devem ser usados na GTX 1650 (4GB VRAM)?
4. Qual a projeção REALISTA de lucro diário com este hardware?
5. Quais riscos de minerar em notebook (degradação de hardware, garantia)?
6. Quais moedas podem ser mineradas simultaneamente com CPU + GPU?

Seja HONESTO e REALISTA. Não exagere lucros. Considere custo de energia no Brasil (~R$0.88/kWh = ~$0.16/kWh).
Responda em português brasileiro."""
    },
    {
        "role": "Auditor Técnico — Triple Check de Gaps e Lacunas",
        "prompt": f"""Você é um auditor técnico sênior especializado em projetos de mineração de criptomoedas.

CONTEXTO: Analise este README de projeto de mineração:

{readme_content[:4000]}

TAREFA: Identifique TODOS os gaps, lacunas e problemas:
1. Funcionalidades prometidas mas não implementadas
2. Algoritmos listados mas sem implementação
3. Inconsistências entre documentação e código
4. Riscos técnicos não mencionados
5. Dependências faltantes ou desatualizadas
6. Problemas de segurança não endereçados
7. Funcionalidades essenciais que estão faltando (ex: auto-update, watchdog, crash recovery)
8. Comparação com mineradores existentes (XMRig, T-Rex, lolMiner) — o que eles têm que o HyperMine não tem?

Seja IMPIEDOSO na auditoria. Liste TODOS os problemas encontrados.
Responda em português brasileiro."""
    }
]

os.makedirs("/home/ubuntu/triple_check_results", exist_ok=True)

for i, q in enumerate(queries, 1):
    print(f"\n{'='*60}")
    print(f"Consultando: {q['role']}")
    print(f"{'='*60}")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=q["prompt"]
        )
        
        result = response.text if hasattr(response, 'text') else str(response)
        
        filename = f"/home/ubuntu/triple_check_results/{i:02d}_{q['role'].split(' — ')[0].replace(' ', '_').lower()}.md"
        with open(filename, "w") as f:
            f.write(f"# {q['role']}\n\n")
            f.write(f"**Data:** Fevereiro 2026\n\n---\n\n")
            f.write(result)
        
        print(f"✅ Salvo: {filename}")
        print(f"   Tamanho: {len(result)} caracteres")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        filename = f"/home/ubuntu/triple_check_results/{i:02d}_error.md"
        with open(filename, "w") as f:
            f.write(f"# ERRO: {q['role']}\n\n{str(e)}")

print("\n\n=== Triple Check Completo ===")
print(f"Resultados em: /home/ubuntu/triple_check_results/")
