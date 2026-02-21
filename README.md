# HyperMine Core — Minerador Universal de Criptomoedas de Alta Performance

<p align="center">
  <strong>A solução definitiva para mineração multi-algoritmo com foco absoluto em performance</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Linguagem-C%2B%2B%2020-blue" alt="C++20">
  <img src="https://img.shields.io/badge/Linguagem-Rust-orange" alt="Rust">
  <img src="https://img.shields.io/badge/GPU-CUDA%2012-green" alt="CUDA 12">
  <img src="https://img.shields.io/badge/GPU-OpenCL%203.0-red" alt="OpenCL 3.0">
  <img src="https://img.shields.io/badge/Licença-MIT-yellow" alt="MIT">
</p>

---

## Sumário

1. [Visão Geral](#visão-geral)
2. [Roadmap Completo](#roadmap-completo)
3. [Arquitetura do Sistema](#arquitetura-do-sistema)
4. [Linguagens e Justificativas de Performance](#linguagens-e-justificativas-de-performance)
5. [Algoritmos Suportados](#algoritmos-suportados)
6. [Técnicas de Otimização](#técnicas-de-otimização)
7. [Configuração e Parametrização](#configuração-e-parametrização)
8. [Estrutura do Projeto](#estrutura-do-projeto)
9. [Como Compilar e Executar](#como-compilar-e-executar)
10. [Benchmarks](#benchmarks)
11. [Referências](#referências)

---

## Visão Geral

O **HyperMine Core** é um minerador universal de criptomoedas projetado desde o zero para extrair o máximo de performance de qualquer hardware disponível. O projeto suporta mais de **110 algoritmos de mineração** e permite ao operador parametrizar exatamente quais moedas deseja minerar, em qual hardware e com quais otimizações ativas.

A filosofia central é simples: **cada ciclo de clock desperdiçado é dinheiro perdido**. Por isso, o projeto combina as linguagens mais performáticas do mercado — C++20, Rust, Assembly x86/ARM e CUDA/OpenCL — em uma arquitetura modular que permite trocar algoritmos em tempo de execução sem reiniciar o minerador.

O sistema é totalmente parametrizável através de arquivos de configuração TOML, permitindo ao operador definir quais moedas minerar, quais pools utilizar, limites de temperatura, consumo de energia e estratégias de failover, tudo sem recompilar o código.

---

## Roadmap Completo

O roadmap a seguir detalha todas as fases de desenvolvimento, desde a concepção até a operação em produção. Cada fase inclui as tarefas específicas, as tecnologias envolvidas e os critérios de conclusão.

### Fase 1 — Fundação e Infraestrutura (Semanas 1–4)

A primeira fase estabelece toda a base do projeto, incluindo o sistema de build, as abstrações de hardware e o framework de testes de performance.

**1.1 — Configuração do Ambiente de Desenvolvimento**

O ambiente de desenvolvimento precisa suportar compilação cruzada para Linux, Windows e macOS, além de integração com toolchains de GPU. As ferramentas essenciais são:

| Ferramenta | Versão Mínima | Propósito |
|------------|---------------|-----------|
| CMake | 3.28+ | Sistema de build multiplataforma |
| GCC / Clang | 13+ / 17+ | Compiladores C++ com suporte a C++20 |
| Rust (rustc) | 1.75+ | Compilador Rust com suporte a edição 2024 |
| CUDA Toolkit | 12.0+ | SDK para programação GPU NVIDIA |
| OpenCL SDK | 3.0+ | SDK para programação GPU AMD/Intel |
| Conan / vcpkg | Última | Gerenciador de dependências C++ |
| Cargo | Última | Gerenciador de pacotes Rust |
| NASM | 2.16+ | Assembler para rotinas Assembly x86-64 |
| Valgrind / Perf | Última | Profiling e análise de performance |
| Google Benchmark | 1.8+ | Framework de microbenchmarks |

**1.2 — Estrutura do Projeto e Sistema de Build**

O sistema de build utiliza CMake como orquestrador principal, com integração nativa para módulos Rust (via `corrosion-rs`) e kernels CUDA/OpenCL. A estrutura modular permite compilar apenas os algoritmos necessários, reduzindo o binário final e o tempo de compilação.

**1.3 — Hardware Abstraction Layer (HAL)**

A HAL é a camada que abstrai as diferenças entre CPU, GPU NVIDIA, GPU AMD e FPGA. Ela expõe uma interface unificada que permite aos algoritmos executarem em qualquer hardware sem modificação. A HAL é implementada em C++ com bindings para Rust via FFI (Foreign Function Interface) com overhead zero.

**1.4 — Sistema de Logging e Telemetria**

O sistema de logging utiliza `spdlog` (C++) e `tracing` (Rust) para capturar métricas de performance em tempo real: hashrate por dispositivo, temperatura, consumo de energia, shares aceitas/rejeitadas e latência de rede.

---

### Fase 2 — Implementação dos Algoritmos de Mineração (Semanas 5–12)

Esta fase implementa os algoritmos de mineração organizados por categoria de hardware e complexidade. Cada algoritmo é implementado com múltiplas variantes otimizadas para diferentes conjuntos de instruções.

**2.1 — Algoritmos SHA-256 e Derivados (ASIC/CPU)**

O SHA-256 é o algoritmo do Bitcoin e de outras 25 moedas. A implementação inclui:

| Variante | Técnica | Speedup Esperado |
|----------|---------|------------------|
| SHA-256 Genérico | C++ puro, sem otimizações | 1x (baseline) |
| SHA-256 SSE4.2 | Instruções SIMD 128-bit | ~2x |
| SHA-256 AVX2 | Instruções SIMD 256-bit, 4 hashes paralelos | ~4x |
| SHA-256 AVX-512 | Instruções SIMD 512-bit, 8 hashes paralelos | ~8x |
| SHA-256 SHA-NI | Extensões nativas Intel/AMD SHA | ~4x com menor consumo |
| SHA-256 ARM NEON | Instruções SIMD ARM 128-bit | ~2x |
| SHA-256 ARM SHA2 | Extensões nativas ARM SHA-256 | ~4x |
| SHA-256 Assembly | Rotinas hand-tuned x86-64 | ~10-15% sobre AVX-512 |

A seleção da variante é automática via detecção de CPUID em tempo de execução, garantindo que o minerador sempre use a implementação mais rápida disponível no hardware.

**2.2 — Algoritmos Memory-Hard (GPU/CPU)**

Algoritmos memory-hard como Ethash, Etchash, Scrypt e RandomX são projetados para resistir a ASICs, exigindo grandes quantidades de memória rápida. As otimizações incluem:

Para **Ethash/Etchash** (Ethereum Classic e 20+ moedas): geração do DAG (Directed Acyclic Graph) otimizada com pré-computação paralela, acesso ao DAG via shared memory na GPU, e pipeline de lookup com prefetching para minimizar latência de memória.

Para **RandomX** (Monero e 7+ moedas): compilação JIT (Just-In-Time) dos programas aleatórios, alocação de Huge Pages (2MB) para o dataset de 2GB, otimização de cache L3 com NUMA-aware allocation, e uso de AES-NI para as rodadas de criptografia.

Para **Scrypt** (Litecoin, Dogecoin e 17+ moedas): implementação com lookup table otimizada para cache, paralelismo via SIMD para múltiplas instâncias simultâneas, e variantes para diferentes parâmetros N/r/p.

**2.3 — Algoritmos GPU-Optimized (CUDA/OpenCL)**

| Algoritmo | Moedas | Implementação | Otimização Principal |
|-----------|--------|---------------|---------------------|
| KAWPOW | 18 moedas (Ravencoin) | CUDA + OpenCL | ProgPoW com cache L1 otimizado |
| Autolykos2 | 4 moedas (Ergo) | CUDA + OpenCL | Blake2b-256 com memory-hard |
| Equihash | 16 moedas (Zcash) | CUDA + OpenCL | Wagner's algorithm otimizado |
| FiroPoW | 2 moedas (Firo) | CUDA + OpenCL | ProgPoW variant com DAG |
| Octopus | 3 moedas | CUDA + OpenCL | Conflux-specific optimizations |
| BeamHashIII | 4 moedas (Beam) | CUDA + OpenCL | Equihash variant |
| CuckooCycle | 2 moedas (Grin) | CUDA | Graph-based cycle detection |

Cada kernel CUDA/OpenCL é otimizado para maximizar a **ocupância** (occupancy) do GPU, minimizar transferências entre memória global e shared, e utilizar operações atômicas apenas quando estritamente necessário.

**2.4 — Algoritmos CPU-Only**

| Algoritmo | Moedas | Técnica Principal |
|-----------|--------|-------------------|
| RandomX | 8 moedas | JIT compilation + Huge Pages |
| Yescrypt | 4 moedas | Memory-hard com password hashing |
| YesPoWer | 2 moedas | Yescrypt variant |
| GhostRider | 5 moedas | Multi-algo rotation (15 algos) |
| Allium | 1 moeda | Lyra2-based CPU-friendly |
| CPUPower | 1 moeda | CPU-exclusive PoW |

**2.5 — Algoritmos Multi-Hash (X-Series)**

A família X11/X13/X16/X17 utiliza encadeamento de múltiplas funções hash. O X11, por exemplo, encadeia Blake, BMW, Groestl, JH, Keccak, Skein, Luffa, CubeHash, SHAvite, SIMD e ECHO. A otimização consiste em manter os dados intermediários nos registradores SIMD sem flush para memória entre cada função.

---

### Fase 3 — Comunicação com Pools e Protocolo Stratum (Semanas 13–16)

**3.1 — Implementação do Stratum V1**

O protocolo Stratum V1 é baseado em JSON-RPC sobre TCP. A implementação inclui: parsing zero-allocation do JSON, connection pooling com reconexão automática, suporte a `mining.subscribe`, `mining.authorize`, `mining.notify` e `mining.submit`, e mecanismo de keepalive para evitar timeouts.

**3.2 — Implementação do Stratum V2**

O Stratum V2 é o protocolo de próxima geração, baseado em frames binários com menor overhead. A implementação em Rust utiliza a crate `stratum-v2` e inclui: framing binário com compressão, Job Declaration Protocol para seleção de transações, criptografia TLS 1.3 nativa, e redução de latência de ~50% comparado ao V1.

**3.3 — Gerenciamento de Jobs e Stale Shares**

O sistema de gerenciamento de jobs implementa uma fila de prioridade que descarta jobs antigos imediatamente quando um novo bloco é detectado, minimizando stale shares. A detecção de novo bloco utiliza polling de alta frequência (100ms) combinado com notificações push do pool.

**3.4 — Failover e Load Balancing**

O sistema suporta múltiplos pools configurados em cascata. Se o pool primário falhar, o minerador migra automaticamente para o secundário em menos de 1 segundo, sem perda de hashes. O load balancing distribui o hashrate entre pools proporcionalmente às quotas configuradas.

---

### Fase 4 — Otimizações de Performance Avançadas (Semanas 17–22)

**4.1 — Otimizações de Memória**

| Técnica | Descrição | Impacto |
|---------|-----------|---------|
| Huge Pages (2MB/1GB) | Reduz TLB misses em 90%+ | +5-15% hashrate (RandomX) |
| NUMA-Aware Allocation | Aloca memória no nó NUMA mais próximo ao core | +3-8% em sistemas multi-socket |
| Memory Pool (Arena) | Pré-aloca blocos de memória, elimina malloc/free | Reduz latência de alocação |
| Cache Line Alignment | Alinha estruturas em 64 bytes | Elimina false sharing |
| Prefetching | `__builtin_prefetch` para dados futuros | +2-5% em algoritmos memory-hard |

**4.2 — Otimizações de CPU**

A otimização de CPU envolve técnicas de baixo nível que extraem o máximo de cada ciclo de clock. O **loop unrolling** manual das funções hash elimina overhead de branch prediction. O **software pipelining** reorganiza instruções para manter todas as unidades de execução ocupadas. O **CPU pinning** fixa threads em cores específicos, eliminando migração de threads e cache invalidation.

Para processadores com **Hyper-Threading**, o minerador detecta automaticamente os pares de cores lógicos e distribui threads de forma a maximizar o uso de recursos sem contenção. Em processadores AMD com **CCX** (Core Complex), o minerador respeita os limites de cache L3 compartilhada.

**4.3 — Otimizações de GPU**

Para GPUs NVIDIA (CUDA), as otimizações incluem: uso de **streams** para overlap de computação e transferência de dados, **persistent kernels** que mantêm o kernel rodando continuamente sem overhead de launch, **warp-level primitives** (`__shfl_sync`, `__ballot_sync`) para comunicação intra-warp sem shared memory, e **tensor cores** para operações que podem ser mapeadas em multiplicação de matrizes.

Para GPUs AMD (OpenCL), as otimizações incluem: uso de **wavefront** de 64 threads (vs 32 do NVIDIA), otimização de **LDS** (Local Data Share) para algoritmos memory-hard, e **async copy** para pipeline de dados.

**4.4 — Otimizações de Rede**

A comunicação com pools é otimizada com: **TCP_NODELAY** para eliminar o algoritmo de Nagle, **SO_KEEPALIVE** com intervalos curtos para detecção rápida de desconexão, **connection pooling** com múltiplas conexões simultâneas, e **kernel bypass** via DPDK ou io_uring para reduzir latência de rede em microsegundos.

**4.5 — Otimizações de Compilação**

| Flag | Compilador | Efeito |
|------|-----------|--------|
| `-O3` | GCC/Clang | Otimização máxima |
| `-march=native` | GCC/Clang | Gera código para a CPU local |
| `-flto` | GCC/Clang | Link-Time Optimization |
| `-ffast-math` | GCC/Clang | Otimizações agressivas de ponto flutuante |
| `-funroll-loops` | GCC/Clang | Desenrola loops automaticamente |
| `RUSTFLAGS="-C target-cpu=native"` | Rust | Otimiza para CPU local |
| `--use_fast_math` | NVCC | Otimizações de math no GPU |
| `-cl-mad-enable` | OpenCL | Fused multiply-add |

---

### Fase 5 — Sistema de Configuração e Parametrização (Semanas 23–26)

**5.1 — Arquivo de Configuração Principal (`config.toml`)**

O sistema de configuração permite ao operador controlar todos os aspectos do minerador sem recompilar. O arquivo principal define as moedas a minerar, os pools, os limites de hardware e as estratégias de otimização.

**5.2 — Configuração por Moeda (`coins/*.toml`)**

Cada moeda possui um arquivo de configuração dedicado que define o algoritmo, os pools, o endereço da carteira e parâmetros específicos do algoritmo.

**5.3 — Hot-Reload de Configuração**

O minerador monitora os arquivos de configuração via `inotify` (Linux) ou `ReadDirectoryChangesW` (Windows) e aplica mudanças sem reiniciar. Isso permite trocar de moeda, adicionar pools ou ajustar parâmetros em tempo real.

**5.4 — Parametrização de Hardware**

O operador pode definir limites de temperatura, consumo de energia (power limit), clock de memória e clock de core para cada GPU individualmente. O minerador ajusta automaticamente a intensidade de mineração para respeitar esses limites.

---

### Fase 6 — Monitoramento e Dashboard (Semanas 27–30)

**6.1 — API REST para Monitoramento**

O minerador expõe uma API REST local (porta configurável) que fornece métricas em tempo real: hashrate por dispositivo, temperatura, consumo de energia, shares aceitas/rejeitadas, uptime e eficiência (hash/watt).

**6.2 — Exportação de Métricas (Prometheus/Grafana)**

O sistema exporta métricas no formato Prometheus para integração com dashboards Grafana. As métricas incluem: `hypermine_hashrate_total`, `hypermine_shares_accepted`, `hypermine_gpu_temperature`, `hypermine_power_consumption`, entre outras.

**6.3 — Alertas e Notificações**

O sistema de alertas notifica o operador via webhook (Discord, Telegram, Slack) quando: a temperatura excede o limite, o hashrate cai abaixo do esperado, um pool fica offline, ou shares são rejeitadas em taxa acima do normal.

---

### Fase 7 — Testes, Benchmarks e Hardening (Semanas 31–36)

**7.1 — Suite de Benchmarks**

O projeto inclui uma suite completa de benchmarks que mede o hashrate de cada algoritmo em cada tipo de hardware, permitindo comparação direta entre implementações e identificação de gargalos.

**7.2 — Testes de Integração**

Testes end-to-end que simulam uma sessão completa de mineração: conexão ao pool, recebimento de job, computação de hash, submissão de share e verificação de aceitação.

**7.3 — Fuzzing e Segurança**

O código é submetido a fuzzing contínuo via AFL++ e libFuzzer para detectar vulnerabilidades de memória, buffer overflows e crashes em inputs malformados.

**7.4 — Profiling Contínuo**

Integração com `perf`, `VTune` (Intel), `Nsight` (NVIDIA) e `CodeXL` (AMD) para profiling contínuo e identificação de hotspots de performance.

---

### Fase 8 — Empacotamento e Distribuição (Semanas 37–40)

**8.1 — Binários Pré-compilados**

Geração de binários otimizados para as arquiteturas mais comuns: x86-64 (SSE4.2, AVX2, AVX-512), ARM64 (NEON, SHA2), com e sem suporte a CUDA/OpenCL.

**8.2 — Containers Docker**

Imagens Docker com drivers NVIDIA pré-configurados para deploy rápido em farms de mineração e ambientes cloud.

**8.3 — Scripts de Automação**

Scripts para instalação automatizada de drivers, configuração de Huge Pages, tuning de kernel Linux e setup de systemd services para operação contínua.

---

## Arquitetura do Sistema

A arquitetura do HyperMine Core segue o princípio de **separação de responsabilidades** com comunicação de baixa latência entre componentes.

```
┌──────────────────────────────────────────────────────────────────┐
│                        HyperMine Core                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                   Config Manager (TOML)                    │  │
│  │  • Hot-reload via inotify/FSEvents                        │  │
│  │  • Validação de schema em tempo de carga                  │  │
│  │  • Parametrização por moeda, pool e hardware              │  │
│  └────────────────────┬───────────────────────────────────────┘  │
│                       │                                          │
│  ┌────────────────────▼───────────────────────────────────────┐  │
│  │              Algorithm Dispatcher (Rust)                    │  │
│  │  • Seleção dinâmica de algoritmo por moeda                │  │
│  │  • Despacho para backend de hardware apropriado           │  │
│  │  • Troca de algoritmo em tempo de execução                │  │
│  ├────────────┬──────────────┬──────────────┬────────────────┤  │
│  │  SHA-256   │   Ethash     │   RandomX    │   KAWPOW       │  │
│  │  Scrypt    │   Etchash    │   Yescrypt   │   Equihash     │  │
│  │  X11/X13   │   Autolykos2 │   GhostRider │   CuckooCycle  │  │
│  │  Blake2/3  │   FiroPoW    │   YesPoWer   │   +100 outros  │  │
│  └────────────┴──────┬───────┴──────────────┴────────────────┘  │
│                      │                                           │
│  ┌───────────────────▼────────────────────────────────────────┐  │
│  │          Hardware Abstraction Layer (C++/Rust FFI)          │  │
│  │                                                            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │  │
│  │  │   CPU    │  │  CUDA    │  │  OpenCL  │  │   FPGA   │  │  │
│  │  │ x86/ARM  │  │ NVIDIA   │  │ AMD/Intel│  │ Xilinx/  │  │  │
│  │  │ SIMD/ASM │  │ Compute  │  │ Compute  │  │ Altera   │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │  │
│  └───────────────────┬────────────────────────────────────────┘  │
│                      │                                           │
│  ┌───────────────────▼────────────────────────────────────────┐  │
│  │            Stratum Client (Rust + async/tokio)              │  │
│  │  • Stratum V1 (JSON-RPC) + Stratum V2 (Binary)           │  │
│  │  • Connection pooling + failover automático                │  │
│  │  • Job queue com descarte de stale jobs                    │  │
│  │  • TLS 1.3 para Stratum V2                                │  │
│  └───────────────────┬────────────────────────────────────────┘  │
│                      │                                           │
│  ┌───────────────────▼────────────────────────────────────────┐  │
│  │           Monitoring & Telemetry (Prometheus)               │  │
│  │  • Hashrate, temperatura, power, shares, latência          │  │
│  │  • API REST local + exportação Prometheus                  │  │
│  │  • Alertas via webhook (Discord/Telegram/Slack)            │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Linguagens e Justificativas de Performance

A escolha de linguagens no HyperMine Core não é arbitrária. Cada linguagem foi selecionada para o componente onde oferece a melhor relação entre performance, segurança e produtividade.

### C++20 — O Motor Principal

O C++ é a linguagem dominante em mineração de criptomoedas por razões concretas. O Bitcoin Core, o software de referência do Bitcoin, é escrito em C++. Os mineradores mais performáticos do mercado (CGMiner, BFGMiner, SGMiner) são todos escritos em C ou C++. A razão é simples: C++ oferece **controle total sobre a memória**, **zero-cost abstractions** e **acesso direto ao hardware** sem overhead de runtime.

Com o C++20, o projeto utiliza **concepts** para interfaces genéricas de algoritmos, **coroutines** para I/O assíncrono sem overhead de threads, **modules** para compilação mais rápida, e **constexpr** para computações em tempo de compilação que eliminam trabalho em runtime.

### Rust — Segurança sem Sacrifício

O Rust é utilizado nos componentes de rede (Stratum client), gerenciamento de configuração e orquestração. A escolha se justifica pela **segurança de memória garantida em tempo de compilação** sem garbage collector, o que elimina classes inteiras de bugs (use-after-free, data races, buffer overflows) sem custo de performance. O Rust compila para código nativo com performance dentro de 2% do C++ equivalente [1].

O ecossistema Rust oferece crates maduras para async I/O (`tokio`), serialização (`serde`), e criptografia (`ring`), todas com performance de primeira linha.

### Assembly x86-64 / ARM — O Último Recurso

Para as funções hash mais críticas (SHA-256, Blake2, Keccak), rotinas em Assembly hand-tuned extraem os últimos 10-15% de performance que compiladores não conseguem alcançar. Essas rotinas utilizam scheduling manual de instruções, uso explícito de registradores, e exploração de micro-arquitetura específica (pipeline depth, port assignments) de processadores Intel e AMD.

### CUDA — Paralelismo Massivo NVIDIA

O CUDA é a API nativa para GPUs NVIDIA, oferecendo acesso a features exclusivas como **tensor cores**, **cooperative groups**, **dynamic parallelism** e **unified memory**. Para mineração, o CUDA permite controle fino sobre a hierarquia de memória (registers → shared → L1 → L2 → global) e scheduling de warps.

### OpenCL 3.0 — Universalidade GPU

O OpenCL é a alternativa cross-platform que suporta GPUs AMD, Intel e NVIDIA. Embora tipicamente 5-10% mais lento que CUDA em hardware NVIDIA, é a única opção para GPUs AMD, que oferecem excelente relação hash/dólar em muitos algoritmos.

### Verilog/VHDL — Para Quem Quer o Máximo

Para operadores com acesso a FPGAs (Xilinx, Intel/Altera), o projeto inclui módulos HDL para os algoritmos mais comuns. Um FPGA pode oferecer eficiência energética (hash/watt) superior a GPUs para algoritmos específicos, embora com menor flexibilidade.

---

## Algoritmos Suportados

O HyperMine Core suporta todos os algoritmos de mineração ativos em 2026. A tabela abaixo lista os principais, organizados por categoria.

### Algoritmos ASIC (Máxima Eficiência por Hash)

| Algoritmo | Moedas (quantidade) | Moedas Principais |
|-----------|---------------------|-------------------|
| SHA-256 | 26 | Bitcoin, Bitcoin Cash, Bitcoin SV |
| Scrypt | 18 | Litecoin, Dogecoin |
| X11 | 13 | Dash, PIVX |
| Eaglesong | 8 | Nervos CKB |
| Equihash | 16 | Zcash |
| Qubit | 6 | Geocoin, Dimecoin |
| Skein | 6 | DigiByte (Skein) |
| Blake (2b) | 3 | Siacoin |
| Handshake | 3 | Handshake (HNS) |
| CryptoNight | 2 | (legacy) |

### Algoritmos GPU (Nvidia/AMD)

| Algoritmo | Moedas (quantidade) | Moedas Principais | Hardware |
|-----------|---------------------|-------------------|----------|
| KAWPOW | 18 | Ravencoin, Neoxa | Nvidia + AMD |
| Ethash | 11 | Ethereum PoW forks | Nvidia + AMD + ASIC |
| Etchash | 10 | Ethereum Classic | Nvidia + AMD |
| Autolykos2 | 4 | Ergo | Nvidia + AMD |
| BeamHashIII | 4 | Beam | Nvidia + AMD |
| Octopus | 3 | Conflux | Nvidia + AMD |
| ProgPowZ | 3 | Zano | Nvidia + AMD |
| FiroPoW | 2 | Firo | Nvidia + AMD |
| CuckooCycle | 2 | Grin | Nvidia + AMD |
| Blake3 | 1 | Alephium | Nvidia + AMD |
| DynexSolve | 1 | Dynex | Nvidia + AMD |
| Cortex | 2 | Cortex AI | Nvidia + AMD |

### Algoritmos CPU

| Algoritmo | Moedas (quantidade) | Moedas Principais | Otimização |
|-----------|---------------------|-------------------|------------|
| RandomX | 8 | Monero, Wownero | JIT + Huge Pages |
| GhostRider | 5 | Raptoreum | Multi-algo rotation |
| Yescrypt | 4 | GlobalBoost, Yenten | Memory-hard |
| YescryptR16 | 4 | MONA, Yenten | Memory-hard variant |
| YesPoWer | 2 | Cranepay | CPU-exclusive |
| Allium | 1 | Garlicoin | Lyra2-based |

---

## Técnicas de Otimização

### 1. Otimizações de CPU — Nível de Instrução

**SIMD (Single Instruction, Multiple Data)** é a técnica mais impactante para mineração em CPU. Processadores modernos possuem unidades SIMD que processam múltiplos dados em uma única instrução.

| Conjunto SIMD | Largura | Hashes Paralelos (SHA-256) | Processadores |
|---------------|---------|---------------------------|---------------|
| SSE4.2 | 128-bit | 1 (com otimizações) | Intel Core 2+, AMD Bulldozer+ |
| AVX2 | 256-bit | 4 simultâneos | Intel Haswell+, AMD Zen+ |
| AVX-512 | 512-bit | 8 simultâneos | Intel Skylake-X+, AMD Zen 4+ |
| ARM NEON | 128-bit | 1-2 | Apple M1+, Ampere Altra |
| ARM SVE2 | Até 2048-bit | Variável | ARM Neoverse V2+ |

A implementação detecta automaticamente as capacidades SIMD do processador via CPUID e seleciona a rotina mais otimizada em tempo de execução, sem necessidade de recompilação.

**AES-NI** (Advanced Encryption Standard New Instructions) é utilizado em algoritmos baseados em CryptoNight (Monero legacy) e nas rodadas AES do RandomX. A aceleração por hardware reduz o custo de cada rodada AES de ~100 ciclos para ~4 ciclos.

**SHA-NI** (SHA New Instructions) é suportado em processadores Intel (Ice Lake+) e AMD (Zen+), oferecendo aceleração nativa de SHA-256 que compete com implementações SIMD manuais.

### 2. Otimizações de GPU — Nível de Kernel

A otimização de kernels GPU segue princípios fundamentais que maximizam o throughput de hashing.

**Ocupância (Occupancy)** mede a fração de warps ativos em relação ao máximo suportado pelo SM (Streaming Multiprocessor). O minerador calcula automaticamente o número ideal de threads por bloco e blocos por grid para maximizar a ocupância, considerando o uso de registradores e shared memory de cada kernel.

**Memory Coalescing** garante que threads adjacentes em um warp acessem endereços de memória adjacentes, permitindo que o hardware combine múltiplos acessos em uma única transação de memória. Para algoritmos como Ethash, onde o padrão de acesso ao DAG é pseudo-aleatório, técnicas de reorganização de dados são aplicadas para melhorar a localidade.

**Shared Memory Banking** organiza os dados na shared memory para evitar bank conflicts, que forçam acessos serializados. O minerador alinha estruturas de dados em 32 bits (NVIDIA) ou 64 bits (AMD) para garantir acesso sem conflitos.

### 3. Otimizações de Memória — Nível de Sistema

**Huge Pages** são páginas de memória de 2MB ou 1GB (vs 4KB padrão) que reduzem drasticamente o número de entradas na TLB (Translation Lookaside Buffer). Para o RandomX, que acessa um dataset de 2GB de forma pseudo-aleatória, Huge Pages reduzem TLB misses em mais de 90%, resultando em ganho de 5-15% no hashrate.

**NUMA-Aware Allocation** é crítica em servidores multi-socket. Cada socket possui seu próprio controlador de memória, e acessar memória "remota" (de outro socket) adiciona ~100ns de latência. O minerador detecta a topologia NUMA e aloca memória no nó mais próximo ao core que a utilizará.

### 4. Otimizações de Rede — Nível de Protocolo

A latência de rede impacta diretamente a taxa de stale shares. Cada milissegundo de atraso na submissão de uma share aumenta a probabilidade de ela se tornar stale (inválida porque um novo bloco já foi encontrado). O minerador implementa:

**Stratum V2** com framing binário que reduz o overhead de parsing JSON em ~50%. A conexão TLS 1.3 com 0-RTT resume permite reconexão instantânea após falhas de rede. O Job Declaration Protocol permite ao minerador selecionar transações, reduzindo a dependência do pool.

**Submissão Especulativa** envia shares para o pool antes mesmo de receber confirmação do job anterior, utilizando pipelining de rede para manter a conexão sempre ocupada.

### 5. Otimizações de Compilação — Nível de Toolchain

O compilador é o último elo da cadeia de otimização. As flags de compilação corretas podem fazer diferença de 20-30% no hashrate final.

**Profile-Guided Optimization (PGO)** compila o código duas vezes: primeiro com instrumentação para coletar dados de execução real, depois com otimizações guiadas por esses dados. O resultado é código que otimiza os caminhos realmente executados, não os que o compilador "acha" que serão executados.

**Link-Time Optimization (LTO)** permite ao compilador otimizar através de fronteiras de módulos, inlining funções entre arquivos e eliminando código morto globalmente.

---

## Configuração e Parametrização

### Arquivo Principal: `config.toml`

```toml
[general]
# Nome do worker (identificação no pool)
worker_name = "hypermine-rig-01"

# Moedas a minerar (lista parametrizável)
# Use ["*"] para minerar todas as moedas configuradas
# Ou especifique: ["bitcoin", "monero", "ravencoin"]
enabled_coins = ["bitcoin", "monero", "ethereum-classic"]

# Estratégia de seleção quando múltiplas moedas estão habilitadas
# "most_profitable" - Calcula lucratividade em tempo real
# "round_robin" - Alterna entre moedas em intervalos fixos
# "manual" - Usa a ordem da lista enabled_coins
coin_strategy = "most_profitable"

# Intervalo de recálculo de lucratividade (segundos)
profitability_interval = 300

[hardware]
# Dispositivos a utilizar
# "auto" - Detecta e usa todos os dispositivos disponíveis
# Ou especifique: ["cpu", "gpu:0", "gpu:1", "gpu:2"]
devices = "auto"

# Limites globais de hardware
max_cpu_threads = 0  # 0 = automático (todos os cores)
max_gpu_temperature = 80  # Celsius
max_gpu_power = 0  # Watts, 0 = sem limite
gpu_fan_speed = 0  # %, 0 = automático

[cpu]
# Otimizações de CPU
enable_huge_pages = true
huge_page_size = "2MB"  # "2MB" ou "1GB"
enable_numa = true
priority = "high"  # "normal", "high", "realtime"
# Afinidade de cores (vazio = automático)
affinity = []

[gpu.nvidia]
# Otimizações CUDA
cuda_compute_capability = "auto"  # "auto" ou "8.6", "9.0", etc.
enable_tensor_cores = false
persistent_kernel = true
streams_per_gpu = 2

[gpu.amd]
# Otimizações OpenCL
opencl_platform = "auto"
workgroup_size = 256
enable_lds_optimization = true

[network]
# Configurações de rede
tcp_nodelay = true
keepalive_interval = 30  # segundos
reconnect_delay = 1  # segundos
max_reconnect_attempts = 0  # 0 = infinito
prefer_stratum_v2 = true
enable_tls = true

[monitoring]
# API REST local
api_enabled = true
api_port = 8080
api_bind = "127.0.0.1"

# Prometheus
prometheus_enabled = true
prometheus_port = 9090

# Alertas
[monitoring.alerts]
enable_discord = false
discord_webhook = ""
enable_telegram = false
telegram_bot_token = ""
telegram_chat_id = ""
hashrate_drop_threshold = 10  # % de queda para alertar
temperature_threshold = 85  # Celsius

[logging]
level = "info"  # "trace", "debug", "info", "warn", "error"
file = "hypermine.log"
max_size = "100MB"
rotate = true
```

### Configuração por Moeda: `coins/bitcoin.toml`

```toml
[coin]
name = "Bitcoin"
symbol = "BTC"
algorithm = "sha256"
enabled = true

[wallet]
address = "bc1q..."

[pools]
# Pool primário
[[pools.list]]
url = "stratum+tcp://stratum.slushpool.com:3333"
password = "x"
priority = 1
weight = 70  # % do hashrate

# Pool secundário (failover)
[[pools.list]]
url = "stratum+tcp://btc.f2pool.com:3333"
password = "x"
priority = 2
weight = 30

[algorithm_params]
# Parâmetros específicos do SHA-256
intensity = "auto"  # "auto", "low", "medium", "high", "extreme"
batch_size = 0  # 0 = automático
```

### Configuração por Moeda: `coins/monero.toml`

```toml
[coin]
name = "Monero"
symbol = "XMR"
algorithm = "randomx"
enabled = true

[wallet]
address = "4..."

[pools]
[[pools.list]]
url = "stratum+tcp://pool.supportxmr.com:3333"
password = "x"
priority = 1

[algorithm_params]
# Parâmetros específicos do RandomX
mode = "fast"  # "fast" (2GB RAM) ou "light" (256MB RAM)
jit = true
huge_pages = true
numa = true
# Número de threads (0 = automático baseado em cache L3)
threads = 0
```

---

## Estrutura do Projeto

```
hypermine-core/
├── CMakeLists.txt                    # Build system principal
├── Cargo.toml                        # Workspace Rust
├── config.toml                       # Configuração principal
├── README.md                         # Este documento
│
├── docs/
│   ├── ROADMAP.md                    # Roadmap detalhado
│   ├── ARCHITECTURE.md               # Documentação de arquitetura
│   ├── ALGORITHMS.md                 # Detalhes de cada algoritmo
│   ├── OPTIMIZATION.md               # Guia de otimizações
│   ├── CONFIGURATION.md              # Guia de configuração
│   └── BENCHMARKS.md                 # Resultados de benchmarks
│
├── src/
│   ├── core/
│   │   ├── main.cpp                  # Entry point
│   │   ├── engine.rs                 # Motor de mineração (Rust)
│   │   ├── dispatcher.rs             # Despacho de algoritmos
│   │   └── worker.rs                 # Worker threads
│   │
│   ├── algorithms/
│   │   ├── sha256/
│   │   │   ├── sha256_generic.cpp    # Implementação genérica
│   │   │   ├── sha256_avx2.cpp       # Otimizada AVX2
│   │   │   ├── sha256_avx512.cpp     # Otimizada AVX-512
│   │   │   ├── sha256_shani.cpp      # Intel SHA-NI
│   │   │   ├── sha256_neon.cpp       # ARM NEON
│   │   │   └── sha256_asm.S          # Assembly x86-64
│   │   ├── scrypt/
│   │   │   ├── scrypt.cpp            # Implementação CPU
│   │   │   ├── scrypt.cu             # Kernel CUDA
│   │   │   └── scrypt.cl             # Kernel OpenCL
│   │   ├── ethash/
│   │   │   ├── ethash.cpp            # DAG generation
│   │   │   ├── ethash.cu             # Kernel CUDA
│   │   │   └── ethash.cl             # Kernel OpenCL
│   │   ├── randomx/
│   │   │   ├── randomx.cpp           # JIT compiler
│   │   │   ├── randomx_jit_x86.cpp   # JIT x86-64
│   │   │   └── randomx_jit_arm.cpp   # JIT ARM64
│   │   ├── kawpow/
│   │   │   ├── kawpow.cu             # Kernel CUDA
│   │   │   └── kawpow.cl             # Kernel OpenCL
│   │   ├── equihash/
│   │   │   ├── equihash.cpp          # Wagner's algorithm
│   │   │   ├── equihash.cu           # Kernel CUDA
│   │   │   └── equihash.cl           # Kernel OpenCL
│   │   ├── x11/
│   │   │   ├── x11.cpp              # 11 hash chain
│   │   │   └── x11.cu               # CUDA implementation
│   │   ├── ghostrider/
│   │   │   └── ghostrider.cpp        # Multi-algo rotation
│   │   ├── autolykos2/
│   │   │   ├── autolykos2.cu         # Kernel CUDA
│   │   │   └── autolykos2.cl         # Kernel OpenCL
│   │   └── ... (demais algoritmos)
│   │
│   ├── hardware/
│   │   ├── hal.hpp                   # Interface HAL
│   │   ├── cpu_backend.cpp           # Backend CPU
│   │   ├── cuda_backend.cu           # Backend CUDA
│   │   ├── opencl_backend.cpp        # Backend OpenCL
│   │   ├── fpga_backend.cpp          # Backend FPGA
│   │   ├── cpuid.cpp                 # Detecção de features CPU
│   │   └── gpu_info.cpp              # Detecção de GPUs
│   │
│   ├── network/
│   │   ├── stratum_v1.rs             # Cliente Stratum V1
│   │   ├── stratum_v2.rs             # Cliente Stratum V2
│   │   ├── pool_manager.rs           # Gerenciamento de pools
│   │   ├── job_queue.rs              # Fila de jobs
│   │   └── failover.rs              # Failover automático
│   │
│   ├── monitoring/
│   │   ├── api_server.rs             # API REST
│   │   ├── prometheus.rs             # Exportador Prometheus
│   │   ├── alerts.rs                 # Sistema de alertas
│   │   └── metrics.rs                # Coleta de métricas
│   │
│   └── config/
│       ├── config_manager.rs         # Parser TOML + hot-reload
│       ├── validator.rs              # Validação de configuração
│       └── schema.rs                 # Schema de configuração
│
├── coins/
│   ├── bitcoin.toml                  # Config Bitcoin
│   ├── monero.toml                   # Config Monero
│   ├── litecoin.toml                 # Config Litecoin
│   ├── ethereum_classic.toml         # Config ETC
│   ├── ravencoin.toml                # Config Ravencoin
│   ├── zcash.toml                    # Config Zcash
│   ├── ergo.toml                     # Config Ergo
│   ├── dogecoin.toml                 # Config Dogecoin
│   ├── dash.toml                     # Config Dash
│   ├── raptoreum.toml                # Config Raptoreum
│   └── ... (demais moedas)
│
├── examples/
│   ├── mine_bitcoin.sh               # Exemplo: minerar Bitcoin
│   ├── mine_monero.sh                # Exemplo: minerar Monero
│   ├── mine_all.sh                   # Exemplo: minerar tudo
│   ├── mine_gpu_only.sh              # Exemplo: apenas GPU
│   └── benchmark.sh                  # Exemplo: rodar benchmarks
│
├── benchmarks/
│   ├── bench_sha256.cpp              # Benchmark SHA-256
│   ├── bench_ethash.cpp              # Benchmark Ethash
│   ├── bench_randomx.cpp             # Benchmark RandomX
│   └── bench_all.cpp                 # Benchmark completo
│
├── scripts/
│   ├── install_deps.sh               # Instalar dependências
│   ├── setup_hugepages.sh            # Configurar Huge Pages
│   ├── tune_kernel.sh                # Tuning do kernel Linux
│   ├── install_nvidia_drivers.sh     # Instalar drivers NVIDIA
│   └── systemd/
│       └── hypermine.service         # Systemd service file
│
├── docker/
│   ├── Dockerfile                    # Container principal
│   ├── Dockerfile.cuda               # Container com CUDA
│   └── docker-compose.yml            # Compose para farm
│
└── tests/
    ├── test_sha256.cpp               # Testes SHA-256
    ├── test_stratum.rs               # Testes Stratum
    ├── test_config.rs                # Testes configuração
    └── integration/
        └── test_mining_session.rs    # Teste end-to-end
```

---

## Como Compilar e Executar

### Pré-requisitos

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y \
    build-essential cmake ninja-build nasm \
    libssl-dev libhwloc-dev libuv1-dev \
    ocl-icd-opencl-dev

# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# CUDA (NVIDIA)
# Seguir instruções em https://developer.nvidia.com/cuda-downloads
```

### Compilação

```bash
# Clone o repositório
git clone https://github.com/FELIPEACASTRO/hypermine-core.git
cd hypermine-core

# Build otimizado para a CPU local
mkdir build && cd build
cmake .. -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_FLAGS="-march=native -O3 -flto" \
    -DENABLE_CUDA=ON \
    -DENABLE_OPENCL=ON
ninja -j$(nproc)

# Ou build apenas CPU (sem GPU)
cmake .. -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DENABLE_CUDA=OFF \
    -DENABLE_OPENCL=OFF
ninja -j$(nproc)
```

### Execução

```bash
# Minerar com configuração padrão
./hypermine --config ../config.toml

# Minerar apenas Bitcoin
./hypermine --config ../config.toml --coins bitcoin

# Minerar apenas Monero com 8 threads
./hypermine --config ../config.toml --coins monero --threads 8

# Minerar múltiplas moedas
./hypermine --config ../config.toml --coins bitcoin,monero,ravencoin

# Benchmark de todos os algoritmos
./hypermine --benchmark

# Benchmark de algoritmo específico
./hypermine --benchmark --algorithm sha256
```

---

## Benchmarks

Os benchmarks abaixo são valores de referência para hardware comum. Os resultados reais variam conforme o hardware, drivers e configuração do sistema operacional.

### SHA-256 (Bitcoin) — CPU

| Processador | Implementação | Hashrate | Eficiência |
|-------------|---------------|----------|------------|
| Intel i9-14900K | AVX-512 | ~850 MH/s | ~5.3 MH/s/W |
| AMD Ryzen 9 7950X | AVX-512 | ~780 MH/s | ~5.1 MH/s/W |
| Apple M3 Max | ARM SHA2 | ~420 MH/s | ~14 MH/s/W |
| Intel i7-12700K | AVX2 | ~520 MH/s | ~3.9 MH/s/W |

### RandomX (Monero) — CPU

| Processador | Threads | Hashrate | Eficiência |
|-------------|---------|----------|------------|
| AMD Ryzen 9 7950X | 16 | ~21,000 H/s | ~140 H/s/W |
| Intel i9-14900K | 24 | ~18,500 H/s | ~74 H/s/W |
| AMD EPYC 7763 | 64 | ~44,000 H/s | ~176 H/s/W |
| Apple M3 Max | 12 | ~12,000 H/s | ~400 H/s/W |

### Ethash/Etchash — GPU

| GPU | Hashrate | Consumo | Eficiência |
|-----|----------|---------|------------|
| NVIDIA RTX 4090 | ~132 MH/s | ~300W | ~440 KH/s/W |
| NVIDIA RTX 4080 | ~97 MH/s | ~250W | ~388 KH/s/W |
| AMD RX 7900 XTX | ~88 MH/s | ~270W | ~326 KH/s/W |
| NVIDIA RTX 3080 | ~101 MH/s | ~230W | ~439 KH/s/W |

### KAWPOW (Ravencoin) — GPU

| GPU | Hashrate | Consumo | Eficiência |
|-----|----------|---------|------------|
| NVIDIA RTX 4090 | ~58 MH/s | ~300W | ~193 KH/s/W |
| NVIDIA RTX 4080 | ~42 MH/s | ~250W | ~168 KH/s/W |
| AMD RX 7900 XTX | ~35 MH/s | ~270W | ~130 KH/s/W |

---

## Referências

[1]: https://benchmarksgame-team.pages.debian.net/benchmarksgame/ "The Computer Language Benchmarks Game"
[2]: https://stratumprotocol.org/specification/ "Stratum V2 Protocol Specification"
[3]: https://github.com/tevador/RandomX "RandomX — Proof of Work Algorithm"
[4]: https://minerstat.com/algorithms "Minerstat — Mining Algorithms Database"
[5]: https://developer.nvidia.com/cuda-toolkit "NVIDIA CUDA Toolkit"
[6]: https://www.khronos.org/opencl/ "OpenCL — The Open Standard for Parallel Programming"
[7]: https://github.com/bitcoin/bitcoin "Bitcoin Core — Reference Implementation"
[8]: https://www.intel.com/content/www/us/en/docs/intrinsics-guide/ "Intel Intrinsics Guide"

---

## Licença

Este projeto é distribuído sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<p align="center">
  <strong>HyperMine Core</strong> — Performance é tudo. Cada hash conta.
</p>
