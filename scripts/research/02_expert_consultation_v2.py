#!/usr/bin/env python3
"""
HyperMine Core — Double Check Avassalador v2
Consulta 6 conectores de IA com debug melhorado.
"""

import os
import json
import asyncio
import httpx
import time
import traceback

RESULTS_DIR = "/home/ubuntu/expert_results"
os.makedirs(RESULTS_DIR, exist_ok=True)

PROJECT_CONTEXT = """
Projeto: HyperMine Core — Minerador Universal de Criptomoedas de Alta Performance.
Linguagens: C++20 (algoritmos, kernels GPU, HAL) + Rust (networking Stratum, config, monitoring).
GPU: CUDA 12 (NVIDIA) + OpenCL 3.0 (AMD/Intel). Assembly x86-64 para hotspots.
Suporta 30+ algoritmos: SHA-256, RandomX, Ethash/Etchash, KAWPOW, Equihash, Scrypt, X11, GhostRider, Autolykos2, etc.
Parametrizável via TOML: enabled_coins=["*"] ou ["bitcoin","monero"] ou ["*","!dogecoin"].
Estratégias: most_profitable, round_robin, manual.
Otimizações: SIMD (SSE4.2/AVX2/AVX-512/SHA-NI/NEON), Huge Pages, NUMA, persistent kernels GPU,
Stratum V1/V2, TLS 1.3, failover <1s, PGO, LTO, lock-free data structures.
Monitoramento: API REST + Prometheus + alertas Discord/Telegram.
Roadmap: 8 fases, 40 semanas.
"""

async def call_perplexity(client):
    """Especialista 1: Blockchain e Criptografia"""
    try:
        resp = await client.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['SONAR_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar-pro",
                "messages": [
                    {"role": "system", "content": "Você é um engenheiro sênior de blockchain e criptografia com 15 anos de experiência em mineração de criptomoedas. Responda em português brasileiro com riqueza técnica."},
                    {"role": "user", "content": f"""Analise criticamente este projeto de minerador de criptomoedas:

{PROJECT_CONTEXT}

Forneça:
1. VALIDAÇÃO: Os algoritmos estão corretos e atualizados para 2025-2026? Quais faltam?
2. NOVOS ALGORITMOS de mineração que surgiram em 2024-2026
3. MOEDAS EMERGENTES mineráveis relevantes
4. POOLS ATUALIZADOS: Slushpool, F2Pool, 2Miners ainda são os melhores?
5. HARDWARE 2025-2026: GPUs/CPUs mais recentes (RTX 5090, MI300X)
6. TENDÊNCIAS: merge mining, MEV, proof-of-useful-work
7. ERROS OU OMISSÕES graves no projeto

Seja extremamente detalhado."""}
                ],
                "max_tokens": 4000
            },
            timeout=120
        )
        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}: {resp.text[:500]}")
        data = resp.json()
        result = data["choices"][0]["message"]["content"]
        with open(f"{RESULTS_DIR}/01_perplexity_blockchain_expert.md", "w") as f:
            f.write(f"# Especialista 1: Engenheiro de Blockchain e Criptografia (Perplexity/Sonar)\n\n{result}\n")
        print("[OK] Perplexity")
        return True
    except Exception as e:
        err_msg = f"ERRO Perplexity: {e}\n{traceback.format_exc()}"
        print(err_msg[:200])
        with open(f"{RESULTS_DIR}/01_perplexity_blockchain_expert.md", "w") as f:
            f.write(err_msg)
        return False

async def call_gemini(client):
    """Especialista 2: Arquiteto de Sistemas"""
    try:
        resp = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={os.environ['GEMINI_API_KEY']}",
            json={
                "contents": [{"parts": [{"text": f"""Você é um arquiteto de sistemas de alta performance especializado em computação paralela e GPGPU. Responda em português brasileiro.

Analise este projeto de minerador:
{PROJECT_CONTEXT}

Forneça análise sobre:
1. ARQUITETURA: A arquitetura em camadas está correta? O que melhorar?
2. C++ vs RUST: A divisão está ideal? Onde Zig ou Carbon seriam melhores?
3. CUDA/OpenCL: Otimizações suficientes? O que falta?
4. SIMD: As 7 variantes cobrem tudo? AVX10, AMX?
5. MEMÓRIA: Algo mais avançado como CXL memory, HBM3?
6. COMPILAÇÃO: PGO + LTO suficientes? BOLT, AutoFDO?
7. BENCHMARKS: Números realistas para 2025-2026?
8. MELHORIAS CRÍTICAS: Top 5 melhorias para maior impacto em performance.
9. ERROS TÉCNICOS no design.

Seja extremamente técnico."""}]}],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 4000}
            },
            timeout=120
        )
        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}: {resp.text[:500]}")
        data = resp.json()
        result = data["candidates"][0]["content"]["parts"][0]["text"]
        with open(f"{RESULTS_DIR}/02_gemini_systems_architect.md", "w") as f:
            f.write(f"# Especialista 2: Arquiteto de Sistemas (Google Gemini)\n\n{result}\n")
        print("[OK] Gemini")
        return True
    except Exception as e:
        err_msg = f"ERRO Gemini: {e}"
        print(err_msg[:200])
        with open(f"{RESULTS_DIR}/02_gemini_systems_architect.md", "w") as f:
            f.write(err_msg)
        return False

