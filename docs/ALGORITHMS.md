# HyperMine Core — Algoritmos de Mineração

Este documento detalha todos os algoritmos de mineração suportados pelo HyperMine Core, suas características técnicas, moedas associadas e estratégias de otimização.

## Classificação por Tipo de Computação

Os algoritmos de mineração podem ser classificados em quatro categorias fundamentais, cada uma exigindo estratégias de otimização distintas.

**Algoritmos CPU-Bound** são dominados por operações aritméticas e lógicas puras, com pouca dependência de memória. O SHA-256 é o exemplo clássico: cada hash requer 64 rodadas de operações de 32-bit (rotações, shifts, adições, XOR) sobre um estado de 256 bits. A otimização principal é o paralelismo via SIMD, processando múltiplos hashes independentes simultaneamente.

**Algoritmos Memory-Hard** são projetados para exigir grandes quantidades de memória rápida, tornando ASICs menos eficientes. O Ethash requer um DAG de ~5GB, o RandomX utiliza um dataset de 2GB, e o Scrypt usa um scratchpad de 128KB por instância. A otimização principal é a hierarquia de cache: manter os dados mais acessados em L1/L2 e minimizar acessos à memória principal.

**Algoritmos GPU-Optimized** são projetados para explorar o paralelismo massivo das GPUs. O KAWPOW utiliza o cache L1 do GPU de forma intensiva, o Autolykos2 combina Blake2b com acesso memory-hard, e o Equihash resolve um problema de busca em grafo que se beneficia de sorting paralelo.

**Algoritmos Multi-Hash** encadeiam múltiplas funções hash em sequência. O X11 utiliza 11 funções diferentes, o X13 utiliza 13, e o GhostRider rotaciona entre 15 algoritmos. A otimização principal é manter os dados intermediários em registradores SIMD entre funções, evitando flush para memória.

## Tabela Completa de Algoritmos

| # | Algoritmo | Tipo | Moedas | Hardware | Complexidade |
|---|-----------|------|--------|----------|-------------|
| 1 | SHA-256 | CPU-Bound | 26 | ASIC/CPU | Baixa |
| 2 | Scrypt | Memory-Hard | 18 | ASIC | Média |
| 3 | KAWPOW | GPU-Optimized | 18 | GPU | Alta |
| 4 | Equihash (todas variantes) | Memory-Hard | 16+ | GPU/ASIC | Alta |
| 5 | X11 | Multi-Hash | 13 | ASIC | Média |
| 6 | Ethash | Memory-Hard | 11 | GPU/ASIC | Alta |
| 7 | Etchash | Memory-Hard | 10 | GPU | Alta |
| 8 | RandomX | CPU-Optimized | 8 | CPU | Muito Alta |
| 9 | Eaglesong | CPU-Bound | 8 | GPU/ASIC | Baixa |
| 10 | NeoScrypt | Memory-Hard | 8 | GPU/CPU | Média |
| 11 | Lyra2REv2 | Multi-Hash | 7 | GPU/ASIC/CPU | Média |
| 12 | Qubit | Multi-Hash | 6 | ASIC | Baixa |
| 13 | Skein | CPU-Bound | 6 | GPU/ASIC | Baixa |
| 14 | Zhash | Memory-Hard | 6 | GPU | Alta |
| 15 | GhostRider | Multi-Hash | 5 | CPU/GPU | Muito Alta |
| 16 | Groestl | CPU-Bound | 5 | ASIC/CPU | Baixa |
| 17 | BeamHashIII | Memory-Hard | 4 | GPU | Alta |
| 18 | Autolykos2 | Memory-Hard | 4 | GPU | Média |
| 19 | Yescrypt | Memory-Hard | 4 | CPU | Média |
| 20 | YescryptR16 | Memory-Hard | 4 | CPU | Média |
| 21 | Blake (2b) | CPU-Bound | 3 | GPU/ASIC | Baixa |
| 22 | Handshake | CPU-Bound | 3 | ASIC | Baixa |
| 23 | Octopus | GPU-Optimized | 3 | GPU | Média |
| 24 | ProgPowZ | GPU-Optimized | 3 | GPU | Alta |
| 25 | X16RT | Multi-Hash | 3 | GPU | Alta |
| 26 | Blake (2b-Sia) | CPU-Bound | 1 | ASIC | Baixa |
| 27 | Blake3 | CPU-Bound | 1 | GPU | Baixa |
| 28 | CuckooCycle | Graph-Based | 2 | GPU | Muito Alta |
| 29 | FiroPoW | GPU-Optimized | 2 | GPU | Alta |
| 30 | DynexSolve | GPU-Optimized | 1 | GPU | Alta |

