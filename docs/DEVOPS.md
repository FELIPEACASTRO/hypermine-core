# HyperMine Core — Guia de DevOps para Farms (1000+ GPUs)

**Versão:** 2.0 (Validado pelo Especialista em DevOps e Infraestrutura — Fevereiro 2026)

---

## Arquitetura de Deploy para Farms

A arquitetura de deploy recomendada para farms de grande escala utiliza Ansible para gerenciamento de configuração, Docker para containerização do minerador, e Nomad como orquestrador leve para bare metal. Kubernetes é utilizado apenas para serviços de suporte (Prometheus, Grafana, APIs de gestão).

```
┌─────────────────────────────────────────────────────────────────┐
│                    PLANO DE CONTROLE                             │
│  Ansible Control Node · Nomad Server · Consul · Vault           │
├─────────────────────────────────────────────────────────────────┤
│                  SERVIÇOS DE SUPORTE (K8s)                      │
│  Prometheus (Federação) · Grafana · AlertManager · API Gateway  │
├─────────────────────────────────────────────────────────────────┤
│              NÓS DE MINERAÇÃO (Bare Metal + Docker)             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐              │
│  │ Node 01 │ │ Node 02 │ │ Node 03 │ │ Node N  │              │
│  │ 8x GPU  │ │ 8x GPU  │ │ 8x GPU  │ │ 8x GPU  │              │
│  │ Docker  │ │ Docker  │ │ Docker  │ │ Docker  │              │
│  │ Nomad   │ │ Nomad   │ │ Nomad   │ │ Nomad   │              │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Stack de Ferramentas

| Ferramenta | Uso | Justificativa |
|---|---|---|
| **Docker** | Containerização do minerador | Consistência, portabilidade, isolamento de GPU |
| **Ansible** | Gerenciamento de configuração | Templates TOML, distribuição de config, updates |
| **Nomad** | Orquestração de containers | Leve, suporte nativo a GPU, ideal para bare metal |
| **Consul** | Service discovery e health checks | Integração nativa com Nomad |
| **Vault** | Gerenciamento de secrets | Endereços de carteira, tokens de API |
| **Prometheus** | Coleta de métricas | Federação para 1000+ GPUs |
| **Grafana** | Dashboards | Visualização de métricas em tempo real |
| **AlertManager** | Alertas | Discord, Telegram, Email, PagerDuty |
| **Terraform** | Infrastructure as Code | Provisionamento de cloud/bare metal |
| **GitHub Actions** | CI/CD | Build, test, deploy automatizado |

---

## Ansible Playbooks

### Playbook: Deploy do Minerador

```yaml
# deploy_miner.yml
- hosts: mining_nodes
  become: yes
  vars:
    hypermine_version: "1.0.0"
    config_template: "templates/config.toml.j2"
  tasks:
    - name: Pull Docker image
      docker_image:
        name: "hypermine/core:{{ hypermine_version }}"
        source: pull

    - name: Deploy configuration
      template:
        src: "{{ config_template }}"
        dest: "/opt/hypermine/config.toml"
        mode: "0600"
      notify: restart_miner

    - name: Deploy coin configs
      copy:
        src: "coins/"
        dest: "/opt/hypermine/coins/"
        mode: "0600"
      notify: restart_miner

    - name: Start miner container
      docker_container:
        name: hypermine
        image: "hypermine/core:{{ hypermine_version }}"
        runtime: nvidia
        devices:
          - "/dev/nvidia0:/dev/nvidia0"
          - "/dev/nvidiactl:/dev/nvidiactl"
          - "/dev/nvidia-uvm:/dev/nvidia-uvm"
        volumes:
          - "/opt/hypermine/config.toml:/app/config.toml:ro"
          - "/opt/hypermine/coins:/app/coins:ro"
        restart_policy: always
        state: started
```

### Playbook: Setup de Huge Pages

```yaml
# setup_hugepages.yml
- hosts: mining_nodes
  become: yes
  tasks:
    - name: Configure Huge Pages (2MB)
      sysctl:
        name: vm.nr_hugepages
        value: "1280"
        state: present
        reload: yes

    - name: Configure Transparent Huge Pages
      shell: echo madvise > /sys/kernel/mm/transparent_hugepage/enabled
```

---

## Docker

### Dockerfile Multi-stage

```dockerfile
# Stage 1: Build
FROM nvidia/cuda:12.0-devel-ubuntu22.04 AS builder
RUN apt-get update && apt-get install -y cmake build-essential libssl-dev
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
COPY . /src
WORKDIR /src/build
RUN cmake .. -DCMAKE_BUILD_TYPE=Release -DENABLE_CUDA=ON -DENABLE_LTO=ON
RUN make -j$(nproc)

# Stage 2: Runtime
FROM nvidia/cuda:12.0-runtime-ubuntu22.04
COPY --from=builder /src/build/hypermine-core /usr/local/bin/
ENTRYPOINT ["hypermine-core", "--config", "/app/config.toml"]
```

### Docker Compose para Nó de Mineração

```yaml
version: "3.8"
services:
  hypermine:
    image: hypermine/core:latest
    runtime: nvidia
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    volumes:
      - ./config.toml:/app/config.toml:ro
      - ./coins:/app/coins:ro
    restart: always
    ports:
      - "9090:9090"  # Prometheus metrics
      - "8080:8080"  # REST API (bind localhost only)
```

---

## Monitoramento em Escala

### Prometheus Federation

Para farms com 1000+ GPUs, a federação do Prometheus é essencial. Cada nó de mineração expõe métricas localmente, e um Prometheus central faz scraping federado.

```yaml
# prometheus.yml (central)
scrape_configs:
  - job_name: 'hypermine-federation'
    honor_labels: true
    metrics_path: '/federate'
    params:
      'match[]':
        - '{job="hypermine"}'
    static_configs:
      - targets:
        - 'prometheus-node-01:9090'
        - 'prometheus-node-02:9090'
        # ... até N nós
```

### Métricas Exportadas

| Métrica | Tipo | Descrição |
|---|---|---|
| `hypermine_hashrate_total` | Gauge | Hashrate total do nó |
| `hypermine_hashrate_per_gpu` | Gauge | Hashrate por GPU |
| `hypermine_shares_accepted` | Counter | Shares aceitas |
| `hypermine_shares_rejected` | Counter | Shares rejeitadas |
| `hypermine_gpu_temperature` | Gauge | Temperatura por GPU (°C) |
| `hypermine_gpu_power_draw` | Gauge | Consumo por GPU (W) |
| `hypermine_gpu_fan_speed` | Gauge | Velocidade do fan (%) |
| `hypermine_hash_per_watt` | Gauge | Eficiência energética |
| `hypermine_pool_latency_ms` | Histogram | Latência para pool |
| `hypermine_uptime_seconds` | Counter | Tempo de operação |

---

## Alertas Recomendados

| Alerta | Condição | Severidade |
|---|---|---|
| GPU Offline | `hypermine_hashrate_per_gpu == 0` por 5 min | Crítica |
| Hashrate Baixo | `hypermine_hashrate_total < 80%` do esperado | Alta |
| Temperatura Alta | `hypermine_gpu_temperature > 85` | Alta |
| Shares Rejeitadas | `rate(hypermine_shares_rejected) > 2%` | Média |
| Pool Desconectado | `hypermine_pool_connected == 0` por 1 min | Crítica |
| Fan Parado | `hypermine_gpu_fan_speed == 0` | Crítica |
| Power Draw Alto | `hypermine_gpu_power_draw > power_limit * 1.1` | Média |
