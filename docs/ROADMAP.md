# HyperMine Core — Roadmap Detalhado

## Cronograma Geral (40 Semanas)

| Fase | Período | Descrição | Status |
|------|---------|-----------|--------|
| 1 | Semanas 1–4 | Fundação e Infraestrutura | 🔲 Planejado |
| 2 | Semanas 5–12 | Implementação dos Algoritmos | 🔲 Planejado |
| 3 | Semanas 13–16 | Protocolo Stratum e Rede | 🔲 Planejado |
| 4 | Semanas 17–22 | Otimizações Avançadas | 🔲 Planejado |
| 5 | Semanas 23–26 | Configuração e Parametrização | 🔲 Planejado |
| 6 | Semanas 27–30 | Monitoramento e Dashboard | 🔲 Planejado |
| 7 | Semanas 31–36 | Testes e Benchmarks | 🔲 Planejado |
| 8 | Semanas 37–40 | Empacotamento e Distribuição | 🔲 Planejado |

---

## Fase 1 — Fundação e Infraestrutura (Semanas 1–4)

### Semana 1: Setup do Ambiente

A primeira semana é dedicada à configuração completa do ambiente de desenvolvimento. O sistema de build CMake é configurado com suporte a compilação cruzada (Linux x86-64, Linux ARM64, Windows x86-64), integração com o toolchain Rust via `corrosion-rs`, e detecção automática de CUDA e OpenCL. O CI/CD é configurado no GitHub Actions com pipelines para build, testes e benchmarks em cada push.

**Entregas:**
- Repositório inicializado com `.gitignore`, `LICENSE` (MIT), e `README.md`
- `CMakeLists.txt` raiz com detecção de features (SIMD, CUDA, OpenCL)
- `Cargo.toml` workspace com crates para cada módulo Rust
- GitHub Actions workflow para CI/CD
- Dockerfile base para builds reproduzíveis

### Semana 2: Hardware Abstraction Layer (HAL)

A HAL define a interface que todos os backends de hardware devem implementar. Essa interface inclui: `initialize()` para setup do dispositivo, `allocate()` para alocação de memória no dispositivo, `submit()` para envio de trabalho, `synchronize()` para aguardar conclusão, e `get_metrics()` para coleta de métricas.

**Entregas:**
- `hal.hpp` com interface abstrata
- `cpu_backend.cpp` com detecção de CPUID e seleção de SIMD
- `cuda_backend.cu` com gerenciamento de contexto CUDA
- `opencl_backend.cpp` com gerenciamento de plataforma/device OpenCL
- `gpu_info.cpp` com detecção de GPUs e capabilities

### Semana 3: Sistema de Logging e Telemetria

O sistema de logging é implementado com `spdlog` para C++ e `tracing` para Rust, com formatação estruturada (JSON) para integração com ferramentas de análise. As métricas são coletadas em intervalos configuráveis e armazenadas em ring buffers lock-free para evitar impacto na performance de mineração.

**Entregas:**
- Logger unificado C++/Rust com formatação JSON
- Coletor de métricas com ring buffer lock-free
- Métricas de CPU: hashrate, temperatura, frequência, uso
- Métricas de GPU: hashrate, temperatura, power draw, fan speed, memory usage

### Semana 4: Framework de Testes e Benchmarks

O framework de testes utiliza Google Test para C++ e `cargo test` para Rust. O framework de benchmarks utiliza Google Benchmark para microbenchmarks e um sistema custom para benchmarks end-to-end de mineração.

**Entregas:**
- Suite de testes unitários para HAL
- Framework de microbenchmarks para funções hash
- Scripts de benchmark automatizado
- Baseline de performance para comparação futura

---

## Fase 2 — Implementação dos Algoritmos (Semanas 5–12)

### Semanas 5–6: SHA-256 e Derivados

A implementação do SHA-256 é a base para Bitcoin e 25+ outras moedas. São criadas 7 variantes otimizadas, cada uma para um conjunto de instruções diferente. A seleção é feita em runtime via CPUID, sem necessidade de recompilação.

O processo de implementação segue uma abordagem incremental: primeiro a versão genérica (C++ puro) como referência, depois as versões SIMD (SSE4.2 → AVX2 → AVX-512), depois as versões com extensões de hardware (SHA-NI, ARM SHA2), e finalmente a versão Assembly hand-tuned para os hotspots restantes.

**Entregas:**
- 7 variantes de SHA-256 (genérica, SSE4.2, AVX2, AVX-512, SHA-NI, ARM NEON, Assembly)
- Dispatcher automático baseado em CPUID
- Testes de corretude contra vetores de teste oficiais (NIST)
- Benchmarks comparativos entre variantes

### Semanas 7–8: Ethash, Etchash e Algoritmos DAG

A implementação do Ethash requer a geração do DAG (Directed Acyclic Graph), uma estrutura de dados de ~5GB que é recalculada a cada época (~5 dias). A geração do DAG é paralelizada em GPU para completar em segundos ao invés de minutos.

O kernel de mineração implementa o loop de lookup no DAG com 64 acessos pseudo-aleatórios de 128 bytes cada. A otimização principal é o uso de shared memory para cache dos dados mais acessados e prefetching para reduzir a latência dos acessos à memória global.

**Entregas:**
- Gerador de DAG paralelo (CPU e GPU)
- Kernel CUDA otimizado para Ethash/Etchash
- Kernel OpenCL otimizado para Ethash/Etchash
- Suporte a DAG caching para troca rápida entre moedas