## Detalhes dos Algoritmos Principais

### SHA-256 (Bitcoin e 25+ moedas)

O SHA-256 processa blocos de 512 bits e produz um digest de 256 bits. Cada bloco passa por 64 rodadas de compressão, onde cada rodada executa: escolha condicional (Ch), maioria (Maj), duas funções sigma (Σ0, Σ1), e adição modular de 32 bits.

A mineração de Bitcoin requer **double SHA-256**: o header do bloco (80 bytes) é hashado duas vezes. O minerador itera sobre o campo nonce (4 bytes) e, quando esgotado, modifica o campo extraNonce no coinbase transaction.

A implementação AVX-512 processa **8 hashes SHA-256 simultaneamente** em um único core, utilizando 16 registradores ZMM de 512 bits. Cada registrador contém 8 valores de 32 bits (um de cada hash), e as operações SIMD processam todos os 8 hashes em paralelo.

### RandomX (Monero e 7+ moedas)

O RandomX é o algoritmo mais sofisticado em termos de implementação. Ele gera programas aleatórios que são compilados e executados em uma máquina virtual customizada. Cada programa contém ~256 instruções que incluem operações de inteiro, ponto flutuante e acesso a memória.

O **modo fast** pré-computa um dataset de 2GB a partir de uma key de 32 bytes. Esse dataset é acessado de forma pseudo-aleatória durante a execução do programa, exigindo que toda a estrutura esteja em memória RAM. O uso de Huge Pages (2MB) reduz TLB misses de ~15% para ~0.1%, resultando em ganho significativo de hashrate.

O **compilador JIT** traduz os programas RandomX diretamente para instruções nativas x86-64 ou ARM64, eliminando o overhead de interpretação. O JIT compiler otimiza: alocação de registradores (mantendo variáveis quentes em registradores físicos), scheduling de instruções (reordenando para evitar stalls de pipeline), e eliminação de código morto.

### Ethash/Etchash (Ethereum Classic e 20+ moedas)

O Ethash é um algoritmo memory-hard que requer um DAG (Directed Acyclic Graph) de ~5GB. O processo de mineração consiste em: gerar um seed a partir do número do bloco, computar um cache de 64MB a partir do seed, gerar o DAG de ~5GB a partir do cache, e realizar 64 lookups pseudo-aleatórios de 128 bytes no DAG para cada tentativa de nonce.

A otimização em GPU foca em minimizar a latência dos lookups no DAG. Como o DAG não cabe na shared memory (tipicamente 48-96KB), ele reside na memória global do GPU. O kernel utiliza **prefetching** para iniciar o próximo lookup enquanto o atual ainda está sendo processado, e **memory coalescing** para garantir que threads adjacentes acessem endereços adjacentes quando possível.

### KAWPOW (Ravencoin e 17+ moedas)

O KAWPOW é uma variante do ProgPoW (Programmatic Proof of Work) que gera programas pseudo-aleatórios a cada período. Cada programa utiliza intensivamente o cache L1 do GPU, tornando FPGAs e ASICs menos eficientes.

A implementação CUDA utiliza **registers** e **shared memory** de forma intensiva, com o programa gerado acessando todos os componentes do SM (Streaming Multiprocessor) de forma balanceada.

### Equihash (Zcash e 15+ moedas)

O Equihash é baseado no **Generalized Birthday Problem**: encontrar k valores de n bits cuja soma XOR é zero. A variante mais comum é Equihash(200,9), que requer encontrar 512 valores de 200 bits.

A implementação utiliza o **algoritmo de Wagner** otimizado com sorting paralelo em GPU. Cada rodada do algoritmo reduz o número de candidatos pela metade, e o sorting é implementado com **radix sort** paralelo que explora a localidade de memória.

### GhostRider (Raptoreum e 4+ moedas)

O GhostRider é um algoritmo multi-hash que rotaciona entre **15 algoritmos diferentes** em uma sequência determinada pelo hash do bloco anterior. Os 15 algoritmos são: Blake, BMW, Groestl, JH, Keccak, Skein, Luffa, CubeHash, SHAvite, SIMD, ECHO, Hamsi, Fugue, Shabal e Whirlpool.

A otimização principal é manter todas as 15 implementações carregadas em memória e prontas para execução, com transição zero-overhead entre algoritmos. Os dados intermediários são mantidos em registradores SIMD entre funções quando possível.
