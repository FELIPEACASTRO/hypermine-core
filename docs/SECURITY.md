# HyperMine Core — Guia de Segurança Enterprise-Grade

**Versão:** 2.0 (Validado pelo Engenheiro de Segurança e Protocolos — Fevereiro 2026)

---

## Modelo de Ameaças

O HyperMine Core opera em um ambiente adversarial onde atacantes podem tentar roubar hashrate, interceptar recompensas, comprometer a integridade do minerador ou realizar ataques de negação de serviço. O modelo de ameaças considera os seguintes vetores de ataque:

| Vetor de Ataque | Descrição | Severidade |
|---|---|---|
| **Hashrate Hijacking** | Atacante redireciona hashrate para sua própria carteira | Crítica |
| **Man-in-the-Middle** | Interceptação e modificação de comunicação com pool | Crítica |
| **Wallet Address Tampering** | Modificação do endereço de carteira no config | Crítica |
| **Binary Tampering** | Modificação do binário do minerador | Alta |
| **Supply Chain Attack** | Dependência maliciosa inserida no build | Alta |
| **API Exploitation** | Acesso não autorizado à API de monitoramento | Média |
| **DoS no Pool** | Atacante derruba conexão com pool | Média |
| **Information Disclosure** | Vazamento de métricas ou configuração | Baixa |

---

## Camadas de Proteção

### 1. Protocolo — Stratum V2 + NOISE Framework

O Stratum V2 utiliza o NOISE Protocol Framework para autenticação e criptografia de ponta a ponta. O perfil NOISE NNpsk0 é utilizado para autenticação mútua entre minerador e pool, eliminando a possibilidade de ataques MITM.

A implementação utiliza a crate Rust `snow` para o NOISE Framework, com as seguintes configurações:

| Parâmetro | Valor | Justificativa |
|---|---|---|
| Perfil NOISE | NNpsk0 | Autenticação mútua com pre-shared key |
| Cipher | ChaChaPoly | Alta performance em CPUs sem AES-NI |
| Hash | BLAKE2s | Mais rápido que SHA-256 para NOISE |
| DH | Curve25519 | Padrão da indústria |

### 2. Transporte — TLS 1.3 + Certificate Pinning

Para pools que não suportam Stratum V2, a comunicação é protegida com TLS 1.3. O certificate pinning garante que o minerador só se conecte a pools com certificados conhecidos e confiáveis.

A lista de certificados pinados é armazenada em um arquivo separado (`trusted_pools.toml`) com hashes SHA-256 das chaves públicas dos pools confiáveis. O minerador recusa conexão a qualquer pool cujo certificado não corresponda a um hash na lista.

### 3. Anti-Hijacking — Criptografia de Carteiras

Os endereços de carteira no arquivo de configuração são criptografados com AES-256-GCM. A chave de criptografia é derivada de uma senha mestra via Argon2id (resistente a ataques de GPU e ASIC). O minerador solicita a senha mestra apenas na inicialização.

### 4. Integridade do Binário — Code Signing

Os binários oficiais são assinados digitalmente com chave Ed25519. O minerador verifica sua própria integridade em runtime, comparando o hash do binário em execução com o hash esperado. Se a verificação falhar, o minerador encerra imediatamente e alerta o operador.

### 5. API — JWT + Rate Limiting

A API REST de monitoramento é protegida com autenticação JWT (JSON Web Tokens) e rate limiting para prevenir ataques de força bruta. Por padrão, a API aceita conexões apenas de localhost (127.0.0.1).

### 6. Supply Chain — Verificação de Dependências

O pipeline de CI/CD inclui verificação automática de dependências com `cargo-audit` (Rust) e Dependabot (GitHub). Um SBOM (Software Bill of Materials) é gerado em cada release para rastreabilidade completa.

### 7. Configuração — Permissões de Arquivo

Os arquivos de configuração que contêm informações sensíveis (endereços de carteira, tokens de API) são protegidos com permissões restritas (chmod 600 no Linux). O minerador verifica as permissões na inicialização e alerta o operador se estiverem muito permissivas.

---

## Boas Práticas para Operadores

1. Sempre use Stratum V2 quando disponível no pool.
2. Habilite certificate pinning para todos os pools.
3. Use senha mestra forte para criptografia de carteiras.
4. Mantenha o minerador atualizado para receber patches de segurança.
5. Execute o minerador com usuário não-root dedicado.
6. Configure firewall para bloquear acesso externo à API de monitoramento.
7. Monitore alertas de segurança via Discord/Telegram.
8. Verifique checksums SHA-256 de binários baixados antes de executar.
