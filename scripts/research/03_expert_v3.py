#!/usr/bin/env python3
"""
HyperMine Core — Double Check v3
Usa Gemini (funciona) + OpenRouter com modelos corretos para múltiplas perspectivas.
"""

import os
import json
import asyncio
import httpx
import time

RESULTS_DIR = "/home/ubuntu/expert_results"
os.makedirs(RESULTS_DIR, exist_ok=True)

PROJECT_CONTEXT = """
Projeto: HyperMine Core — Minerador Universal de Criptomoedas de Alta Performance.
Linguagens: C++20 (algoritmos, kernels GPU, HAL) + Rust (networking Stratum, config, monitoring).
GPU: CUDA 12 (NVIDIA) + OpenCL 3.0 (AMD/Intel). Assembly x86-64 para hotspots.
Suporta 30+ algoritmos: SHA-256, RandomX, Ethash/Etchash, KAWPOW, Equihash, Scrypt, X11, GhostRider, Autolykos2, etc.
Parametrizável via TOML. Estratégias: most_profitable, round_robin, manual.
Otimizações: SIMD (SSE4.2/AVX2/AVX-512/SHA-NI/NEON), Huge Pages, NUMA, persistent kernels GPU,
Stratum V1/V2, TLS 1.3, failover <1s, PGO, LTO, lock-free data structures.
Monitoramento: API REST + Prometheus + alertas Discord/Telegram.
Roadmap: 8 fases, 40 semanas.
"""

EXPERT_PROMPTS = [
    {
        "name": "01_blockchain_crypto_expert",
        "title": "Engenheiro de Blockchain e Criptografia",
        "prompt": f"""Você é um engenheiro sênior de blockchain e criptografia com 15 anos de experiência em mineração. Responda em português brasileiro.

Analise criticamente este minerador:
{PROJECT_CONTEXT}

1. VALIDAÇÃO: Algoritmos corretos e atualizados para 2025-2026? Quais faltam?
2. NOVOS ALGORITMOS de mineração 2024-2026
3. MOEDAS EMERGENTES mineráveis
4. POOLS ATUALIZADOS: melhores pools atuais
5. HARDWARE 2025-2026: GPUs/CPUs mais recentes
6. TENDÊNCIAS: merge mining, MEV, proof-of-useful-work
7. ERROS OU OMISSÕES graves

Seja extremamente detalhado."""
    },
    {
        "name": "02_systems_architect",
        "title": "Arquiteto de Sistemas de Alta Performance",
        "prompt": f"""Você é um arquiteto de sistemas de alta performance especializado em computação paralela e GPGPU. Responda em português brasileiro.

Analise este minerador:
{PROJECT_CONTEXT}

1. ARQUITETURA em camadas: correta? Melhorias?
2. C++ vs RUST: divisão ideal? Zig, Carbon?
3. CUDA/OpenCL: otimizações suficientes?
4. SIMD: 7 variantes cobrem tudo? AVX10, AMX?
5. MEMÓRIA: CXL memory, HBM3?
6. COMPILAÇÃO: PGO+LTO suficientes? BOLT, AutoFDO?
7. BENCHMARKS: números realistas 2025-2026?
8. Top 5 melhorias de maior impacto em performance
9. ERROS TÉCNICOS no design

Seja extremamente técnico."""
    },
    {
        "name": "03_gpu_computing_expert",
        "title": "Especialista em GPU Computing e CUDA",
        "prompt": f"""Você é um especialista em GPU computing, CUDA e otimização de kernels para mineração. Responda em português brasileiro.

Analise este minerador focando em GPU:
{PROJECT_CONTEXT}

1. CUDA 12.x features: Cooperative Groups, Graph API
2. NVIDIA RTX 50-series otimizações, Blackwell
3. AMD ROCm/HIP vs OpenCL
4. Kernel design para SHA-256, Ethash, KAWPOW, Equihash
5. Memory hierarchy: registers, shared, L1/L2, global
6. Warp-level primitives cruciais
7. Multi-GPU: NVLink, PCIe, P2P
8. Power efficiency: hash/watt
9. Vulkan compute como alternativa
10. Erros na abordagem GPU"""
    },
    {
        "name": "04_security_expert",
        "title": "Engenheiro de Segurança e Protocolos",
        "prompt": f"""Você é um engenheiro de segurança especializado em mineração de criptomoedas. Responda em português brasileiro.

Analise este minerador:
{PROJECT_CONTEXT}

1. STRATUM V2: implementação completa? NOISE protocol?
2. SEGURANÇA DE REDE: TLS 1.3, certificate pinning
3. ATAQUES: pool poisoning, MITM, hashrate hijacking
4. WALLET SECURITY: proteção de endereços
5. ANTI-TAMPERING: proteção do binário
6. API SECURITY: API REST local
7. SUPPLY CHAIN: segurança de dependências
8. COMPLIANCE: considerações legais
9. ROADMAP DE SEGURANÇA enterprise-grade
10. VULNERABILIDADES críticas"""
    },
    {
        "name": "05_devops_infrastructure",
        "title": "Especialista em DevOps e Infraestrutura",
        "prompt": f"""Você é um especialista em DevOps e infraestrutura de farms de mineração (1000+ GPUs). Responda em português brasileiro.

Analise este minerador:
{PROJECT_CONTEXT}

1. DOCKER/K8S: orquestração de 100+ mineradores
2. CI/CD: testes automatizados essenciais
3. MONITORING: Prometheus+Grafana para 1000+ GPUs
4. CONFIG MANAGEMENT: TOML para farms? Ansible?
5. AUTO-SCALING baseado em lucratividade
6. DRIVER MANAGEMENT em escala
7. DISASTER RECOVERY
8. COST OPTIMIZATION
9. BARE METAL vs CLOUD
10. ROADMAP DevOps enterprise"""
    },
    {
        "name": "06_innovation_strategist",
        "title": "Estrategista de Inovação em Crypto e Web3",
        "prompt": f"""Você é um estrategista de inovação em criptomoedas e Web3. Responda em português brasileiro.

Analise este minerador:
{PROJECT_CONTEXT}

1. FUTURO DA MINERAÇÃO 2025-2030
2. PROOF-OF-USEFUL-WORK: Qubic, Flux, Golem
3. AI + MINING: render farming, training
4. MERGE MINING oportunidades
5. GREEN MINING: sustentabilidade
6. NOVAS BLOCKCHAINS mineráveis PoW
7. FPGA/ASIC: investir mais?
8. COMPETIDORES: XMRig, T-Rex, lolMiner, TeamRedMiner, Gminer
9. ROADMAP ESTRATÉGICO: vantagem competitiva
10. COMUNIDADE open-source"""
    }
]

