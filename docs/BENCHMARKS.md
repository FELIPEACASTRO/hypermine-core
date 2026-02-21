# HyperMine Core — Benchmarks e Comparações

**Versão:** 2.0 (Fevereiro 2026)

---

## Benchmarks Estimados por Hardware

### GPUs — Hashrate por Algoritmo

| Algoritmo | RTX 4090 | RTX 5090 | RTX 3090 | RX 7900 XTX | Arc B580 |
|---|---|---|---|---|---|
| Etchash | ~260 MH/s | ~310 MH/s | ~125 MH/s | ~110 MH/s | ~45 MH/s |
| KAWPOW | ~62 MH/s | ~75 MH/s | ~35 MH/s | ~30 MH/s | ~15 MH/s |
| kHeavyHash | ~1.2 GH/s | ~1.5 GH/s | ~600 MH/s | ~500 MH/s | ~200 MH/s |
| Autolykos2 | ~280 MH/s | ~340 MH/s | ~170 MH/s | ~150 MH/s | ~60 MH/s |
| Equihash | ~1100 Sol/s | ~1400 Sol/s | ~650 Sol/s | ~550 Sol/s | ~250 Sol/s |
| Blake3 | ~4.5 GH/s | ~5.5 GH/s | ~2.5 GH/s | ~2.0 GH/s | ~800 MH/s |
| FiroPoW | ~35 MH/s | ~42 MH/s | ~20 MH/s | ~17 MH/s | ~8 MH/s |

### CPUs — Hashrate por Algoritmo

| Algoritmo | Ryzen 9 9950X | Ryzen 9 7950X3D | Ryzen 7 7800X3D | i9-14900K |
|---|---|---|---|---|
| RandomX | ~22 KH/s | ~20 KH/s | ~14 KH/s | ~12 KH/s |
| VerusHash 2.2 | ~45 MH/s | ~42 MH/s | ~30 MH/s | ~28 MH/s |
| GhostRider | ~4.5 KH/s | ~4.2 KH/s | ~3.0 KH/s | ~3.0 KH/s |

### Lucratividade Estimada por GPU (Fevereiro 2026)

| GPU | Lucro/dia (USD) | Custo Energia/dia | Lucro Líquido/dia | ROI (meses) |
|---|---|---|---|---|
| RTX 4090 | ~$2.73 | ~$0.72 | ~$2.01 | ~25 |
| RTX 5090 | ~$1.63 | ~$0.96 | ~$0.67 | ~70 |
| RTX 3090 | ~$1.22 | ~$0.72 | ~$0.50 | ~30 |
| RX 7900 XTX | ~$0.95 | ~$0.60 | ~$0.35 | ~45 |
| Arc B580 | ~$0.35 | ~$0.36 | ~-$0.01 | N/A |

*Nota: Baseado em custo de energia de $0.10/kWh. Valores variam conforme moeda minerada, dificuldade e preço.*

---

## Comparação com Mineradores Existentes

| Característica | HyperMine Core | XMRig | T-Rex | lolMiner | TeamRedMiner |
|---|---|---|---|---|---|
| Algoritmos | 42+ | ~10 | ~30 | ~25 | ~20 |
| Moedas | 23+ | ~8 | ~15 | ~12 | ~10 |
| GPU NVIDIA | CUDA 12 | CUDA | CUDA | CUDA/OCL | OpenCL |
| GPU AMD | HIP/ROCm | OpenCL | Não | OpenCL | OpenCL |
| GPU Intel | OpenCL 3.0 | Não | Não | OpenCL | Não |
| Stratum V2 | Sim | Não | Não | Não | Não |
| NOISE Protocol | Sim | Não | Não | Não | Não |
| Merge Mining | Sim | Não | Não | Parcial | Não |
| PoUW | Sim | Não | Não | Não | Não |
| CUDA Graphs | Sim | Não | Parcial | Não | Não |
| BOLT + PGO | Sim | PGO | Não | Não | Não |
| Prometheus | Nativo | Não | API | Não | Não |
| Plugins | DSO/DLL | Não | Não | Não | Não |
| Dev Fee | 0% (MIT) | 0-1% | 1-2% | 0.7-1% | 0.75-3% |

*Nota: Benchmarks são estimativas baseadas em dados públicos (minerstat.com) e análises dos especialistas. Valores reais serão publicados após o release v1.0.0.*
