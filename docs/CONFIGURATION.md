# HyperMine Core — Guia de Configuração

Este documento explica todos os parâmetros de configuração disponíveis no HyperMine Core e como utilizá-los para otimizar a mineração para seu hardware e objetivos específicos.

## Estrutura de Configuração

A configuração do HyperMine Core é hierárquica e utiliza o formato TOML (Tom's Obvious, Minimal Language). A hierarquia de precedência é:

| Nível | Fonte | Precedência |
|-------|-------|-------------|
| 1 (mais alta) | Flags de linha de comando | `--coins bitcoin --threads 8` |
| 2 | Variáveis de ambiente | `HYPERMINE_COINS=bitcoin` |
| 3 | Arquivo principal | `config.toml` |
| 4 | Arquivos por moeda | `coins/bitcoin.toml` |
| 5 (mais baixa) | Defaults internos | Valores padrão do código |

## Parametrização de Moedas

O sistema de parametrização permite ao operador controlar exatamente quais moedas minerar. A configuração é feita no campo `enabled_coins` do `config.toml`.

Para **minerar todas as moedas configuradas**, defina `enabled_coins = ["*"]`. O minerador carregará todos os arquivos `coins/*.toml` e distribuirá o hashrate entre eles conforme a estratégia selecionada.

Para **minerar moedas específicas**, liste-as explicitamente: `enabled_coins = ["bitcoin", "monero", "ravencoin"]`. Apenas as moedas listadas serão mineradas, mesmo que existam outros arquivos de configuração no diretório `coins/`.

Para **excluir moedas específicas**, use o prefixo `!`: `enabled_coins = ["*", "!dogecoin", "!dash"]`. Isso minera todas as moedas exceto Dogecoin e Dash.

## Estratégias de Seleção de Moeda

Quando múltiplas moedas estão habilitadas, o minerador precisa decidir como distribuir o hashrate entre elas. Três estratégias estão disponíveis.

**`most_profitable`** calcula a lucratividade de cada moeda em tempo real, considerando: dificuldade atual da rede, preço da moeda (via API de exchanges), recompensa por bloco, e custo de energia do operador. O minerador alterna automaticamente para a moeda mais lucrativa a cada intervalo configurado (`profitability_interval`).

**`round_robin`** alterna entre moedas em intervalos fixos, minerando cada uma por um período configurável. Essa estratégia é útil quando o operador deseja acumular múltiplas moedas independentemente da lucratividade momentânea.

**`manual`** minera as moedas na ordem listada em `enabled_coins`, dedicando todo o hashrate à primeira moeda da lista. As demais servem como fallover caso os pools da moeda principal fiquem indisponíveis.

## Configuração de Hardware

### CPU

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `max_cpu_threads` | int | 0 (auto) | Número máximo de threads de mineração |
| `enable_huge_pages` | bool | true | Habilitar Huge Pages para RandomX |
| `huge_page_size` | string | "2MB" | Tamanho das Huge Pages ("2MB" ou "1GB") |
| `enable_numa` | bool | true | Habilitar alocação NUMA-aware |
| `priority` | string | "high" | Prioridade do processo ("normal", "high", "realtime") |
| `affinity` | array | [] | Lista de cores para CPU pinning (vazio = auto) |

### GPU NVIDIA (CUDA)

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `cuda_compute_capability` | string | "auto" | Compute capability alvo |
| `enable_tensor_cores` | bool | false | Usar tensor cores (quando aplicável) |
| `persistent_kernel` | bool | true | Usar persistent kernels |
| `streams_per_gpu` | int | 2 | Número de CUDA streams por GPU |
| `max_gpu_temperature` | int | 80 | Temperatura máxima em Celsius |
| `max_gpu_power` | int | 0 | Power limit em Watts (0 = sem limite) |
| `gpu_fan_speed` | int | 0 | Velocidade do fan em % (0 = auto) |

### GPU AMD (OpenCL)

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `opencl_platform` | string | "auto" | Plataforma OpenCL a usar |
| `workgroup_size` | int | 256 | Tamanho do workgroup |
| `enable_lds_optimization` | bool | true | Otimizar uso de LDS |

## Configuração de Rede

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `tcp_nodelay` | bool | true | Desabilitar algoritmo de Nagle |
| `keepalive_interval` | int | 30 | Intervalo de keepalive em segundos |
| `reconnect_delay` | int | 1 | Delay entre tentativas de reconexão |
| `max_reconnect_attempts` | int | 0 | Máximo de tentativas (0 = infinito) |
| `prefer_stratum_v2` | bool | true | Preferir Stratum V2 quando disponível |
| `enable_tls` | bool | true | Habilitar TLS para conexões |

## Configuração de Monitoramento

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `api_enabled` | bool | true | Habilitar API REST local |
| `api_port` | int | 8080 | Porta da API REST |
| `api_bind` | string | "127.0.0.1" | Endereço de bind da API |
| `prometheus_enabled` | bool | true | Habilitar exportador Prometheus |
| `prometheus_port` | int | 9090 | Porta do Prometheus |

## Configuração por Moeda

Cada moeda possui seu próprio arquivo de configuração no diretório `coins/`. O arquivo define o algoritmo, endereço da carteira, pools e parâmetros específicos do algoritmo.

### Parâmetros Comuns

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `coin.name` | string | Nome da moeda |
| `coin.symbol` | string | Símbolo (BTC, XMR, etc.) |
| `coin.algorithm` | string | Algoritmo de mineração |
| `coin.enabled` | bool | Se a moeda está habilitada |
| `wallet.address` | string | Endereço da carteira |
| `pools.list[].url` | string | URL do pool (stratum+tcp://...) |
| `pools.list[].password` | string | Senha do pool |
| `pools.list[].priority` | int | Prioridade (1 = mais alta) |
| `pools.list[].weight` | int | Peso para load balancing (%) |

### Parâmetros Específicos por Algoritmo

**SHA-256:** `intensity` (auto/low/medium/high/extreme), `batch_size` (0 = auto)

**RandomX:** `mode` (fast/light), `jit` (true/false), `huge_pages` (true/false), `numa` (true/false), `threads` (0 = auto)

**Ethash/Etchash:** `dag_cache` (true/false), `dag_generation_device` (cpu/gpu), `epoch_precompute` (true/false)

**KAWPOW:** `intensity` (auto/low/medium/high), `period_seed_cache` (true/false)

**Equihash:** `solver` (default/tromp/silentarmy), `nonce_range` (auto/custom)

## Hot-Reload

O minerador monitora todos os arquivos de configuração e aplica mudanças automaticamente sem reiniciar. Os seguintes parâmetros podem ser alterados em tempo de execução:

- Moedas habilitadas/desabilitadas
- Endereços de carteira
- Pools (adicionar, remover, alterar prioridade)
- Limites de temperatura e power
- Parâmetros de monitoramento e alertas

Os seguintes parâmetros requerem reinício:

- Número de threads de CPU
- Dispositivos de GPU
- Configurações de Huge Pages
- Modo do RandomX (fast/light)

## Exemplos de Configuração

### Mineração Apenas de Bitcoin (Máxima Performance)

```toml
[general]
worker_name = "btc-rig-01"
enabled_coins = ["bitcoin"]
coin_strategy = "manual"

[hardware]
devices = ["cpu"]
max_cpu_threads = 0

[cpu]
enable_huge_pages = false
priority = "high"
```

### Mineração Multi-Moeda (Mais Lucrativa)

```toml
[general]
worker_name = "multi-rig-01"
enabled_coins = ["bitcoin", "monero", "ethereum-classic", "ravencoin", "ergo"]
coin_strategy = "most_profitable"
profitability_interval = 300

[hardware]
devices = "auto"
```

### Farm de GPUs (Apenas GPU)

```toml
[general]
worker_name = "gpu-farm-01"
enabled_coins = ["ethereum-classic", "ravencoin", "ergo"]
coin_strategy = "most_profitable"

[hardware]
devices = ["gpu:0", "gpu:1", "gpu:2", "gpu:3", "gpu:4", "gpu:5"]
max_gpu_temperature = 75
max_gpu_power = 250

[gpu.nvidia]
persistent_kernel = true
streams_per_gpu = 2
```