async def call_grok(client):
    """Especialista 3: GPU Computing"""
    try:
        resp = await client.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['XAI_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "grok-3-mini-fast",
                "messages": [
                    {"role": "system", "content": "Você é um especialista em GPU computing e CUDA. Responda em português brasileiro."},
                    {"role": "user", "content": f"""Analise este minerador focando em GPU:
{PROJECT_CONTEXT}

Analise:
1. CUDA 12.x features a explorar (Cooperative Groups, Graph API)
2. NVIDIA RTX 50-series otimizações
3. AMD ROCm/HIP vs OpenCL
4. Kernel design ideal para SHA-256, Ethash, KAWPOW, Equihash
5. Memory hierarchy optimization
6. Warp-level primitives cruciais
7. Multi-GPU scaling (NVLink, PCIe)
8. Power efficiency (hash/watt)
9. Vulkan compute como alternativa
10. Erros e omissões na abordagem GPU"""}
                ],
                "max_tokens": 4000
            },
            timeout=120
        )
        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}: {resp.text[:500]}")
        data = resp.json()
        result = data["choices"][0]["message"]["content"]
        with open(f"{RESULTS_DIR}/03_grok_gpu_expert.md", "w") as f:
            f.write(f"# Especialista 3: GPU Computing Expert (Grok/xAI)\n\n{result}\n")
        print("[OK] Grok")
        return True
    except Exception as e:
        err_msg = f"ERRO Grok: {e}\n{traceback.format_exc()}"
        print(err_msg[:200])
        with open(f"{RESULTS_DIR}/03_grok_gpu_expert.md", "w") as f:
            f.write(err_msg)
        return False

async def call_anthropic(client):
    """Especialista 4: Segurança"""
    try:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": os.environ['ANTHROPIC_API_KEY'],
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 4000,
                "messages": [
                    {"role": "user", "content": f"""Você é um engenheiro de segurança especializado em mineração de criptomoedas. Responda em português brasileiro.

Analise este minerador:
{PROJECT_CONTEXT}

Analise:
1. STRATUM V2: Implementação completa? NOISE protocol?
2. SEGURANÇA DE REDE: TLS 1.3 suficiente? Certificate pinning?
3. ATAQUES: Pool poisoning, MITM, hashrate hijacking
4. WALLET SECURITY: Proteção de endereços na config
5. ANTI-TAMPERING: Proteção contra modificação do binário
6. API SECURITY: API REST local segura?
7. SUPPLY CHAIN: Segurança de dependências
8. COMPLIANCE: Considerações legais
9. ROADMAP DE SEGURANÇA para enterprise-grade
10. VULNERABILIDADES críticas no design"""}
                ]
            },
            timeout=120
        )
        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}: {resp.text[:500]}")
        data = resp.json()
        result = data["content"][0]["text"]
        with open(f"{RESULTS_DIR}/04_anthropic_security_expert.md", "w") as f:
            f.write(f"# Especialista 4: Engenheiro de Segurança (Anthropic Claude)\n\n{result}\n")
        print("[OK] Anthropic")
        return True
    except Exception as e:
        err_msg = f"ERRO Anthropic: {e}\n{traceback.format_exc()}"
        print(err_msg[:200])
        with open(f"{RESULTS_DIR}/04_anthropic_security_expert.md", "w") as f:
            f.write(err_msg)
        return False

