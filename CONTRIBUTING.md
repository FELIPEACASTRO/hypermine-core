# Contribuindo para o HyperMine Core

Obrigado pelo interesse em contribuir para o HyperMine Core! Este documento fornece diretrizes para contribuições.

## Estrutura do Projeto

O projeto utiliza uma arquitetura híbrida C++/Rust:

- **C++20** — Algoritmos de hashing, kernels GPU (CUDA/OpenCL), HAL
- **Rust** — Networking (Stratum), configuração, monitoramento, engine

## Requisitos de Desenvolvimento

- CMake 3.28+
- GCC 13+ ou Clang 17+
- Rust 1.82+ (edition 2024)
- CUDA Toolkit 12.0+ (opcional, para suporte NVIDIA)
- OpenCL SDK (opcional, para suporte AMD)
- NASM (para Assembly x86-64)

## Como Contribuir

1. Faça fork do repositório
2. Crie uma branch para sua feature: `git checkout -b feature/minha-feature`
3. Implemente suas mudanças com testes
4. Execute `cargo test --all` e `ctest` para verificar
5. Abra um Pull Request com descrição detalhada

## Padrões de Código

### C++
- Use `clang-format` com o estilo do projeto
- Nomes de funções e variáveis em `snake_case`
- Nomes de classes e structs em `PascalCase`
- Constantes em `UPPER_SNAKE_CASE`
- Comente funções públicas com Doxygen

### Rust
- Use `cargo fmt` e `cargo clippy`
- Documente módulos e funções públicas com `///`
- Use `thiserror` para tipos de erro
- Use `anyhow` para propagação de erros em binários

## Adicionando um Novo Algoritmo

1. Crie o diretório `src/algorithms/<nome>/`
2. Implemente a versão genérica (C++ puro) como referência
3. Adicione variantes SIMD conforme necessário
4. Adicione kernels CUDA/OpenCL se o algoritmo for GPU-friendly
5. Registre o algoritmo no `Algorithm` enum em `src/network/src/lib.rs`
6. Adicione o mapeamento no dispatcher em `src/core/src/lib.rs`
7. Crie o arquivo de configuração em `coins/<moeda>.toml`
8. Adicione testes de corretude contra vetores de teste oficiais
9. Adicione benchmarks comparativos

## Adicionando Suporte a uma Nova Moeda

1. Identifique o algoritmo de mineração da moeda
2. Se o algoritmo já está implementado, apenas crie `coins/<moeda>.toml`
3. Se o algoritmo é novo, siga o guia "Adicionando um Novo Algoritmo"
4. Adicione pools recomendados no arquivo de configuração
5. Teste contra um pool real (testnet se disponível)
