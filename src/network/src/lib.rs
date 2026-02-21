//! HyperMine Network — Stratum V1/V2 Client
//!
//! Este módulo implementa os clientes Stratum para comunicação com pools de mineração.
//! Suporta tanto Stratum V1 (JSON-RPC sobre TCP) quanto Stratum V2 (binário com TLS).

pub mod stratum_v1;
pub mod stratum_v2;
pub mod pool_manager;
pub mod job_queue;
pub mod failover;

use serde::{Deserialize, Serialize};
use thiserror::Error;

// ============================================================================
// Tipos Fundamentais
// ============================================================================

/// Representa um job de mineração recebido do pool
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MiningJob {
    /// ID único do job
    pub job_id: String,
    /// Header do bloco (dados para hash)
    pub block_header: Vec<u8>,
    /// Target de dificuldade (hash deve ser menor que este valor)
    pub target: [u8; 32],
    /// Nonce inicial sugerido
    pub nonce_start: u64,
    /// Range de nonces a testar
    pub nonce_range: u64,
    /// Timestamp de recebimento (para detecção de stale)
    pub received_at: std::time::Instant,
    /// Algoritmo de mineração
    pub algorithm: Algorithm,
    /// Dados extras específicos do algoritmo
    pub extra_data: Vec<u8>,
}

/// Representa uma share encontrada pelo minerador
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Share {
    /// ID do job que gerou esta share
    pub job_id: String,
    /// Nonce que satisfaz o target
    pub nonce: u64,
    /// Hash resultante
    pub hash: [u8; 32],
    /// Timestamp de descoberta
    pub found_at: std::time::Instant,
    /// ID do dispositivo que encontrou
    pub device_id: String,
}

/// Algoritmos de mineração suportados
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Algorithm {
    Sha256,
    Scrypt,
    Ethash,
    Etchash,
    RandomX,
    KawPow,
    Equihash200_9,
    Equihash144_5,
    Equihash192_7,
    X11,
    X13,
    X16R,
    X16Rv2,
    Blake2b,
    Blake2s,
    Blake3,
    Autolykos2,
    CuckooCycle,
    FiroPoW,
    GhostRider,
    Yescrypt,
    YesPoWer,
    Eaglesong,
    BeamHashIII,
    Octopus,
    ProgPowZ,
    CryptoNightConceal,
    CryptoNightGPU,
    DynexSolve,
    NeoScrypt,
    Lyra2REv2,
    Lyra2z,
    Groestl,
    Skein,
    Qubit,
    Zhash,
    Verthash,
    VerusHash,
    Radiant,
    KHeavyHash,
    Allium,
    CPUPower,
}

/// Erros do módulo de rede
#[derive(Error, Debug)]
pub enum NetworkError {
    #[error("Falha na conexão com o pool: {0}")]
    ConnectionFailed(String),
    
    #[error("Autenticação rejeitada pelo pool: {0}")]
    AuthenticationFailed(String),
    
    #[error("Timeout na comunicação: {0}")]
    Timeout(String),
    
    #[error("Share rejeitada: {0}")]
    ShareRejected(String),
    
    #[error("Job stale: {0}")]
    StaleJob(String),
    
    #[error("Erro de protocolo: {0}")]
    ProtocolError(String),
    
    #[error("Erro de TLS: {0}")]
    TlsError(String),
    
    #[error("Pool indisponível: {0}")]
    PoolUnavailable(String),
}

/// Resultado de submissão de share
#[derive(Debug, Clone)]
pub enum ShareResult {
    Accepted,
    Rejected(String),
    Stale,
}

/// Configuração de um pool
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PoolConfig {
    pub url: String,
    pub worker_name: String,
    pub password: String,
    pub priority: u32,
    pub weight: u32,
    pub stratum_version: StratumVersion,
    pub tls_enabled: bool,
}

/// Versão do protocolo Stratum
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub enum StratumVersion {
    V1,
    V2,
    Auto,
}

/// Estatísticas de rede
#[derive(Debug, Clone, Default)]
pub struct NetworkStats {
    pub shares_accepted: u64,
    pub shares_rejected: u64,
    pub shares_stale: u64,
    pub latency_ms: f64,
    pub bytes_sent: u64,
    pub bytes_received: u64,
    pub reconnections: u64,
    pub uptime_seconds: u64,
}

// ============================================================================
// Trait para Cliente Stratum
// ============================================================================

/// Interface unificada para clientes Stratum V1 e V2
#[allow(async_fn_in_trait)]
pub trait StratumClient: Send + Sync {
    /// Conecta ao pool
    async fn connect(&mut self, config: &PoolConfig) -> Result<(), NetworkError>;
    
    /// Desconecta do pool
    async fn disconnect(&mut self) -> Result<(), NetworkError>;
    
    /// Autentica o worker
    async fn authorize(&mut self, worker: &str, password: &str) -> Result<(), NetworkError>;
    
    /// Submete uma share
    async fn submit_share(&mut self, share: &Share) -> Result<ShareResult, NetworkError>;
    
    /// Recebe o próximo job (blocking)
    async fn receive_job(&mut self) -> Result<MiningJob, NetworkError>;
    
    /// Verifica se a conexão está ativa
    fn is_connected(&self) -> bool;
    
    /// Retorna estatísticas de rede
    fn get_stats(&self) -> NetworkStats;
}