async def call_cohere(client):
    """Especialista 5: DevOps e Infraestrutura"""
    try:
        resp = await client.post(
            "https://api.cohere.com/v2/chat",
            headers={
                "Authorization": f"Bearer {os.environ['COHERE_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "command-r-plus",
                "messages": [
                    {"role": "system", "content": "Você é um especialista em DevOps e infraestrutura de farms de mineração. Responda em português brasileiro."},
                    {"role": "user", "content": f"""Analise este minerador focando em infraestrutura e escalabilidade:
{PROJECT_CONTEXT}

Analise:
1. DOCKER/K8S: Orquestração de 100+ mineradores
2. CI/CD: Testes automatizados essenciais
3. MONITORING: Prometheus + Grafana para 1000+ GPUs
4. CONFIG MANAGEMENT: TOML adequado para farms?
5. AUTO-SCALING baseado em lucratividade
6. DRIVER MANAGEMENT em escala
7. DISASTER RECOVERY para farms
8. COST OPTIMIZATION: energia, hardware, cloud
9. BARE METAL vs CLOUD para mineração
10. ROADMAP DevOps para operação enterprise"""}
                ]
            },
            timeout=120
        )
        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}: {resp.text[:500]}")
        data = resp.json()
        # Try different response formats
        if "message" in data:
            msg = data["message"]
            if isinstance(msg, dict) and "content" in msg:
                content = msg["content"]
                if isinstance(content, list):
                    result = content[0]["text"] if content else str(data)
                else:
                    result = str(content)
            else:
                result = str(msg)
        elif "text" in data:
            result = data["text"]
        else:
            result = json.dumps(data, indent=2)
        
        with open(f"{RESULTS_DIR}/05_cohere_devops_expert.md", "w") as f:
            f.write(f"# Especialista 5: DevOps e Infraestrutura (Cohere)\n\n{result}\n")
        print("[OK] Cohere")
        return True
    except Exception as e:
        err_msg = f"ERRO Cohere: {e}\n{traceback.format_exc()}"
        print(err_msg[:200])
        with open(f"{RESULTS_DIR}/05_cohere_devops_expert.md", "w") as f:
            f.write(err_msg)
        return False

async def call_openrouter(client):
    """Especialista 6: Estrategista de Inovação"""
    try:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-2.5-flash-preview",
                "messages": [
                    {"role": "system", "content": "Você é um estrategista de inovação em criptomoedas e Web3. Responda em português brasileiro."},
                    {"role": "user", "content": f"""Analise este minerador com visão estratégica:
{PROJECT_CONTEXT}

Analise:
1. FUTURO DA MINERAÇÃO 2025-2030
2. PROOF-OF-USEFUL-WORK: Qubic, Flux, Golem
3. AI + MINING: render farming, training
4. MERGE MINING oportunidades
5. GREEN MINING: sustentabilidade, carbon credits
6. NOVAS BLOCKCHAINS mineráveis PoW
7. FPGA/ASIC: investir mais?
8. COMPETIDORES: XMRig, T-Rex, lolMiner, TeamRedMiner
9. ROADMAP ESTRATÉGICO: features para vantagem competitiva
10. COMUNIDADE open-source"""}
                ],
                "max_tokens": 4000
            },
            timeout=180
        )
        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}: {resp.text[:500]}")
        data = resp.json()
        result = data["choices"][0]["message"]["content"]
        with open(f"{RESULTS_DIR}/06_openrouter_innovation_strategist.md", "w") as f:
            f.write(f"# Especialista 6: Estrategista de Inovação (OpenRouter)\n\n{result}\n")
        print("[OK] OpenRouter")
        return True
    except Exception as e:
        err_msg = f"ERRO OpenRouter: {e}\n{traceback.format_exc()}"
        print(err_msg[:200])
        with open(f"{RESULTS_DIR}/06_openrouter_innovation_strategist.md", "w") as f:
            f.write(err_msg)
        return False

async def main():
    print("=" * 70)
    print("HyperMine Core — Double Check Avassalador v2")
    print("Consultando 6 especialistas via conectores de IA...")
    print("=" * 70)
    
    start = time.time()
    
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            call_perplexity(client),
            call_gemini(client),
            call_grok(client),
            call_anthropic(client),
            call_cohere(client),
            call_openrouter(client),
            return_exceptions=True
        )
    
    elapsed = time.time() - start
    successes = sum(1 for r in results if r is True)
    print(f"\n{'=' * 70}")
    print(f"Consultas concluídas em {elapsed:.1f}s")
    print(f"Sucessos: {successes}/6")
    print(f"Resultados salvos em: {RESULTS_DIR}/")
    
    # List result files
    for f in sorted(os.listdir(RESULTS_DIR)):
        size = os.path.getsize(f"{RESULTS_DIR}/{f}")
        print(f"  {f} ({size} bytes)")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
