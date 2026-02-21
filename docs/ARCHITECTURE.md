# HyperMine Core — Arquitetura do Sistema

**Versão:** 2.0 (Validado por Especialistas — Fevereiro 2026)

---

## Visão Geral da Arquitetura

O HyperMine Core utiliza uma arquitetura em camadas projetada para maximizar performance e modularidade. A arquitetura foi validada por um Arquiteto de Sistemas de Alta Performance e um Especialista em GPU Computing como "fundamentalmente correta e robusta".

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA DE APRESENTAÇÃO                       │
│  REST API · Prometheus Exporter · Discord/Telegram Webhooks     │
│  Grafana Dashboards · CLI Interface · Web Dashboard             │
├─────────────────────────────────────────────────────────────────┤
│                    CAMADA DE CONTROLE (Rust)                    │
│  Stratum V1/V2 Client · NOISE Protocol · TLS 1.3               │
│  Config Manager · Profit Switcher · Merge Mining Controller     │
│  Pool Failover (<1s) · Certificate Pinning · JWT Auth API       │
├─────────────────────────────────────────────────────────────────┤
│              CAMADA DE AGENDAMENTO (Scheduler/Dispatcher)       │
│  Lock-free Task Queue · Adaptive Tuning · Hot-swap de Kernels   │
│  Resource Allocator (CPU/GPU/MEM) · Priority Manager            │
├─────────────────────────────────────────────────────────────────┤
│                CAMADA DE ALGORITMOS (Plugin System)              │
│  42+ Algoritmos como DSOs/DLLs carregáveis dinamicamente        │
│  SHA-256 · RandomX · Etchash · KAWPOW · Equihash · kHeavyHash  │
│  Blake3 · NexaPoW · KarlsenHash · PyrinHash · VerusHash 2.2    │
│  Autolykos2 · GhostRider · FiroPoW · ZelHash · Verthash · ...  │
├─────────────────────────────────────────────────────────────────┤
│            CAMADA DE ABSTRAÇÃO DE HARDWARE (HAL) — C++20        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │ CPU HAL  │ │ NVIDIA   │ │ AMD HAL  │ │ Intel HAL        │   │
│  │ SIMD x9  │ │ CUDA 12  │ │ HIP/ROCm │ │ OpenCL 3.0       │   │
│  │ NUMA     │ │ Graphs   │ │ RDNA/CDNA│ │ oneAPI/Battlemage │   │
│  │ HugePages│ │ Tensor   │ │ Matrix   │ │ Xe Cores         │   │
│  │ CXL Mem  │ │ NVLink   │ │ Infinity │ │                  │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                  CAMADA DE TELEMETRIA                            │
│  Ring Buffers · Lock-free Queues · DCGM Exporter (NVIDIA)       │
│  ROCm SMI (AMD) · Métricas hash/watt · Alertas Inteligentes    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Divisão de Linguagens

A escolha de linguagens foi validada como "quase ideal" pelo Arquiteto de Sistemas. Zig e Carbon foram avaliados mas considerados prematuros para produção.

| Camada | Linguagem | Justificativa Técnica |
|---|---|---|
| Kernels de Hashing | C++20 | Zero-overhead abstractions, controle granular de memória, interop nativo com CUDA/HIP. Templates e constexpr para otimizações em compile-time. |
| Kernels GPU | CUDA C / HIP C | Acesso direto ao hardware NVIDIA (CUDA 12) e AMD (HIP/ROCm 6). Suporte a CUDA Graphs, Cooperative Groups, Tensor Cores. |
| Hotspots Críticos | Assembly x86-64 | Rotinas hand-tuned para loops internos de hash onde cada ciclo de clock importa. SHA-256 com SHA-NI, AES com AES-NI. |
| Networking | Rust | Segurança de memória sem GC, concorrência segura com async/await (tokio), eliminação de data races em compile-time. |
| Configuração | Rust | Parsing seguro de TOML com serde, validação de tipos em compile-time, error handling robusto com Result. |
| Monitoramento | Rust | Thread safety garantida pelo borrow checker, integração nativa com Prometheus via crate `prometheus`. |
| Scheduler | Rust + C++ FFI | Lock-free queues implementadas em C++ para máxima performance, orquestração segura em Rust via FFI com overhead zero. |

---

## Componentes Principais

### 1. Config Manager (Rust)

O Config Manager carrega, valida e distribui configurações para todos os componentes. Ele monitora arquivos via `inotify` (Linux) ou `ReadDirectoryChangesW` (Windows) para hot-reload. A configuração é hierárquica: CLI > variáveis de ambiente > `config.toml` > defaults.

### 2. Engine (Rust + C++ FFI)

O Engine coordena todo o processo de mineração em um loop event-driven single-threaded que coordena Workers multi-threaded. Essa arquitetura evita locks no caminho crítico e minimiza latência.

### 3. Algorithm Dispatcher (Plugin System)

Os algoritmos são implementados como plugins carregáveis dinamicamente (DSOs no Linux, DLLs no Windows). Cada plugin exporta uma interface C padronizada, permitindo adicionar novos algoritmos sem recompilar o minerador.

