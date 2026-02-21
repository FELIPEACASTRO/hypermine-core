//! HyperMine Monitoring — API REST, Prometheus e Alertas
//!
//! Este módulo fornece monitoramento em tempo real do minerador,
//! incluindo API REST local, exportação Prometheus e alertas via webhook.

use serde::{Deserialize, Serialize};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;

// ============================================================================
// Métricas
// ============================================================================

/// Métricas globais do minerador (thread-safe via atomics)
#[derive(Debug)]
pub struct MinerMetrics {
    // Hashrate
    pub total_hashes: AtomicU64,
    pub hashrate_1s: AtomicU64,
    pub hashrate_60s: AtomicU64,
    pub hashrate_15m: AtomicU64,
    
    // Shares
    pub shares_accepted: AtomicU64,
    pub shares_rejected: AtomicU64,
    pub shares_stale: AtomicU64,
    
    // Uptime
    pub start_time: std::time::Instant,
    
    // Dispositivos
    pub devices: Vec<DeviceMetrics>,
}

/// Métricas por dispositivo
#[derive(Debug)]
pub struct DeviceMetrics {
    pub device_id: String,
    pub device_type: DeviceType,
    pub hashrate: AtomicU64,
    pub temperature: AtomicU64,    // em centésimos de grau (ex: 7500 = 75.00°C)
    pub power_draw: AtomicU64,     // em miliwatts
    pub fan_speed: AtomicU64,      // em %
    pub memory_used: AtomicU64,    // em bytes
    pub memory_total: AtomicU64,   // em bytes
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum DeviceType {
    Cpu,
    GpuNvidia,
    GpuAmd,
    Fpga,
}

// ============================================================================
// API REST — Respostas
// ============================================================================

/// Resposta da API: status geral
#[derive(Debug, Serialize, Deserialize)]
pub struct StatusResponse {
    pub version: String,
    pub uptime_seconds: u64,
    pub algorithm: String,
    pub coin: String,
    pub pool: String,
    pub hashrate: HashrateInfo,
    pub shares: SharesInfo,
    pub devices: Vec<DeviceInfo>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct HashrateInfo {
    pub current: f64,
    pub average_60s: f64,
    pub average_15m: f64,
    pub unit: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SharesInfo {
    pub accepted: u64,
    pub rejected: u64,
    pub stale: u64,
    pub acceptance_rate: f64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DeviceInfo {
    pub id: String,
    pub device_type: String,
    pub name: String,
    pub hashrate: f64,
    pub temperature: f64,
    pub power_draw: f64,
    pub fan_speed: u32,
    pub memory_used_mb: f64,
    pub memory_total_mb: f64,
    pub efficiency: f64, // hash/watt
}

// ============================================================================
// Prometheus — Exportador de Métricas
// ============================================================================

/// Gera métricas no formato Prometheus
pub fn generate_prometheus_metrics(metrics: &MinerMetrics) -> String {
    let mut output = String::new();
    
    // Hashrate total
    output.push_str("# HELP hypermine_hashrate_total Total hashrate in H/s\n");
    output.push_str("# TYPE hypermine_hashrate_total gauge\n");
    output.push_str(&format!(
        "hypermine_hashrate_total {}\n",
        metrics.hashrate_1s.load(Ordering::Relaxed)
    ));
    
    // Shares
    output.push_str("# HELP hypermine_shares_accepted Total accepted shares\n");
    output.push_str("# TYPE hypermine_shares_accepted counter\n");
    output.push_str(&format!(
        "hypermine_shares_accepted {}\n",
        metrics.shares_accepted.load(Ordering::Relaxed)
    ));
    
    output.push_str("# HELP hypermine_shares_rejected Total rejected shares\n");
    output.push_str("# TYPE hypermine_shares_rejected counter\n");
    output.push_str(&format!(
        "hypermine_shares_rejected {}\n",
        metrics.shares_rejected.load(Ordering::Relaxed)
    ));
    
    // Métricas por dispositivo
    for device in &metrics.devices {
        let id = &device.device_id;
        let temp = device.temperature.load(Ordering::Relaxed) as f64 / 100.0;
        let power = device.power_draw.load(Ordering::Relaxed) as f64 / 1000.0;
        
        output.push_str(&format!(
            "hypermine_device_hashrate{{device=\"{}\"}} {}\n",
            id,
            device.hashrate.load(Ordering::Relaxed)
        ));
        output.push_str(&format!(
            "hypermine_device_temperature{{device=\"{}\"}} {:.1}\n",
            id, temp
        ));
        output.push_str(&format!(
            "hypermine_device_power_watts{{device=\"{}\"}} {:.1}\n",
            id, power
        ));
    }
    
    // Uptime
    output.push_str("# HELP hypermine_uptime_seconds Miner uptime in seconds\n");
    output.push_str("# TYPE hypermine_uptime_seconds counter\n");
    output.push_str(&format!(
        "hypermine_uptime_seconds {}\n",
        metrics.start_time.elapsed().as_secs()
    ));
    
    output
}

// ============================================================================
// Alertas
// ============================================================================

/// Tipos de alerta
#[derive(Debug, Clone, Serialize)]
pub enum AlertType {
    HighTemperature { device: String, temperature: f64, threshold: f64 },
    LowHashrate { current: f64, expected: f64, drop_percent: f64 },
    PoolDisconnected { pool: String },
    HighRejectRate { rate: f64, threshold: f64 },
    DeviceError { device: String, error: String },
}

/// Envia alerta via webhook
pub async fn send_webhook_alert(
    webhook_url: &str,
    alert: &AlertType,
) -> Result<(), Box<dyn std::error::Error>> {
    let message = match alert {
        AlertType::HighTemperature { device, temperature, threshold } => {
            format!(
                "⚠️ **Temperatura Alta** — Dispositivo `{}`: {:.1}°C (limite: {:.1}°C)",
                device, temperature, threshold
            )
        }
        AlertType::LowHashrate { current, expected, drop_percent } => {
            format!(
                "📉 **Hashrate Baixo** — Atual: {:.2} H/s, Esperado: {:.2} H/s (queda de {:.1}%)",
                current, expected, drop_percent
            )
        }
        AlertType::PoolDisconnected { pool } => {
            format!("🔌 **Pool Desconectado** — {}", pool)
        }
        AlertType::HighRejectRate { rate, threshold } => {
            format!(
                "❌ **Taxa de Rejeição Alta** — {:.1}% (limite: {:.1}%)",
                rate, threshold
            )
        }
        AlertType::DeviceError { device, error } => {
            format!("🚨 **Erro no Dispositivo** — `{}`: {}", device, error)
        }
    };
    
    let payload = serde_json::json!({
        "content": message
    });
    
    let client = reqwest::Client::new();
    client.post(webhook_url)
        .json(&payload)
        .send()
        .await?;
    
    Ok(())
}