### Semanas 9–10: RandomX, Scrypt e Algoritmos Memory-Hard

O RandomX é o algoritmo mais complexo de implementar devido ao seu compilador JIT que gera programas aleatórios em tempo de execução. A implementação inclui backends JIT para x86-64 e ARM64, com otimizações específicas para cada micro-arquitetura.

O Scrypt é implementado com variantes para diferentes parâmetros (N=1024 para Litecoin/Dogecoin, N=2048 para outros), com lookup tables otimizadas para cache L1/L2.

**Entregas:**
- Compilador JIT RandomX para x86-64 e ARM64
- Alocador de Huge Pages com fallback para páginas normais
- Implementação Scrypt com variantes parametrizáveis
- Testes de corretude contra implementações de referência

### Semanas 11–12: KAWPOW, Equihash, X-Series e Demais Algoritmos

As últimas semanas da Fase 2 implementam os algoritmos restantes. O KAWPOW (ProgPoW variant) é implementado com kernels CUDA/OpenCL que utilizam cache L1 do GPU de forma intensiva. O Equihash utiliza o algoritmo de Wagner otimizado com sorting paralelo. A família X11/X13/X16/X17 implementa o encadeamento de funções hash com dados mantidos em registradores SIMD.

**Entregas:**
- Kernels CUDA/OpenCL para KAWPOW, Equihash, Autolykos2, FiroPoW
- Implementação X11/X13/X16/X17 com SIMD
- GhostRider com rotação de 15 algoritmos
- Yescrypt/YesPoWer para CPU
- Testes de corretude para todos os algoritmos

---

## Fase 3 — Protocolo Stratum e Rede (Semanas 13–16)

### Semanas 13–14: Stratum V1

A implementação do Stratum V1 em Rust utiliza `tokio` para I/O assíncrono e `serde_json` para parsing de mensagens JSON-RPC. O parser é otimizado para zero-allocation na maioria dos casos, reutilizando buffers pré-alocados.

**Entregas:**
- Cliente Stratum V1 completo (subscribe, authorize, notify, submit)
- Parser JSON-RPC zero-allocation
- Connection pooling com reconexão automática
- Testes contra pools reais (testnet)

### Semanas 15–16: Stratum V2 e Gerenciamento de Jobs

O Stratum V2 é implementado com framing binário, criptografia TLS 1.3 e suporte ao Job Declaration Protocol. O gerenciamento de jobs utiliza uma fila de prioridade lock-free que descarta jobs stale imediatamente.

**Entregas:**
- Cliente Stratum V2 com framing binário
- TLS 1.3 com 0-RTT resume
- Fila de jobs lock-free com descarte automático de stale jobs
- Failover automático entre pools (<1s de downtime)
- Load balancing configurável entre pools

---

## Fase 4 — Otimizações Avançadas (Semanas 17–22)

### Semanas 17–18: Otimizações de Memória

Implementação de Huge Pages (2MB e 1GB), NUMA-aware allocation, memory pools (arena allocators) e cache line alignment. Cada otimização é medida individualmente para quantificar seu impacto no hashrate.

### Semanas 19–20: Otimizações de GPU

Implementação de persistent kernels, warp-level primitives, shared memory banking optimization e async memory transfers. Profiling com NVIDIA Nsight e AMD CodeXL para identificar e eliminar gargalos.

### Semanas 21–22: Otimizações de Rede e Compilação

Implementação de TCP_NODELAY, kernel bypass (io_uring), submissão especulativa de shares. Configuração de PGO (Profile-Guided Optimization) e LTO (Link-Time Optimization) no pipeline de build.

---

## Fase 5 — Configuração e Parametrização (Semanas 23–26)

### Semanas 23–24: Sistema de Configuração

Implementação do parser TOML com validação de schema, hot-reload via inotify/FSEvents, e sistema de defaults inteligentes que configura automaticamente parâmetros baseado no hardware detectado.

### Semanas 25–26: Configuração por Moeda

Criação dos arquivos de configuração para as 50+ moedas mais populares, com pools recomendados, parâmetros otimizados e documentação inline.

---

## Fase 6 — Monitoramento e Dashboard (Semanas 27–30)

### Semanas 27–28: API REST e Prometheus

Implementação da API REST local com endpoints para métricas, configuração e controle. Exportador Prometheus com métricas customizadas para integração com Grafana.

### Semanas 29–30: Alertas e Notificações

Sistema de alertas com suporte a Discord, Telegram e Slack via webhooks. Alertas configuráveis para temperatura, hashrate, shares rejeitadas e desconexão de pool.

---

## Fase 7 — Testes e Benchmarks (Semanas 31–36)

### Semanas 31–33: Suite de Testes

Testes unitários para cada algoritmo, testes de integração para o pipeline completo de mineração, e testes de stress para operação contínua (72h+).

### Semanas 34–36: Benchmarks e Profiling

Suite completa de benchmarks para cada algoritmo em cada tipo de hardware. Relatório de performance com comparação contra mineradores de referência (XMRig, T-Rex, lolMiner).

---

## Fase 8 — Empacotamento e Distribuição (Semanas 37–40)

### Semanas 37–38: Binários e Docker

Geração de binários pré-compilados para as plataformas mais comuns. Imagens Docker com e sem suporte a CUDA.

### Semanas 39–40: Documentação Final e Release

Documentação completa, guia de início rápido, FAQ, e release v1.0.0 no GitHub com binários, checksums e notas de release.
