//! HyperMine Config — Gerenciamento de Configuração com Hot-Reload
//!
//! Este módulo carrega, valida e distribui configurações TOML para todos os
//! componentes do minerador. Suporta hot-reload via inotify/FSEvents.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::{Path, PathBuf};

// ============================================================================
// Estruturas de Configuração
// ============================================================================

/// Configuração principal do minerador
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MinerConfig {
    pub general: GeneralConfig,
    pub hardware: HardwareConfig,
    pub cpu: CpuConfig,
    #[serde(rename = "gpu")]
    pub gpu: GpuConfig,
    pub network: NetworkConfig,
    pub monitoring: MonitoringConfig,
    pub logging: LoggingConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GeneralConfig {
    /// Nome do worker (identificação no pool)
    pub worker_name: String,
    /// Moedas habilitadas para mineração
    /// ["*"] = todas, ["bitcoin", "monero"] = específicas, ["*", "!doge"] = exclusão
    pub enabled_coins: Vec<String>,
    /// Estratégia de seleção de moeda
    pub coin_strategy: CoinStrategy,
    /// Intervalo de recálculo de lucratividade (segundos)
    #[serde(default = "default_profitability_interval")]
    pub profitability_interval: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CoinStrategy {
    MostProfitable,
    RoundRobin,
    Manual,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HardwareConfig {
    /// Dispositivos a utilizar: "auto" ou lista específica
    pub devices: DeviceSelection,
    /// Número máximo de threads CPU (0 = auto)
    #[serde(default)]
    pub max_cpu_threads: u32,
    /// Temperatura máxima da GPU em Celsius
    #[serde(default = "default_max_temp")]
    pub max_gpu_temperature: u32,
    /// Power limit em Watts (0 = sem limite)
    #[serde(default)]
    pub max_gpu_power: u32,
    /// Velocidade do fan em % (0 = auto)
    #[serde(default)]
    pub gpu_fan_speed: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(untagged)]
pub enum DeviceSelection {
    Auto(String),
    Specific(Vec<String>),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CpuConfig {
    #[serde(default = "default_true")]
    pub enable_huge_pages: bool,
    #[serde(default = "default_huge_page_size")]
    pub huge_page_size: String,
    #[serde(default = "default_true")]
    pub enable_numa: bool,
    #[serde(default = "default_priority")]
    pub priority: String,
    #[serde(default)]
    pub affinity: Vec<u32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GpuConfig {
    pub nvidia: Option<NvidiaConfig>,
    pub amd: Option<AmdConfig>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NvidiaConfig {
    #[serde(default = "default_auto")]
    pub cuda_compute_capability: String,
    #[serde(default)]
    pub enable_tensor_cores: bool,
    #[serde(default = "default_true")]
    pub persistent_kernel: bool,
    #[serde(default = "default_streams")]
    pub streams_per_gpu: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AmdConfig {
    #[serde(default = "default_auto")]
    pub opencl_platform: String,
    #[serde(default = "default_workgroup_size")]
    pub workgroup_size: u32,
    #[serde(default = "default_true")]
    pub enable_lds_optimization: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NetworkConfig {
    #[serde(default = "default_true")]
    pub tcp_nodelay: bool,
    #[serde(default = "default_keepalive")]
    pub keepalive_interval: u32,
    #[serde(default = "default_reconnect_delay")]
    pub reconnect_delay: u32,
    #[serde(default)]
    pub max_reconnect_attempts: u32,
    #[serde(default = "default_true")]
    pub prefer_stratum_v2: bool,
    #[serde(default = "default_true")]
    pub enable_tls: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MonitoringConfig {
    #[serde(default = "default_true")]
    pub api_enabled: bool,
    #[serde(default = "default_api_port")]
    pub api_port: u16,
    #[serde(default = "default_bind")]
    pub api_bind: String,
    #[serde(default = "default_true")]
    pub prometheus_enabled: bool,
    #[serde(default = "default_prometheus_port")]
    pub prometheus_port: u16,
    #[serde(default)]
    pub alerts: AlertsConfig,
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct AlertsConfig {
    #[serde(default)]
    pub enable_discord: bool,
    #[serde(default)]
    pub discord_webhook: String,
    #[serde(default)]
    pub enable_telegram: bool,
    #[serde(default)]
    pub telegram_bot_token: String,
    #[serde(default)]
    pub telegram_chat_id: String,
    #[serde(default = "default_hashrate_threshold")]
    pub hashrate_drop_threshold: u32,
    #[serde(default = "default_temp_threshold")]
    pub temperature_threshold: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LoggingConfig {
    #[serde(default = "default_log_level")]
    pub level: String,
    #[serde(default = "default_log_file")]
    pub file: String,
    #[serde(default = "default_log_max_size")]
    pub max_size: String,
    #[serde(default = "default_true")]
    pub rotate: bool,
}

/// Configuração de uma moeda individual
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CoinConfig {
    pub coin: CoinInfo,
    pub wallet: WalletConfig,
    pub pools: PoolsConfig,
    #[serde(default)]
    pub algorithm_params: HashMap<String, toml::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CoinInfo {
    pub name: String,
    pub symbol: String,
    pub algorithm: String,
    #[serde(default = "default_true")]
    pub enabled: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WalletConfig {
    pub address: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PoolsConfig {
    pub list: Vec<PoolEntry>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PoolEntry {
    pub url: String,
    #[serde(default = "default_password")]
    pub password: String,
    #[serde(default = "default_priority")]
    pub priority: u32,
    #[serde(default = "default_weight")]
    pub weight: u32,
}

// ============================================================================
// Funções Default
// ============================================================================

fn default_true() -> bool { true }
fn default_auto() -> String { "auto".to_string() }
fn default_priority() -> String { "high".to_string() }
fn default_huge_page_size() -> String { "2MB".to_string() }
fn default_streams() -> u32 { 2 }
fn default_workgroup_size() -> u32 { 256 }
fn default_keepalive() -> u32 { 30 }
fn default_reconnect_delay() -> u32 { 1 }
fn default_api_port() -> u16 { 8080 }
fn default_bind() -> String { "127.0.0.1".to_string() }
fn default_prometheus_port() -> u16 { 9090 }
fn default_hashrate_threshold() -> u32 { 10 }
fn default_temp_threshold() -> u32 { 85 }
fn default_max_temp() -> u32 { 80 }
fn default_log_level() -> String { "info".to_string() }
fn default_log_file() -> String { "hypermine.log".to_string() }
fn default_log_max_size() -> String { "100MB".to_string() }
fn default_profitability_interval() -> u64 { 300 }
fn default_password() -> String { "x".to_string() }
fn default_priority() -> u32 { 1 }
fn default_weight() -> u32 { 100 }

// ============================================================================
// Config Manager
// ============================================================================

/// Gerenciador de configuração com suporte a hot-reload
pub struct ConfigManager {
    config_path: PathBuf,
    coins_dir: PathBuf,
    current_config: MinerConfig,
    coin_configs: HashMap<String, CoinConfig>,
}

impl ConfigManager {
    /// Carrega a configuração a partir dos arquivos
    pub fn load(config_path: &Path) -> anyhow::Result<Self> {
        let config_str = std::fs::read_to_string(config_path)?;
        let current_config: MinerConfig = toml::from_str(&config_str)?;
        
        let coins_dir = config_path.parent()
            .unwrap_or(Path::new("."))
            .join("coins");
        
        let mut coin_configs = HashMap::new();
        
        if coins_dir.exists() {
            for entry in std::fs::read_dir(&coins_dir)? {
                let entry = entry?;
                let path = entry.path();
                if path.extension().map_or(false, |ext| ext == "toml") {
                    let coin_str = std::fs::read_to_string(&path)?;
                    let coin_config: CoinConfig = toml::from_str(&coin_str)?;
                    let name = coin_config.coin.symbol.to_lowercase();
                    coin_configs.insert(name, coin_config);
                }
            }
        }
        
        Ok(Self {
            config_path: config_path.to_path_buf(),
            coins_dir,
            current_config,
            coin_configs,
        })
    }
    
    /// Retorna a configuração atual
    pub fn config(&self) -> &MinerConfig {
        &self.current_config
    }
    
    /// Retorna as configurações de moedas
    pub fn coins(&self) -> &HashMap<String, CoinConfig> {
        &self.coin_configs
    }
    
    /// Retorna as moedas habilitadas com base na configuração
    pub fn enabled_coins(&self) -> Vec<&CoinConfig> {
        let enabled = &self.current_config.general.enabled_coins;
        
        if enabled.contains(&"*".to_string()) {
            // Todas as moedas, exceto as com prefixo "!"
            let excluded: Vec<String> = enabled.iter()
                .filter(|s| s.starts_with('!'))
                .map(|s| s[1..].to_lowercase())
                .collect();
            
            self.coin_configs.values()
                .filter(|c| c.coin.enabled && !excluded.contains(&c.coin.symbol.to_lowercase()))
                .collect()
        } else {
            // Apenas as moedas listadas
            enabled.iter()
                .filter_map(|name| self.coin_configs.get(&name.to_lowercase()))
                .filter(|c| c.coin.enabled)
                .collect()
        }
    }
    
    /// Recarrega a configuração dos arquivos
    pub fn reload(&mut self) -> anyhow::Result<()> {
        let new_config = Self::load(&self.config_path)?;
        self.current_config = new_config.current_config;
        self.coin_configs = new_config.coin_configs;
        Ok(())
    }
}
