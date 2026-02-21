//! HyperMine Engine — Motor Principal de Mineração
//!
//! O Engine coordena todos os componentes do minerador:
//! configuração, algoritmos, hardware, rede e monitoramento.

pub mod dispatcher;
pub mod worker;

use hypermine_config::ConfigManager;
use hypermine_network::{Algorithm, MiningJob, Share, ShareResult};
use std::sync::Arc;

// ============================================================================
// Engine — Motor Principal
// ============================================================================

/// Estado do motor de mineração
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EngineState {
    /// Motor inicializado mas não minerando
    Idle,
    /// Conectando ao pool
    Connecting,
    /// Minerando ativamente
    Mining,
    /// Pausado (por temperatura, configuração, etc.)
    Paused,
    /// Trocando de algoritmo/moeda
    Switching,
    /// Parando
    Stopping,
    /// Parado
    Stopped,
}

/// Informações sobre o dispositivo de hardware
#[derive(Debug, Clone)]
pub struct HardwareDevice {
    pub id: String,
    pub name: String,
    pub device_type: DeviceType,
    pub compute_units: u32,
    pub memory_bytes: u64,
    pub features: Vec<String>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DeviceType {
    Cpu,
    GpuNvidia,
    GpuAmd,
    Fpga,
}

/// Resultado de detecção de hardware
#[derive(Debug, Clone)]
pub struct HardwareInfo {
    pub cpu: CpuInfo,
    pub gpus: Vec<GpuInfo>,
}

#[derive(Debug, Clone)]
pub struct CpuInfo {
    pub name: String,
    pub cores: u32,
    pub threads: u32,
    pub features: CpuFeatures,
    pub cache_l3_kb: u32,
    pub numa_nodes: u32,
}

#[derive(Debug, Clone)]
pub struct CpuFeatures {
    pub sse42: bool,
    pub avx2: bool,
    pub avx512f: bool,
    pub avx512vl: bool,
    pub sha_ni: bool,
    pub aes_ni: bool,
    pub neon: bool,
    pub arm_sha2: bool,
}

#[derive(Debug, Clone)]
pub struct GpuInfo {
    pub id: u32,
    pub name: String,
    pub vendor: GpuVendor,
    pub memory_bytes: u64,
    pub compute_units: u32,
    pub clock_mhz: u32,
    pub pcie_bandwidth_gbps: f32,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum GpuVendor {
    Nvidia,
    Amd,
    Intel,
    Unknown,
}

// ============================================================================
// Dispatcher — Mapeamento Algoritmo → Hardware
// ============================================================================

/// Mapeia algoritmos para a melhor implementação disponível
pub fn select_best_implementation(
    algorithm: Algorithm,
    cpu_features: &CpuFeatures,
    gpus: &[GpuInfo],
) -> ImplementationChoice {
    match algorithm {
        // SHA-256: prioriza SHA-NI > AVX-512 > AVX2 > SSE4.2 > genérico
        Algorithm::Sha256 => {
            if cpu_features.sha_ni {
                ImplementationChoice::CpuShaNi
            } else if cpu_features.avx512f {
                ImplementationChoice::CpuAvx512
            } else if cpu_features.avx2 {
                ImplementationChoice::CpuAvx2
            } else if cpu_features.sse42 {
                ImplementationChoice::CpuSse42
            } else if cpu_features.arm_sha2 {
                ImplementationChoice::CpuArmSha2
            } else if cpu_features.neon {
                ImplementationChoice::CpuNeon
            } else {
                ImplementationChoice::CpuGeneric
            }
        }
        
        // RandomX: sempre CPU (projetado para resistir GPU/ASIC)
        Algorithm::RandomX => {
            if cpu_features.aes_ni {
                ImplementationChoice::CpuAesNi
            } else {
                ImplementationChoice::CpuGeneric
            }
        }
        
        // Ethash/Etchash: prioriza GPU
        Algorithm::Ethash | Algorithm::Etchash => {
            if let Some(gpu) = gpus.first() {
                match gpu.vendor {
                    GpuVendor::Nvidia => ImplementationChoice::GpuCuda,
                    GpuVendor::Amd => ImplementationChoice::GpuOpenCl,
                    _ => ImplementationChoice::GpuOpenCl,
                }
            } else {
                ImplementationChoice::CpuGeneric
            }
        }
        
        // KAWPOW: GPU-only
        Algorithm::KawPow => {
            if let Some(gpu) = gpus.first() {
                match gpu.vendor {
                    GpuVendor::Nvidia => ImplementationChoice::GpuCuda,
                    _ => ImplementationChoice::GpuOpenCl,
                }
            } else {
                ImplementationChoice::Unsupported
            }
        }
        
        // Equihash: prioriza GPU
        Algorithm::Equihash200_9 | Algorithm::Equihash144_5 | Algorithm::Equihash192_7 => {
            if let Some(gpu) = gpus.first() {
                match gpu.vendor {
                    GpuVendor::Nvidia => ImplementationChoice::GpuCuda,
                    _ => ImplementationChoice::GpuOpenCl,
                }
            } else {
                ImplementationChoice::CpuGeneric
            }
        }
        
        // Yescrypt/YesPoWer: CPU-only
        Algorithm::Yescrypt | Algorithm::YesPoWer => {
            ImplementationChoice::CpuGeneric
        }
        
        // GhostRider: CPU preferido
        Algorithm::GhostRider => {
            if cpu_features.avx2 {
                ImplementationChoice::CpuAvx2
            } else {
                ImplementationChoice::CpuGeneric
            }
        }
        
        // Default: tenta GPU primeiro, fallback para CPU
        _ => {
            if !gpus.is_empty() {
                if gpus[0].vendor == GpuVendor::Nvidia {
                    ImplementationChoice::GpuCuda
                } else {
                    ImplementationChoice::GpuOpenCl
                }
            } else {
                ImplementationChoice::CpuGeneric
            }
        }
    }
}

/// Escolha de implementação para um algoritmo
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ImplementationChoice {
    CpuGeneric,
    CpuSse42,
    CpuAvx2,
    CpuAvx512,
    CpuShaNi,
    CpuAesNi,
    CpuNeon,
    CpuArmSha2,
    CpuAssembly,
    GpuCuda,
    GpuOpenCl,
    Fpga,
    Unsupported,
}

impl std::fmt::Display for ImplementationChoice {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::CpuGeneric => write!(f, "CPU (Generic)"),
            Self::CpuSse42 => write!(f, "CPU (SSE4.2)"),
            Self::CpuAvx2 => write!(f, "CPU (AVX2)"),
            Self::CpuAvx512 => write!(f, "CPU (AVX-512)"),
            Self::CpuShaNi => write!(f, "CPU (SHA-NI)"),
            Self::CpuAesNi => write!(f, "CPU (AES-NI)"),
            Self::CpuNeon => write!(f, "CPU (ARM NEON)"),
            Self::CpuArmSha2 => write!(f, "CPU (ARM SHA2)"),
            Self::CpuAssembly => write!(f, "CPU (Assembly)"),
            Self::GpuCuda => write!(f, "GPU (CUDA)"),
            Self::GpuOpenCl => write!(f, "GPU (OpenCL)"),
            Self::Fpga => write!(f, "FPGA"),
            Self::Unsupported => write!(f, "Unsupported"),
        }
    }
}
