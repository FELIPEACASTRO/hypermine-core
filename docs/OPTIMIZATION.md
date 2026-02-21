# HyperMine Core — Guia de Otimizações de Performance

Este documento detalha todas as técnicas de otimização implementadas no HyperMine Core, organizadas por nível de abstração.

## 1. Otimizações de Nível de Instrução (CPU)

### 1.1 SIMD — Single Instruction, Multiple Data

SIMD é a técnica de maior impacto para mineração em CPU. A ideia é processar múltiplos hashes independentes em paralelo usando registradores vetoriais largos.

| Tecnologia | Largura | Registradores | Hashes Paralelos (SHA-256) | Speedup |
|------------|---------|---------------|---------------------------|---------|
| SSE4.2 | 128-bit | 16 x XMM | 1 (otimizado) | ~1.5x |
| AVX2 | 256-bit | 16 x YMM | 4 | ~3.5x |
| AVX-512 | 512-bit | 32 x ZMM | 8 | ~7x |
| ARM NEON | 128-bit | 32 x V | 1-2 | ~1.5x |
| ARM SVE2 | Até 2048-bit | 32 x Z | Variável | ~4-8x |

A detecção de capabilities é feita em runtime via instrução CPUID (x86) ou leitura de `/proc/cpuinfo` e `getauxval(AT_HWCAP)` (ARM). O dispatcher seleciona a implementação mais rápida disponível sem necessidade de recompilação.

### 1.2 Extensões de Hardware Criptográfico

Processadores modernos incluem instruções dedicadas para operações criptográficas que são ordens de magnitude mais rápidas que implementações em software.

**Intel SHA-NI** (disponível em Ice Lake+ e AMD Zen+) implementa as operações de compressão do SHA-256 em hardware. Uma rodada SHA-256 que requer ~10 instruções genéricas é executada em uma única instrução `SHA256RNDS2`. O throughput é de ~4 ciclos por rodada vs ~20 ciclos em software.

**AES-NI** (disponível em praticamente todos os processadores x86 modernos) acelera as operações AES usadas em CryptoNight e RandomX. Cada rodada AES é executada em uma instrução `AESENC` com latência de 4 ciclos e throughput de 1 ciclo.

### 1.3 Branch Prediction e Branchless Code

Branches mal-preditos custam 15-20 ciclos em processadores modernos (pipeline flush). Para funções hash onde o fluxo de controle é determinístico, todas as branches condicionais são eliminadas usando operações bitwise.

```cpp
// ❌ Com branch (pode causar misprediction)
if (x > y) result = a; else result = b;

// ✅ Branchless (sempre executa em tempo constante)
result = b ^ ((a ^ b) & -(x > y));
```

### 1.4 Instruction Scheduling e Software Pipelining

O compilador nem sempre gera o scheduling ótimo de instruções. Em rotinas críticas (inner loop do SHA-256), o scheduling manual em Assembly garante que instruções independentes sejam intercaladas para manter todas as unidades de execução ocupadas.

Em processadores Intel modernos, o SHA-256 inner loop pode ser organizado para utilizar simultaneamente: a porta 0 (ALU + shift), a porta 1 (ALU + LEA), a porta 5 (ALU + shuffle) e a porta 6 (branch + ALU), mantendo 4 operações em voo por ciclo.

## 2. Otimizações de Nível de Memória

### 2.1 Huge Pages

O sistema de memória virtual traduz endereços virtuais para físicos usando a TLB (Translation Lookaside Buffer). Com páginas de 4KB, um dataset de 2GB (RandomX) requer 524.288 entradas na TLB. Como a TLB tipicamente possui 1.024-4.096 entradas, a taxa de miss é alta.

Com Huge Pages de 2MB, o mesmo dataset requer apenas 1.024 entradas, e com páginas de 1GB, apenas 2 entradas. A redução de TLB misses traduz-se diretamente em ganho de hashrate.

| Configuração | Entradas TLB Necessárias | TLB Miss Rate | Impacto no Hashrate |
|-------------|-------------------------|---------------|---------------------|
| 4KB pages | 524.288 | ~15% | Baseline |
| 2MB pages | 1.024 | ~0.1% | +5-15% |
| 1GB pages | 2 | ~0% | +7-18% |

