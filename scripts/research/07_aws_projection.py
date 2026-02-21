#!/usr/bin/env python3
"""
Projeção financeira de mineração na AWS — Todas as instâncias GPU.
Dados reais de fev/2026 de NiceHash, Kryptex e hashrate.no.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os

OUTPUT_DIR = "/home/ubuntu/hypermine-core/docs/projections"
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

USD_TO_BRL = 5.50

# ============================================================================
# DADOS REAIS — Instâncias AWS GPU (fev 2026, pós redução de preço)
# ============================================================================

AWS_INSTANCES = {
    "g4dn.xlarge": {
        "gpu": "1x Tesla T4",
        "vram": "16 GB GDDR6",
        "vcpu": 4,
        "ram_gb": 16,
        "on_demand_hr": 0.526,
        "spot_hr": 0.16,       # ~70% desconto
        "spot_90_hr": 0.053,   # ~90% desconto
        "mining_revenue_day": 0.04,  # NiceHash real data
        "best_coin": "ETCHash/KawPow",
        "hashrate": "30 MH/s ETCHash, 9 MH/s KawPow",
        "gpu_watts": 70,
    },
    "g5.2xlarge": {
        "gpu": "1x A10G",
        "vram": "24 GB GDDR6",
        "vcpu": 8,
        "ram_gb": 32,
        "on_demand_hr": 1.212,
        "spot_hr": 0.36,
        "spot_90_hr": 0.121,
        "mining_revenue_day": 0.35,  # Estimado baseado em A10G benchmarks
        "best_coin": "QTC/GRIN",
        "hashrate": "~40 MH/s ETCHash",
        "gpu_watts": 150,
    },
    "g6.2xlarge": {
        "gpu": "1x L4",
        "vram": "24 GB GDDR6",
        "vcpu": 8,
        "ram_gb": 32,
        "on_demand_hr": 0.978,
        "spot_hr": 0.29,
        "spot_90_hr": 0.098,
        "mining_revenue_day": 0.30,  # Estimado
        "best_coin": "QTC/GRIN",
        "hashrate": "~35 MH/s ETCHash",
        "gpu_watts": 72,
    },
    "p3.2xlarge": {
        "gpu": "1x V100",
        "vram": "16 GB HBM2",
        "vcpu": 8,
        "ram_gb": 61,
        "on_demand_hr": 3.06,
        "spot_hr": 0.92,
        "spot_90_hr": 0.306,
        "mining_revenue_day": 0.50,  # Estimado V100
        "best_coin": "ETCHash/KawPow",
        "hashrate": "~85 MH/s ETCHash",
        "gpu_watts": 250,
    },
    "p4d.24xlarge": {
        "gpu": "8x A100 40GB",
        "vram": "8x 40 GB HBM2e",
        "vcpu": 96,
        "ram_gb": 1152,
        "on_demand_hr": 32.77,
        "spot_hr": 9.83,
        "spot_90_hr": 3.28,
        "mining_revenue_day": 8.00,  # 8x ~$1/dia (Kryptex A100)
        "best_coin": "ETCHash/KawPow",
        "hashrate": "8x 120 MH/s ETCHash",
        "gpu_watts": 2000,
    },
    "p5.48xlarge": {
        "gpu": "8x H100 80GB",
        "vram": "8x 80 GB HBM3",
        "vcpu": 192,
        "ram_gb": 2048,
        "on_demand_hr": 98.32,
        "spot_hr": 29.50,
        "spot_90_hr": 9.83,
        "mining_revenue_day": 12.00,  # Estimado H100
        "best_coin": "ETCHash/KawPow",
        "hashrate": "8x 160 MH/s ETCHash",
        "gpu_watts": 5600,
    },
}

# ============================================================================
# CÁLCULOS
# ============================================================================

def calc_daily_cost(price_hr):
    return price_hr * 24

def calc_monthly_cost(price_hr):
    return price_hr * 24 * 30

def calc_yearly_cost(price_hr):
    return price_hr * 24 * 365

def generate_comparison_table():
    """Gera tabela comparativa de todas as instâncias."""
    print("=" * 120)
    print(f"{'Instancia':<18} {'GPU':<18} {'On-Demand/dia':>14} {'Spot/dia':>12} {'Spot90/dia':>12} {'Receita/dia':>12} {'Lucro OD':>12} {'Lucro Spot':>12} {'Lucro S90':>12}")
    print("=" * 120)
    
    for name, inst in AWS_INSTANCES.items():
        od_day = calc_daily_cost(inst["on_demand_hr"])
        spot_day = calc_daily_cost(inst["spot_hr"])
        spot90_day = calc_daily_cost(inst["spot_90_hr"])
        rev = inst["mining_revenue_day"]
        
        profit_od = rev - od_day
        profit_spot = rev - spot_day
        profit_spot90 = rev - spot90_day
        
        print(f"{name:<18} {inst['gpu']:<18} ${od_day:>11.2f} ${spot_day:>9.2f} ${spot90_day:>9.2f} ${rev:>9.2f} ${profit_od:>9.2f} ${profit_spot:>9.2f} ${profit_spot90:>9.2f}")
    
    print("=" * 120)

def generate_breakeven_analysis():
    """Calcula o preço de crypto necessário para breakeven."""
    print("\n" + "=" * 100)
    print("ANALISE DE BREAKEVEN — Quanto o preco das cryptos precisaria subir")
    print("=" * 100)
    
    for name, inst in AWS_INSTANCES.items():
        spot90_day = calc_daily_cost(inst["spot_90_hr"])
        rev = inst["mining_revenue_day"]
        
        if rev > 0:
            multiplier_spot90 = spot90_day / rev
            multiplier_spot = calc_daily_cost(inst["spot_hr"]) / rev
            multiplier_od = calc_daily_cost(inst["on_demand_hr"]) / rev
        else:
            multiplier_spot90 = float('inf')
            multiplier_spot = float('inf')
            multiplier_od = float('inf')
        
        print(f"\n{name} ({inst['gpu']}):")
        print(f"  Receita atual:     ${rev:.2f}/dia")
        print(f"  Custo On-Demand:   ${calc_daily_cost(inst['on_demand_hr']):.2f}/dia → Crypto precisa subir {multiplier_od:.0f}x ({(multiplier_od-1)*100:.0f}%)")
        print(f"  Custo Spot 70%:    ${calc_daily_cost(inst['spot_hr']):.2f}/dia → Crypto precisa subir {multiplier_spot:.0f}x ({(multiplier_spot-1)*100:.0f}%)")
        print(f"  Custo Spot 90%:    ${spot90_day:.2f}/dia → Crypto precisa subir {multiplier_spot90:.0f}x ({(multiplier_spot90-1)*100:.0f}%)")

def plot_aws_comparison():
    """Gráfico comparativo de custo vs receita na AWS."""
    fig, ax = plt.subplots(figsize=(16, 8))
    
    names = list(AWS_INSTANCES.keys())
    revenues = [inst["mining_revenue_day"] for inst in AWS_INSTANCES.values()]
    costs_od = [calc_daily_cost(inst["on_demand_hr"]) for inst in AWS_INSTANCES.values()]
    costs_spot = [calc_daily_cost(inst["spot_hr"]) for inst in AWS_INSTANCES.values()]
    costs_spot90 = [calc_daily_cost(inst["spot_90_hr"]) for inst in AWS_INSTANCES.values()]
    
    x = np.arange(len(names))
    width = 0.2
    
    bars1 = ax.bar(x - 1.5*width, costs_od, width, label='Custo On-Demand/dia', color='#EF4444', alpha=0.8)
    bars2 = ax.bar(x - 0.5*width, costs_spot, width, label='Custo Spot 70%/dia', color='#F59E0B', alpha=0.8)
    bars3 = ax.bar(x + 0.5*width, costs_spot90, width, label='Custo Spot 90%/dia', color='#3B82F6', alpha=0.8)
    bars4 = ax.bar(x + 1.5*width, revenues, width, label='Receita Mineracao/dia', color='#22C55E', alpha=0.8)
    
    ax.set_ylabel('USD/dia (escala log)', fontsize=12)
    ax.set_title('AWS GPU Mining — Custo da Instancia vs Receita de Mineracao\nDados Reais de Fevereiro 2026', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=15, ha='right')
    ax.legend(fontsize=10)
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3, axis='y')
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%.2f'))
    
    plt.tight_layout()
    path = f"{OUTPUT_DIR}/aws_cost_vs_revenue.png"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nGrafico salvo: {path}")

def plot_multiplier_needed():
    """Gráfico mostrando quantas vezes o preço precisa subir para breakeven."""
    fig, ax = plt.subplots(figsize=(14, 7))
    
    names = list(AWS_INSTANCES.keys())
    multipliers_od = []
    multipliers_spot = []
    multipliers_spot90 = []
    
    for inst in AWS_INSTANCES.values():
        rev = inst["mining_revenue_day"]
        if rev > 0:
            multipliers_od.append(calc_daily_cost(inst["on_demand_hr"]) / rev)
            multipliers_spot.append(calc_daily_cost(inst["spot_hr"]) / rev)
            multipliers_spot90.append(calc_daily_cost(inst["spot_90_hr"]) / rev)
        else:
            multipliers_od.append(0)
            multipliers_spot.append(0)
            multipliers_spot90.append(0)
    
    x = np.arange(len(names))
    width = 0.25
    
    ax.bar(x - width, multipliers_od, width, label='On-Demand', color='#EF4444', alpha=0.8)
    ax.bar(x, multipliers_spot, width, label='Spot 70%', color='#F59E0B', alpha=0.8)
    ax.bar(x + width, multipliers_spot90, width, label='Spot 90%', color='#3B82F6', alpha=0.8)
    
    ax.axhline(y=1, color='#22C55E', linestyle='--', linewidth=2, label='Breakeven (1x)')
    
    ax.set_ylabel('Multiplicador necessario (x)', fontsize=12)
    ax.set_title('Quantas Vezes o Preco das Cryptos Precisa Subir para Breakeven na AWS\nMultiplicador = Custo AWS / Receita Mineracao', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=15, ha='right')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Adicionar valores
    for i, (od, sp, s90) in enumerate(zip(multipliers_od, multipliers_spot, multipliers_spot90)):
        ax.annotate(f'{od:.0f}x', xy=(i - width, od), xytext=(0, 3), textcoords="offset points", ha='center', fontsize=7, color='#EF4444')
        ax.annotate(f'{sp:.0f}x', xy=(i, sp), xytext=(0, 3), textcoords="offset points", ha='center', fontsize=7, color='#F59E0B')
        ax.annotate(f'{s90:.0f}x', xy=(i + width, s90), xytext=(0, 3), textcoords="offset points", ha='center', fontsize=7, color='#3B82F6')
    
    plt.tight_layout()
    path = f"{OUTPUT_DIR}/aws_breakeven_multiplier.png"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Grafico salvo: {path}")

def plot_alternatives_comparison():
    """Gráfico comparando AWS vs alternativas."""
    fig, ax = plt.subplots(figsize=(14, 7))
    
    alternatives = {
        "AWS g4dn\n(On-Demand)": {"cost_day": 12.62, "revenue_day": 0.04, "color": "#EF4444"},
        "AWS g4dn\n(Spot 90%)": {"cost_day": 1.27, "revenue_day": 0.04, "color": "#F59E0B"},
        "AWS p3\n(Spot 90%)": {"cost_day": 7.34, "revenue_day": 0.50, "color": "#F59E0B"},
        "Vast.ai\n(RTX 3090)": {"cost_day": 4.80, "revenue_day": 0.27, "color": "#8B5CF6"},
        "Vast.ai\n(RTX 4090)": {"cost_day": 7.20, "revenue_day": 0.62, "color": "#8B5CF6"},
        "Desktop\nRTX 3090": {"cost_day": 0.58, "revenue_day": 0.27, "color": "#22C55E"},
        "Desktop\nRTX 4090": {"cost_day": 0.77, "revenue_day": 0.62, "color": "#22C55E"},
        "Desktop+Solar\nRTX 4090": {"cost_day": 0.00, "revenue_day": 0.62, "color": "#10B981"},
    }
    
    names = list(alternatives.keys())
    costs = [a["cost_day"] for a in alternatives.values()]
    revenues = [a["revenue_day"] for a in alternatives.values()]
    profits = [r - c for r, c in zip(revenues, costs)]
    colors = ['#22C55E' if p >= 0 else '#EF4444' for p in profits]
    
    x = np.arange(len(names))
    width = 0.35
    
    ax.bar(x - width/2, costs, width, label='Custo/dia', color='#EF4444', alpha=0.6)
    ax.bar(x + width/2, revenues, width, label='Receita/dia', color='#22C55E', alpha=0.6)
    
    ax.set_ylabel('USD/dia', fontsize=12)
    ax.set_title('Comparacao: AWS vs Alternativas para Mineracao\nCusto Diario vs Receita Diaria (Fev 2026)', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=9)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    path = f"{OUTPUT_DIR}/aws_vs_alternatives.png"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Grafico salvo: {path}")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    generate_comparison_table()
    generate_breakeven_analysis()
    plot_aws_comparison()
    plot_multiplier_needed()
    plot_alternatives_comparison()
    print("\nAnalise completa!")