### 4. Worker Pool

Cada Worker é fixado a um core específico (CPU pinning) e possui seu próprio contexto de execução. Para GPUs, cada Worker gerencia streams CUDA / command queues HIP/OpenCL com overlap de compute e memcpy.

### 5. Hardware Abstraction Layer (HAL) — C++20

A HAL expõe uma interface unificada para todos os backends:

```cpp
class IHardwareBackend {
public:
    virtual ~IHardwareBackend() = default;
    virtual bool initialize() = 0;
    virtual DeviceInfo get_device_info() const = 0;
    virtual void* allocate(size_t bytes, AllocFlags flags) = 0;
    virtual void deallocate(void* ptr) = 0;
    virtual void submit_work(const WorkItem& work) = 0;
    virtual void synchronize() = 0;
    virtual Metrics get_metrics() const = 0;
};
```

### 6. Stratum Client (Rust)

Implementado com `tokio` para I/O assíncrono. Suporta Stratum V1 (JSON-RPC) e V2 (binário + NOISE). Comunicação com Engine via channels lock-free (`crossbeam-channel`).

---

## CPU HAL — 9 Variantes SIMD

| Prioridade | ISA | Detecção | Largura |
|---|---|---|---|
| 1 | AVX-512 + SHA-NI | CPUID.7.0:EBX[16] + [29] | 512-bit |
| 2 | AVX-512 | CPUID.7.0:EBX[16] | 512-bit |
| 3 | AVX10 | CPUID.7.1:EDX[19] | 256/512-bit |
| 4 | AVX2 + SHA-NI | CPUID.7.0:EBX[5] + [29] | 256-bit |
| 5 | AVX2 | CPUID.7.0:EBX[5] | 256-bit |
| 6 | AMX | CPUID.7.0:EDX[22] | Matrix |
| 7 | SSE4.2 | CPUID.1:ECX[20] | 128-bit |
| 8 | ARM SVE2 | HWCAP2_SVE2 | Scalable |
| 9 | ARM NEON | HWCAP_NEON | 128-bit |

---

## GPU HAL — 3 Backends

| Backend | Hardware | Otimizações |
|---|---|---|
| CUDA 12 | NVIDIA (Ada, Blackwell, Ampere) | CUDA Graphs, Tensor Cores, NVLink, Cooperative Groups, Persistent Kernels |
| HIP/ROCm 6 | AMD (RDNA 3/4, CDNA 3) | Matrix Accelerators, Infinity Fabric, wavefront 64, LDS optimization |
| OpenCL 3.0 | Intel (Battlemage, Xe), Universal | Xe Cores, oneAPI/SYCL fallback, async copy |

---

## Fluxo de Dados

### Pipeline de Mineração

```
Pool → Stratum Client (Rust) → Job Queue (Lock-free)
                                      ↓
                              Scheduler/Dispatcher
                                      ↓
                    ┌─────────────────────────────────┐
                    │  HAL seleciona backend optimal   │
                    │  CPU: SIMD dispatch via CPUID    │
                    │  GPU: CUDA/HIP/OpenCL dispatch   │
                    └─────────────────────────────────┘
                                      ↓
                          Algorithm Plugin (DSO/DLL)
                                      ↓
                          Hash computation (hot loop)
                                      ↓
                    Nonce found? → Submit share → Pool
```

### Troca de Algoritmo (Profit Switcher)

```
1. Profit Switcher consulta APIs de lucratividade
2. Calcula rentabilidade por algoritmo/moeda (incluindo merge mining)
3. Se moeda mais lucrativa != moeda atual:
   a. Descarrega plugin do algoritmo atual
   b. Carrega plugin do novo algoritmo (DSO/DLL)
   c. Reconecta ao pool da nova moeda
   d. Inicia mineração sem downtime significativo
```

---

## Decisões de Design

### Por que C++ e Rust juntos?

C++ é utilizado nos componentes que exigem controle absoluto sobre o hardware: algoritmos de hashing, kernels GPU e interação com drivers. Rust é utilizado nos componentes que se beneficiam de segurança de memória: networking, parsing de configuração e gerenciamento de estado. A interface FFI tem overhead zero — é uma chamada de função normal no nível de assembly.

### Por que não Go, Java ou Python?

Go possui garbage collector que causa pausas imprevisíveis. Java tem o mesmo problema, agravado pelo JIT warmup. Python é ~100x mais lento para computação numérica. Essas linguagens são adequadas para ferramentas auxiliares, mas não para o caminho crítico de mineração.

### Por que lock-free data structures?

Locks causam contenção quando múltiplas threads competem pelo mesmo recurso. Em um minerador com 16+ threads de CPU e 8+ streams de GPU, a contenção pode reduzir o hashrate em 5-10%. Estruturas lock-free eliminam esse problema.

### Por que plugins (DSO/DLL)?

Plugins permitem adicionar novos algoritmos sem recompilar o minerador, carregar apenas os algoritmos necessários (reduzindo uso de memória), e atualizar algoritmos individualmente sem downtime.
