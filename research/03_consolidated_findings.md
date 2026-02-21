# Descobertas Consolidadas — Double Check Avassalador

## Fontes Consultadas
- 6 Especialistas via Google Gemini (Blockchain, Arquitetura, GPU, Segurança, DevOps, Inovação)
- Coin Bureau (Feb 2026), Minerstat, CoinSpeaker, NFTPlazas, CryptoMus
- Pesquisas web sobre algoritmos, hardware e tendências 2025-2026

## MOEDAS E ALGORITMOS ATUALIZADOS (2025-2026)

### Moedas Confirmadas (já no projeto)
- Bitcoin (BTC) — SHA-256 — ASIC dominado
- Monero (XMR) — RandomX — CPU-hard
- Litecoin (LTC) — Scrypt — ASIC dominado
- Ethereum Classic (ETC) — Etchash — GPU
- Ravencoin (RVN) — KAWPOW — GPU
- Zcash (ZEC) — Equihash — GPU/ASIC
- Ergo (ERG) — Autolykos2 — GPU
- Dogecoin (DOGE) — Scrypt — ASIC (merge mining com LTC)
- Dash (DASH) — X11 — ASIC dominado
- Raptoreum (RTM) — GhostRider — CPU
- Firo (FIRO) — FiroPoW — GPU

### MOEDAS FALTANTES (CRÍTICAS para adicionar)
- **Kaspa (KAS)** — kHeavyHash — GPU/ASIC — Top 30 market cap, muito lucrativa
- **Alephium (ALPH)** — Blake3 — GPU — Sharding PoW, crescente
- **Nexa (NEXA)** — NexaPoW — GPU — Alta lucratividade
- **Karlsen (KLS)** — KarlsenHash — GPU — Fork de Kaspa
- **Pyrin (PYI)** — PyrinHash — GPU — Fork de Kaspa
- **VerusCoin (VRSC)** — VerusHash 2.2 — CPU — Líder CPU mining
- **Flux (FLUX)** — ZelHash (Equihash variant) — GPU
- **Vertcoin (VTC)** — Verthash — GPU — ASIC-resistant
- **Fren (FREN)** — FrenHash — GPU — Emergente
- **Neoxa (NEOX)** — KAWPOW variant — GPU
- **Clore.ai (CLORE)** — KAWPOW — GPU + PoUW
- **Qubic (QUBIC)** — AigarHash — CPU — Proof-of-Useful-Work

### ALGORITMOS FALTANTES
- kHeavyHash (Kaspa)
- Blake3 (Alephium)
- NexaPoW (Nexa)
- KarlsenHash (Karlsen)
- PyrinHash (Pyrin)
- VerusHash 2.2 (VerusCoin)
- ZelHash (Flux)
- Verthash (Vertcoin)
- AigarHash (Qubic)

## HARDWARE ATUALIZADO 2025-2026

### GPUs (Ranking por lucratividade minerstat Feb 2026)
1. NVIDIA RTX 4090 — $2.73/dia
2. NVIDIA RTX 5090 — $1.63/dia (Blackwell, GDDR7)
3. NVIDIA RTX 3090 — $1.22/dia
4. NVIDIA RTX 5080 — $1.12/dia
5. AMD RX 7900 XTX — relevante
6. Intel Arc Battlemage — emergente

### CPUs
- AMD Ryzen 9 9950X (Zen 5) — melhor para RandomX
- AMD Ryzen 9 7950X3D (3D V-Cache) — excelente para RandomX
- Intel Arrow Lake — melhorias em IPC

## CORREÇÕES E MELHORIAS IDENTIFICADAS PELOS ESPECIALISTAS

### Arquitetura
- Adicionar sistema de plugins (DSOs/DLLs) para algoritmos
- Formalizar HAL com suporte a AVX10, AMX, ARM SVE/SVE2
- Adicionar CUDA Graphs como mandatório
- Considerar HIP/ROCm como alternativa ao OpenCL para AMD
- Adicionar BOLT (Binary Optimization and Layout Tool) ao pipeline
- Adicionar AutoFDO como alternativa ao PGO
- Considerar CXL memory para algoritmos memory-hard

### Segurança
- Implementar NOISE protocol para Stratum V2 (não apenas TLS)
- Certificate pinning para pools
- Criptografia de endereços de carteira no config
- Assinatura de código (code signing) dos binários
- API REST com autenticação JWT e rate limiting
- Verificação de integridade em runtime
- Supply chain security (cargo-audit, dependabot)

### DevOps
- Ansible para gerenciamento de farms (não K8s para nós de mineração)
- K8s apenas para serviços de suporte (Prometheus, Grafana)
- Testes de regressão de performance no CI/CD
- DCGM Exporter para métricas NVIDIA
- Nomad como alternativa leve ao K8s para bare metal

### Estratégia
- Merge mining (LTC+DOGE, etc.) — OMISSÃO GRAVE no projeto atual
- Proof-of-Useful-Work (PoUW) — tendência futura crítica
- AI + Mining — render farming, inferência
- Green Mining — métricas de eficiência energética
- Rebranding como "orquestrador de computação distribuída"

### Benchmarks Corrigidos
- SHA-256 em GPU é economicamente inviável (ASIC dominado)
- RTX 5090 rende ~$1.63/dia em mineração GPU
- RTX 4090 ainda é a GPU mais lucrativa
