# HyperMine Core — Arquitetura do Sistema

## Visão Geral da Arquitetura

O HyperMine Core segue uma arquitetura em camadas com comunicação de baixa latência entre componentes. Cada camada possui responsabilidades bem definidas e interfaces estáveis, permitindo evolução independente.

```
┌─────────────────────────────────────────────────────────┐
│                    Camada de Aplicação                    │
│  Config Manager │ CLI │ API REST │ Monitoring            │
├─────────────────────────────────────────────────────────┤
│                   Camada de Orquestração                  │
│  Engine │ Dispatcher │ Worker Pool │ Job Queue            │
├─────────────────────────────────────────────────────────┤
│                   Camada de Algoritmos                    │
│  SHA-256 │ Ethash │ RandomX │ KAWPOW │ Equihash │ ...    │
├─────────────────────────────────────────────────────────┤
│              Hardware Abstraction Layer (HAL)             │
│  CPU Backend │ CUDA Backend │ OpenCL Backend │ FPGA      │
├─────────────────────────────────────────────────────────┤
│                   Camada de Rede                         │
│  Stratum V1 │ Stratum V2 │ Pool Manager │ Failover      │
└─────────────────────────────────────────────────────────┘
```

## Componentes Principais

### 1. Config Manager

O Config Manager é responsável por carregar, validar e distribuir configurações para todos os componentes. Ele monitora arquivos de configuração para hot-reload e expõe uma interface thread-safe para leitura de parâmetros.

A configuração é hierárquica: `config.toml` define parâmetros globais, `coins/*.toml` define parâmetros por moeda, e flags de linha de comando sobrescrevem ambos. A precedência é: CLI > variáveis de ambiente > `config.toml` > defaults.

### 2. Engine (Motor de Mineração)

O Engine é o componente central que coordena todo o processo de mineração. Ele recebe jobs do Stratum Client, despacha para os Workers apropriados, coleta resultados e submete shares de volta ao pool.

O Engine opera em um loop principal single-threaded (event-driven) que coordena Workers multi-threaded. Essa arquitetura evita locks no caminho crítico e minimiza a latência entre recebimento de job e início da computação.

### 3. Algorithm Dispatcher

O Dispatcher mapeia moedas para algoritmos e algoritmos para backends de hardware. Quando o Engine recebe um job para Bitcoin, o Dispatcher seleciona o algoritmo SHA-256 e o despacha para o backend CPU (com a variante SIMD mais rápida disponível) ou ASIC.

O Dispatcher suporta troca de algoritmo em tempo de execução sem parar os Workers. Quando a configuração muda (via hot-reload ou comando da API), o Dispatcher drena os jobs em andamento e redireciona novos jobs para o novo algoritmo.

### 4. Worker Pool

O Worker Pool gerencia threads de mineração. Cada Worker é fixado a um core específico (CPU pinning) e possui seu próprio contexto de execução (registradores SIMD, estado do JIT compiler, etc.).

Para GPUs, cada Worker gerencia um ou mais streams CUDA / command queues OpenCL, permitindo overlap de computação e transferência de dados.

### 5. Hardware Abstraction Layer (HAL)

A HAL expõe uma interface unificada para todos os backends de hardware:

```cpp
class IHardwareBackend {
public:
    virtual ~IHardwareBackend() = default;
    
    // Inicialização e detecção
    virtual bool initialize() = 0;
    virtual DeviceInfo get_device_info() const = 0;
    virtual std::vector<Feature> get_features() const = 0;
    
    // Alocação de memória
    virtual void* allocate(size_t bytes, AllocFlags flags) = 0;
    virtual void deallocate(void* ptr) = 0;
    
    // Execução
    virtual void submit_work(const WorkItem& work) = 0;
    virtual void synchronize() = 0;
    
    // Métricas
    virtual Metrics get_metrics() const = 0;
    virtual float get_temperature() const = 0;
    virtual float get_power_draw() const = 0;
};
```

### 6. Stratum Client

O Stratum Client é implementado em Rust com `tokio` para I/O assíncrono. Ele suporta tanto Stratum V1 (JSON-RPC) quanto Stratum V2 (binário), selecionando automaticamente a versão suportada pelo pool.

A comunicação com o Engine é feita via channels lock-free (`crossbeam-channel`), eliminando contenção no caminho crítico.

## Fluxo de Dados

O fluxo de dados durante a mineração segue este caminho:

1. O **Stratum Client** recebe um `mining.notify` do pool com o header do bloco e o target de dificuldade.
2. O **Job Queue** armazena o job e notifica o **Engine**.
3. O **Engine** consulta o **Dispatcher** para determinar o algoritmo e backend.
4. O **Dispatcher** seleciona a implementação mais rápida disponível.
5. Os **Workers** recebem o job e iniciam a computação de hashes.
6. Quando um Worker encontra um nonce que satisfaz o target, ele notifica o **Engine**.
7. O **Engine** submete a share via **Stratum Client**.
8. O **Monitoring** registra métricas de cada etapa.

## Decisões de Design

### Por que C++ e Rust juntos?

A combinação de C++ e Rust não é acidental. C++ é utilizado nos componentes que exigem controle absoluto sobre o hardware: algoritmos de hashing, kernels GPU e interação com drivers. Rust é utilizado nos componentes que se beneficiam de segurança de memória: networking, parsing de configuração e gerenciamento de estado.

A interface entre C++ e Rust utiliza FFI (Foreign Function Interface) com `extern "C"`, que tem overhead zero (é uma chamada de função normal no nível de assembly). Não há serialização, cópia de dados ou indireção.

### Por que não Go, Java ou Python?

Go possui garbage collector que causa pausas imprevisíveis — inaceitável quando cada milissegundo conta. Java tem o mesmo problema, agravado pelo JIT warmup. Python é ~100x mais lento que C++ para computação numérica. Essas linguagens são adequadas para ferramentas auxiliares (dashboards, scripts de automação), mas não para o caminho crítico de mineração.

### Por que lock-free data structures?

Locks (mutexes, semáforos) causam contenção quando múltiplas threads competem pelo mesmo recurso. Em um minerador com 16+ threads de CPU e 8+ streams de GPU, a contenção pode reduzir o hashrate em 5-10%. Estruturas lock-free (ring buffers, MPSC channels) eliminam esse problema ao custo de maior complexidade de implementação.