A configuração de Huge Pages no Linux requer:

```bash
# Alocar 1280 Huge Pages de 2MB (2.5GB total)
echo 1280 | sudo tee /proc/sys/vm/nr_hugepages

# Ou para páginas de 1GB (requer boot parameter)
# Adicionar ao GRUB: hugepagesz=1G hugepages=3
```

### 2.2 NUMA-Aware Allocation

Em servidores multi-socket, cada socket possui seu próprio controlador de memória. Acessar memória "local" (mesmo socket) tem latência de ~80ns, enquanto memória "remota" (outro socket) tem latência de ~150ns — quase o dobro.

O minerador detecta a topologia NUMA via `libnuma` e garante que cada thread aloque memória no nó NUMA mais próximo ao core onde está executando. Para o RandomX, isso significa alocar o dataset de 2GB no nó NUMA do core que o acessará.

### 2.3 Cache Optimization

A hierarquia de cache moderna tem 3 níveis com características distintas:

| Nível | Tamanho Típico | Latência | Bandwidth |
|-------|---------------|----------|-----------|
| L1 Data | 32-48 KB/core | ~4 ciclos | ~1 TB/s |
| L2 | 256KB-2MB/core | ~12 ciclos | ~500 GB/s |
| L3 | 16-96 MB (compartilhado) | ~40 ciclos | ~200 GB/s |
| RAM | 16-512 GB | ~80-150 ciclos | ~50 GB/s |

Para algoritmos memory-hard, a otimização consiste em maximizar a taxa de acertos em L3 e minimizar acessos à RAM. Técnicas incluem: alinhamento de estruturas em cache lines de 64 bytes, prefetching de dados futuros via `__builtin_prefetch`, e organização de dados para maximizar localidade espacial e temporal.

### 2.4 Memory Pool (Arena Allocator)

Alocações dinâmicas (`malloc`/`free`) são caras: cada chamada requer interação com o alocador do sistema, que pode envolver locks e system calls. O minerador pré-aloca blocos grandes de memória na inicialização e distribui sub-blocos via arena allocator, eliminando o overhead de alocação no caminho crítico.

## 3. Otimizações de GPU

### 3.1 Ocupância e Dimensionamento de Grid

A ocupância mede a fração de warps (NVIDIA) ou wavefronts (AMD) ativos em relação ao máximo suportado pelo SM/CU. Ocupância baixa significa que o hardware está subutilizado; ocupância muito alta pode causar contenção de recursos.

O minerador calcula automaticamente o número ideal de threads por bloco usando a API `cudaOccupancyMaxPotentialBlockSize` (CUDA) ou heurísticas baseadas no uso de registradores e shared memory do kernel.

### 3.2 Memory Coalescing

Quando threads adjacentes em um warp acessam endereços de memória adjacentes, o hardware combina os acessos em uma única transação. Para 32 threads acessando 4 bytes cada, um acesso coalescido requer 1 transação de 128 bytes; acessos não-coalescidos podem requerer até 32 transações separadas.

Para o Ethash, onde os lookups no DAG são pseudo-aleatórios, a coalescência é difícil. A otimização consiste em reorganizar os dados do DAG para que elementos acessados por threads adjacentes estejam em endereços adjacentes, quando possível.

### 3.3 Shared Memory e Bank Conflicts

A shared memory é dividida em 32 banks (NVIDIA) ou 32/64 banks (AMD). Quando duas threads acessam o mesmo bank simultaneamente, ocorre um bank conflict que serializa os acessos. O minerador organiza os dados na shared memory com padding para evitar conflicts.

### 3.4 Persistent Kernels

Em vez de lançar um novo kernel para cada batch de nonces, o minerador utiliza persistent kernels que rodam continuamente, recebendo novos jobs via memória compartilhada. Isso elimina o overhead de launch do kernel (~5-10μs por launch) e permite resposta mais rápida a novos jobs.

### 3.5 Streams e Async Operations