async def call_gemini(client, expert):
    """Chama Gemini para cada especialista."""
    try:
        resp = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={os.environ['GEMINI_API_KEY']}",
            json={
                "contents": [{"parts": [{"text": expert["prompt"]}]}],
                "generationConfig": {"temperature": 0.3, "maxOutputTokens": 8000}
            },
            timeout=180
        )
        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}: {resp.text[:300]}")
        data = resp.json()
        result = data["candidates"][0]["content"]["parts"][0]["text"]
        with open(f"{RESULTS_DIR}/{expert['name']}_gemini.md", "w") as f:
            f.write(f"# {expert['title']} (Google Gemini)\n\n{result}\n")
        print(f"[OK] Gemini — {expert['title']}")
        return result
    except Exception as e:
        err = f"ERRO: {e}"
        print(f"[FAIL] Gemini — {expert['title']}: {err[:100]}")
        with open(f"{RESULTS_DIR}/{expert['name']}_gemini.md", "w") as f:
            f.write(err)
        return None

async def call_openrouter(client, expert):
    """Chama OpenRouter para cada especialista."""
    try:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-2.5-flash-preview-05-20",
                "messages": [
                    {"role": "user", "content": expert["prompt"]}
                ],
                "max_tokens": 8000
            },
            timeout=180
        )
        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}: {resp.text[:300]}")
        data = resp.json()
        result = data["choices"][0]["message"]["content"]
        with open(f"{RESULTS_DIR}/{expert['name']}_openrouter.md", "w") as f:
            f.write(f"# {expert['title']} (OpenRouter)\n\n{result}\n")
        print(f"[OK] OpenRouter — {expert['title']}")
        return result
    except Exception as e:
        err = f"ERRO: {e}"
        print(f"[FAIL] OpenRouter — {expert['title']}: {err[:100]}")
        with open(f"{RESULTS_DIR}/{expert['name']}_openrouter.md", "w") as f:
            f.write(err)
        return None

async def main():
    print("=" * 70)
    print("HyperMine Core — Double Check Avassalador v3")
    print(f"Consultando 6 especialistas via Gemini + OpenRouter...")
    print("=" * 70)
    
    start = time.time()
    
    async with httpx.AsyncClient() as client:
        tasks = []
        # Gemini calls (6 experts)
        for expert in EXPERT_PROMPTS:
            tasks.append(call_gemini(client, expert))
        # OpenRouter calls (6 experts) - second opinion
        for expert in EXPERT_PROMPTS:
            tasks.append(call_openrouter(client, expert))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    elapsed = time.time() - start
    successes = sum(1 for r in results if r is not None and not isinstance(r, Exception))
    print(f"\n{'=' * 70}")
    print(f"Consultas concluídas em {elapsed:.1f}s")
    print(f"Sucessos: {successes}/12")
    
    for f in sorted(os.listdir(RESULTS_DIR)):
        if f.endswith('.md'):
            size = os.path.getsize(f"{RESULTS_DIR}/{f}")
            status = "OK" if size > 500 else "SMALL"
            print(f"  [{status}] {f} ({size:,} bytes)")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