O minerador utiliza múltiplos CUDA streams (ou OpenCL command queues) para sobrepor computação e transferência de dados. Enquanto um stream computa hashes, outro transfere resultados para a CPU e recebe novos jobs.

## 4. Otimizações de Rede

### 4.1 TCP Tuning

A comunicação com pools de mineração é otimizada com configurações TCP agressivas. O `TCP_NODELAY` desabilita o algoritmo de Nagle, que normalmente agrupa pequenos pacotes para eficiência, mas adiciona latência inaceitável para submissão de shares. O `SO_KEEPALIVE` com intervalos curtos (10-30s) detecta desconexões rapidamente.

### 4.2 Stratum V2 Binary Framing

O Stratum V2 substitui JSON-RPC por frames binários, reduzindo o overhead de parsing e o tamanho das mensagens. Um `mining.notify` que ocupa ~500 bytes em JSON ocupa ~120 bytes em formato binário. A redução de tamanho diminui a latência de rede e o uso de CPU para parsing.

### 4.3 Submissão Especulativa

Quando o minerador encontra uma share válida, ele a submete imediatamente sem esperar confirmação de shares anteriores. Isso utiliza pipelining de rede para manter a conexão sempre ocupada e reduz a latência efetiva de submissão.

## 5. Otimizações de Compilação

### 5.1 Profile-Guided Optimization (PGO)

O PGO é um processo de compilação em duas fases. Na primeira fase, o código é compilado com instrumentação que registra quais branches são tomadas, quais funções são chamadas com mais frequência, e quais loops executam mais iterações. Na segunda fase, o compilador usa esses dados para otimizar o código real.

O impacto do PGO no hashrate é tipicamente de 5-15%, pois o compilador pode: inlinar funções quentes, otimizar o layout de branches para o caso mais comum, e alocar registradores com base no uso real.

### 5.2 Link-Time Optimization (LTO)

O LTO permite ao compilador otimizar através de fronteiras de módulos (arquivos .o). Sem LTO, o compilador não pode inlinar uma função definida em outro arquivo. Com LTO, o compilador vê todo o programa como uma unidade e pode aplicar otimizações globais.

### 5.3 Flags de Compilação Recomendadas

```bash
# GCC/Clang - Build otimizado para a CPU local
CXXFLAGS="-O3 -march=native -mtune=native -flto -funroll-loops -fomit-frame-pointer"

# Rust - Build otimizado para a CPU local
RUSTFLAGS="-C target-cpu=native -C opt-level=3 -C lto=fat -C codegen-units=1"

# CUDA - Build otimizado
NVCCFLAGS="-O3 --use_fast_math -arch=sm_86 --ptxas-options=-v"

# OpenCL - Flags de compilação de kernel
"-cl-fast-relaxed-math -cl-mad-enable -cl-no-signed-zeros"
```

## 6. Otimizações de Sistema Operacional

### 6.1 CPU Governor e Frequency Scaling

O governor `performance` fixa a frequência da CPU no máximo, eliminando a latência de transição de frequência que ocorre com governors dinâmicos como `ondemand` ou `schedutil`.

```bash
# Fixar governor em performance
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance | sudo tee $cpu
done
```

### 6.2 IRQ Affinity

Interrupções de hardware (IRQs) podem interromper threads de mineração, causando quedas momentâneas de hashrate. O minerador configura a afinidade de IRQs para direcionar interrupções de rede e disco para cores que não estão minerando.

### 6.3 Kernel Parameters

Parâmetros do kernel Linux que impactam a performance de mineração:

```bash
# Desabilitar mitigações de CPU (Spectre/Meltdown) - RISCO DE SEGURANÇA
# mitigations=off

# Aumentar limite de memória locked (para Huge Pages)
echo "* soft memlock unlimited" >> /etc/security/limits.conf
echo "* hard memlock unlimited" >> /etc/security/limits.conf

# Desabilitar transparent huge pages (conflita com explicit huge pages)
echo never > /sys/kernel/mm/transparent_hugepage/enabled

# Aumentar limite de file descriptors
echo "fs.file-max = 1000000" >> /etc/sysctl.conf
```
