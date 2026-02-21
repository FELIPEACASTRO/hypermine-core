#!/usr/bin/env python3
"""
HyperMine Core — Módulo de Profit-Switching Inteligente com Machine Learning

Este módulo implementa um sistema completo de profit-switching que utiliza
Machine Learning (XGBoost/LightGBM/Random Forest) para prever qual moeda
será mais lucrativa nas próximas horas e trocar automaticamente o algoritmo
de mineração para maximizar o lucro.

Arquitetura:
    Data Collector → Feature Engineer → ML Predictor → Decision Engine → Executor

Autor: HyperMine Core Team
Licença: MIT
"""

import os
import sys
import json
import time
import socket
import logging
import hashlib
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import pandas as pd
import requests
import joblib
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler

try:
    from xgboost import XGBRegressor
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

try:
    from lightgbm import LGBMRegressor
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

from sklearn.ensemble import RandomForestRegressor, VotingRegressor

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

class Config:
    """Configuração centralizada do módulo de profit-switching."""

    # APIs
    COINGECKO_API = "https://api.coingecko.com/api/v3"
    WHATTOMINE_API = "https://whattomine.com/coins.json"
    MINERSTAT_API = "https://api.minerstat.com/v2/coins"

    # Intervalos
    COLLECTION_INTERVAL_SEC = 300       # 5 minutos
    PREDICTION_INTERVAL_SEC = 300       # 5 minutos
    RETRAIN_INTERVAL_SEC = 86400        # 24 horas
    MIN_DATA_POINTS_FOR_TRAINING = 100  # Mínimo de pontos para treinar

    # Hysteresis (evitar trocas muito frequentes)
    HYSTERESIS_THRESHOLD_PCT = 0.05     # 5% de melhoria mínima para trocar
    MIN_MINING_TIME_SEC = 600           # 10 minutos mínimo em cada moeda
    MAX_SWITCHES_PER_HOUR = 3           # Máximo de trocas por hora

    # Caminhos
    DATA_DIR = Path("data")
    MODELS_DIR = Path("models")
    HISTORICAL_DATA_FILE = DATA_DIR / "historical_mining_data.csv"
    FEATURE_COLS_FILE = MODELS_DIR / "feature_columns.json"
    SCALER_FILE = MODELS_DIR / "scaler.pkl"
    STATE_FILE = DATA_DIR / "current_state.json"

    # Comunicação com minerador
    MINER_SOCKET_PATH = "/tmp/hypermine_control.sock"
    MINER_CONFIG_FILE = Path("switch_command.json")
    MINER_SOCKET_TIMEOUT = 5

    # Hardware padrão (será sobrescrito pela config do usuário)
    DEFAULT_HARDWARE = {
        "gpu_model": "GTX 1650",
        "gpu_vram_gb": 4,
        "gpu_tdp_watts": 50,
        "system_total_watts": 120,
        "cpu_model": "i5-9300H",
        "cpu_threads": 8
    }

    # Custo de energia padrão
    DEFAULT_ENERGY_COST_USD_KWH = 0.16  # Brasil: ~R$0.88/kWh

    # Pool fees padrão
    DEFAULT_POOL_FEES_PCT = 0.01  # 1%


# ============================================================================
# DEFINIÇÃO DE MOEDAS E ALGORITMOS
# ============================================================================

# Mapeamento completo de moedas mineráveis por GPU/CPU (excluindo ASIC-only)
MINEABLE_COINS = {
    # === GPU Mining (VRAM-eficiente, viável para 4GB) ===
    "ergo": {
        "symbol": "ERG",
        "algorithm": "Autolykos2",
        "hardware": "GPU",
        "coingecko_id": "ergo",
        "hashrate_gtx1650": {"value": 36.0, "unit": "MH/s"},
        "power_watts": 50,
        "min_vram_gb": 2,
        "pool_url": "stratum+tcp://erg.2miners.com:8888",
        "asic_resistant": True
    },
    "ravencoin": {
        "symbol": "RVN",
        "algorithm": "KawPow",
        "hardware": "GPU",
        "coingecko_id": "ravencoin",
        "hashrate_gtx1650": {"value": 7.15, "unit": "MH/s"},
        "power_watts": 66,
        "min_vram_gb": 4,
        "pool_url": "stratum+tcp://rvn.2miners.com:6060",
        "asic_resistant": True
    },
    "flux": {
        "symbol": "FLUX",
        "algorithm": "ZelHash",
        "hardware": "GPU",
        "coingecko_id": "zelcash",
        "hashrate_gtx1650": {"value": 12.0, "unit": "Sol/s"},
        "power_watts": 50,
        "min_vram_gb": 2,
        "pool_url": "stratum+tcp://flux.2miners.com:9090",
        "asic_resistant": True
    },
    "firo": {
        "symbol": "FIRO",
        "algorithm": "FiroPow",
        "hardware": "GPU",
        "coingecko_id": "firo",
        "hashrate_gtx1650": {"value": 6.0, "unit": "MH/s"},
        "power_watts": 66,
        "min_vram_gb": 4,
        "pool_url": "stratum+tcp://firo.2miners.com:8181",
        "asic_resistant": True
    },
    "neoxa": {
        "symbol": "NEOX",
        "algorithm": "KawPow",
        "hardware": "GPU",
        "coingecko_id": "neoxa",
        "hashrate_gtx1650": {"value": 7.0, "unit": "MH/s"},
        "power_watts": 66,
        "min_vram_gb": 4,
        "pool_url": "stratum+tcp://pool.neoxa.net:3333",
        "asic_resistant": True
    },
    "clore": {
        "symbol": "CLORE",
        "algorithm": "KawPow",
        "hardware": "GPU",
        "coingecko_id": "clore-ai",
        "hashrate_gtx1650": {"value": 7.0, "unit": "MH/s"},
        "power_watts": 66,
        "min_vram_gb": 4,
        "pool_url": "stratum+tcp://clore.2miners.com:2020",
        "asic_resistant": True
    },
    "vertcoin": {
        "symbol": "VTC",
        "algorithm": "Verthash",
        "hardware": "GPU",
        "coingecko_id": "vertcoin",
        "hashrate_gtx1650": {"value": 300.0, "unit": "kH/s"},
        "power_watts": 50,
        "min_vram_gb": 2,
        "pool_url": "stratum+tcp://vtc.suprnova.cc:5678",
        "asic_resistant": True
    },
    "radiant": {
        "symbol": "RXD",
        "algorithm": "SHA512/256d",
        "hardware": "GPU",
        "coingecko_id": "radiant",
        "hashrate_gtx1650": {"value": 180.0, "unit": "MH/s"},
        "power_watts": 50,
        "min_vram_gb": 1,
        "pool_url": "stratum+tcp://rxd.2miners.com:4040",
        "asic_resistant": False
    },
    "iron_fish": {
        "symbol": "IRON",
        "algorithm": "FishHash",
        "hardware": "GPU",
        "coingecko_id": "iron-fish",
        "hashrate_gtx1650": {"value": 5.0, "unit": "MH/s"},
        "power_watts": 50,
        "min_vram_gb": 4,
        "pool_url": "stratum+tcp://iron.2miners.com:3030",
        "asic_resistant": True
    },
    "neurai": {
        "symbol": "XNA",
        "algorithm": "KawPow",
        "hardware": "GPU",
        "coingecko_id": "neurai",
        "hashrate_gtx1650": {"value": 7.0, "unit": "MH/s"},
        "power_watts": 66,
        "min_vram_gb": 4,
        "pool_url": "stratum+tcp://xna.pool.com:3333",
        "asic_resistant": True
    },
    "meowcoin": {
        "symbol": "MEWC",
        "algorithm": "MeowPow",
        "hardware": "GPU",
        "coingecko_id": "meowcoin",
        "hashrate_gtx1650": {"value": 6.5, "unit": "MH/s"},
        "power_watts": 66,
        "min_vram_gb": 4,
        "pool_url": "stratum+tcp://mewc.pool.com:3333",
        "asic_resistant": True
    },
    "dynex": {
        "symbol": "DNX",
        "algorithm": "DynexSolve",
        "hardware": "GPU",
        "coingecko_id": "dynex",
        "hashrate_gtx1650": {"value": 350.0, "unit": "MH/s"},
        "power_watts": 50,
        "min_vram_gb": 3,
        "pool_url": "stratum+tcp://dnx.pool.com:3333",
        "asic_resistant": True
    },
    "pyrin": {
        "symbol": "PYI",
        "algorithm": "PyrinHash",
        "hardware": "GPU",
        "coingecko_id": "pyrin",
        "hashrate_gtx1650": {"value": 150.0, "unit": "MH/s"},
        "power_watts": 50,
        "min_vram_gb": 2,
        "pool_url": "stratum+tcp://pyrin.pool.com:3333",
        "asic_resistant": True
    },

    # === CPU Mining ===
    "monero": {
        "symbol": "XMR",
        "algorithm": "RandomX",
        "hardware": "CPU",
        "coingecko_id": "monero",
        "hashrate_i5_9300h": {"value": 2.5, "unit": "kH/s"},
        "power_watts": 45,
        "min_vram_gb": 0,
        "pool_url": "stratum+tcp://xmr.2miners.com:2222",
        "asic_resistant": True
    },
    "raptoreum": {
        "symbol": "RTM",
        "algorithm": "GhostRider",
        "hardware": "CPU",
        "coingecko_id": "raptoreum",
        "hashrate_i5_9300h": {"value": 1.2, "unit": "kH/s"},
        "power_watts": 45,
        "min_vram_gb": 0,
        "pool_url": "stratum+tcp://rtm.suprnova.cc:3333",
        "asic_resistant": True
    },
    "zephyr": {
        "symbol": "ZEPH",
        "algorithm": "RandomX",
        "hardware": "CPU",
        "coingecko_id": "zephyr-protocol",
        "hashrate_i5_9300h": {"value": 2.5, "unit": "kH/s"},
        "power_watts": 45,
        "min_vram_gb": 0,
        "pool_url": "stratum+tcp://zeph.herominers.com:1123",
        "asic_resistant": True
    },
    "wownero": {
        "symbol": "WOW",
        "algorithm": "RandomX",
        "hardware": "CPU",
        "coingecko_id": "wownero",
        "hashrate_i5_9300h": {"value": 2.5, "unit": "kH/s"},
        "power_watts": 45,
        "min_vram_gb": 0,
        "pool_url": "stratum+tcp://wow.herominers.com:1234",
        "asic_resistant": True
    },
    "dero": {
        "symbol": "DERO",
        "algorithm": "AstroBWT",
        "hardware": "CPU",
        "coingecko_id": "dero",
        "hashrate_i5_9300h": {"value": 150.0, "unit": "H/s"},
        "power_watts": 45,
        "min_vram_gb": 0,
        "pool_url": "stratum+tcp://dero.herominers.com:1111",
        "asic_resistant": True
    },
    "veruscoin": {
        "symbol": "VRSC",
        "algorithm": "VerusHash",
        "hardware": "CPU",
        "coingecko_id": "verus-coin",
        "hashrate_i5_9300h": {"value": 1.5, "unit": "MH/s"},
        "power_watts": 45,
        "min_vram_gb": 0,
        "pool_url": "stratum+tcp://vrsc.pool.com:3333",
        "asic_resistant": True
    },
    "scala": {
        "symbol": "XLA",
        "algorithm": "RandomSFX",
        "hardware": "CPU",
        "coingecko_id": "scala",
        "hashrate_i5_9300h": {"value": 2.0, "unit": "kH/s"},
        "power_watts": 45,
        "min_vram_gb": 0,
        "pool_url": "stratum+tcp://xla.herominers.com:1111",
        "asic_resistant": True
    }
}


# ============================================================================
# DATA COLLECTOR
# ============================================================================

class DataCollector:
    """Coleta dados em tempo real de múltiplas APIs."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger("DataCollector")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "HyperMine-Core/1.0",
            "Accept": "application/json"
        })

    def collect_coingecko_prices(self, coin_ids: List[str]) -> Dict[str, Dict]:
        """Coleta preços atuais, volume 24h e market cap da CoinGecko."""
        try:
            ids_str = ",".join(coin_ids)
            resp = self.session.get(
                f"{self.config.COINGECKO_API}/simple/price",
                params={
                    "ids": ids_str,
                    "vs_currencies": "usd",
                    "include_24hr_vol": "true",
                    "include_market_cap": "true",
                    "include_24hr_change": "true"
                },
                timeout=30
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            self.logger.error(f"Erro CoinGecko: {e}")
            return {}

    def collect_coingecko_history(self, coin_id: str, days: int = 30) -> pd.DataFrame:
        """Coleta histórico de preços da CoinGecko."""
        try:
            resp = self.session.get(
                f"{self.config.COINGECKO_API}/coins/{coin_id}/market_chart",
                params={"vs_currency": "usd", "days": days, "interval": "daily"},
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json()
            if "prices" in data:
                df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                return df
        except Exception as e:
            self.logger.error(f"Erro histórico CoinGecko para {coin_id}: {e}")
        return pd.DataFrame()

    def collect_whattomine_data(self) -> Dict[str, Dict]:
        """Coleta dados de dificuldade, hashrate e block reward do WhatToMine."""
        try:
            resp = self.session.get(self.config.WHATTOMINE_API, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            result = {}
            if "coins" in data:
                for name, info in data["coins"].items():
                    result[name.lower()] = {
                        "algorithm": info.get("algorithm", ""),
                        "block_reward": float(info.get("block_reward", 0)),
                        "nethash": float(info.get("nethash", 0)),
                        "difficulty": float(info.get("difficulty", 0)),
                        "block_time": float(info.get("block_time", 0)),
                        "exchange_rate": float(info.get("exchange_rate", 0)),
                        "exchange_rate_vol": float(info.get("exchange_rate_vol", 0)),
                    }
            return result
        except Exception as e:
            self.logger.error(f"Erro WhatToMine: {e}")
            return {}

    def collect_all(self) -> pd.DataFrame:
        """Coleta todos os dados e retorna um DataFrame consolidado."""
        now = datetime.utcnow()
        coin_ids = [c["coingecko_id"] for c in MINEABLE_COINS.values()]

        # CoinGecko
        cg_data = self.collect_coingecko_prices(coin_ids)

        # WhatToMine
        wtm_data = self.collect_whattomine_data()

        rows = []
        for coin_key, coin_info in MINEABLE_COINS.items():
            cg_id = coin_info["coingecko_id"]
            cg = cg_data.get(cg_id, {})

            row = {
                "timestamp": now,
                "coin_key": coin_key,
                "symbol": coin_info["symbol"],
                "algorithm": coin_info["algorithm"],
                "hardware_type": coin_info["hardware"],
                "price_usd": cg.get("usd", 0),
                "volume_24h_usd": cg.get("usd_24h_vol", 0),
                "market_cap_usd": cg.get("usd_market_cap", 0),
                "price_change_24h_pct": cg.get("usd_24h_change", 0),
                "network_difficulty": 0,
                "network_hashrate": 0,
                "block_reward": 0,
                "block_time_sec": 0,
            }

            # Tentar match com WhatToMine
            for wtm_key, wtm_info in wtm_data.items():
                if coin_info["symbol"].lower() in wtm_key or \
                   coin_key in wtm_key:
                    row["network_difficulty"] = wtm_info["difficulty"]
                    row["network_hashrate"] = wtm_info["nethash"]
                    row["block_reward"] = wtm_info["block_reward"]
                    row["block_time_sec"] = wtm_info["block_time"]
                    break

            rows.append(row)

        return pd.DataFrame(rows)


# ============================================================================
# FEATURE ENGINEER
# ============================================================================

class FeatureEngineer:
    """Transforma dados brutos em features para o modelo de ML."""

    def __init__(self, config: Config, hardware: Dict):
        self.config = config
        self.hardware = hardware
        self.logger = logging.getLogger("FeatureEngineer")

    def create_features(self, df: pd.DataFrame, historical_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Cria features a partir dos dados brutos."""
        if df.empty:
            return df

        df_fe = df.copy()

        # Features temporais
        df_fe["hour_of_day"] = pd.to_datetime(df_fe["timestamp"]).dt.hour
        df_fe["day_of_week"] = pd.to_datetime(df_fe["timestamp"]).dt.dayofweek
        df_fe["is_weekend"] = (df_fe["day_of_week"] >= 5).astype(int)

        # Features de mercado
        df_fe["price_to_volume_ratio"] = df_fe["price_usd"] / (df_fe["volume_24h_usd"] + 1e-9)
        df_fe["log_market_cap"] = np.log1p(df_fe["market_cap_usd"])
        df_fe["log_volume"] = np.log1p(df_fe["volume_24h_usd"])

        # Features de rede
        df_fe["log_difficulty"] = np.log1p(df_fe["network_difficulty"])
        df_fe["log_nethash"] = np.log1p(df_fe["network_hashrate"])
        df_fe["blocks_per_day"] = np.where(
            df_fe["block_time_sec"] > 0,
            86400 / df_fe["block_time_sec"],
            0
        )

        # Features de hardware do usuário
        for coin_key, coin_info in MINEABLE_COINS.items():
            mask = df_fe["coin_key"] == coin_key

            if coin_info["hardware"] == "GPU":
                hr = coin_info.get("hashrate_gtx1650", {}).get("value", 0)
                pw = coin_info.get("power_watts", self.hardware.get("gpu_tdp_watts", 50))
            else:
                hr = coin_info.get("hashrate_i5_9300h", {}).get("value", 0)
                pw = coin_info.get("power_watts", 45)

            df_fe.loc[mask, "user_hashrate"] = hr
            df_fe.loc[mask, "user_power_watts"] = pw

        # Preencher NaN
        df_fe["user_hashrate"] = df_fe["user_hashrate"].fillna(0)
        df_fe["user_power_watts"] = df_fe["user_power_watts"].fillna(0)

        # Custo de energia
        energy_cost = self.config.DEFAULT_ENERGY_COST_USD_KWH
        system_watts = self.hardware.get("system_total_watts", 120)
        df_fe["energy_cost_per_day"] = (system_watts / 1000) * 24 * energy_cost

        # Receita estimada (cálculo direto)
        df_fe["estimated_coins_per_day"] = np.where(
            df_fe["network_hashrate"] > 0,
            df_fe["blocks_per_day"] * df_fe["block_reward"] *
            (df_fe["user_hashrate"] / (df_fe["network_hashrate"] + 1e-9)),
            0
        )
        pool_fees = self.config.DEFAULT_POOL_FEES_PCT
        df_fe["estimated_revenue_usd"] = (
            df_fe["estimated_coins_per_day"] * df_fe["price_usd"] * (1 - pool_fees)
        )
        df_fe["estimated_profit_usd"] = (
            df_fe["estimated_revenue_usd"] - df_fe["energy_cost_per_day"]
        )

        # Eficiência
        df_fe["revenue_per_watt"] = df_fe["estimated_revenue_usd"] / (df_fe["user_power_watts"] + 1e-9)
        df_fe["profit_per_watt"] = df_fe["estimated_profit_usd"] / (df_fe["user_power_watts"] + 1e-9)

        # Limpar infinitos
        df_fe = df_fe.replace([np.inf, -np.inf], np.nan)
        df_fe = df_fe.fillna(0)

        return df_fe

    @staticmethod
    def get_feature_columns() -> List[str]:
        """Retorna a lista de colunas de features para o modelo."""
        return [
            "price_usd", "volume_24h_usd", "market_cap_usd",
            "price_change_24h_pct", "network_difficulty", "network_hashrate",
            "block_reward", "block_time_sec",
            "hour_of_day", "day_of_week", "is_weekend",
            "price_to_volume_ratio", "log_market_cap", "log_volume",
            "log_difficulty", "log_nethash", "blocks_per_day",
            "user_hashrate", "user_power_watts", "energy_cost_per_day",
            "estimated_coins_per_day", "estimated_revenue_usd",
            "revenue_per_watt", "profit_per_watt"
        ]


# ============================================================================
# ML PREDICTOR
# ============================================================================

class MLPredictor:
    """Treina e usa modelos de ML para prever lucratividade."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger("MLPredictor")
        self.models: Dict[str, Any] = {}
        self.scaler: Optional[StandardScaler] = None
        self.feature_cols: List[str] = []

        # Criar diretórios
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        config.MODELS_DIR.mkdir(parents=True, exist_ok=True)

    def train(self, historical_df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Treina os modelos de ML com dados históricos."""
        if len(historical_df) < self.config.MIN_DATA_POINTS_FOR_TRAINING:
            self.logger.warning(
                f"Dados insuficientes ({len(historical_df)} < "
                f"{self.config.MIN_DATA_POINTS_FOR_TRAINING}). "
                "Usando estimativa direta."
            )
            return {}

        self.feature_cols = FeatureEngineer.get_feature_columns()
        available_cols = [c for c in self.feature_cols if c in historical_df.columns]

        X = historical_df[available_cols].fillna(0)
        y = historical_df["estimated_profit_usd"].fillna(0)

        # Normalização
        self.scaler = StandardScaler()
        X_scaled = pd.DataFrame(
            self.scaler.fit_transform(X),
            columns=available_cols,
            index=X.index
        )

        # Split temporal
        tscv = TimeSeriesSplit(n_splits=3)
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, shuffle=False
        )

        # Modelos
        model_configs = {}
        if HAS_XGBOOST:
            model_configs["xgboost"] = XGBRegressor(
                objective="reg:squarederror",
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1
            )
        if HAS_LIGHTGBM:
            model_configs["lightgbm"] = LGBMRegressor(
                objective="regression",
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1,
                verbose=-1
            )
        model_configs["random_forest"] = RandomForestRegressor(
            n_estimators=200,
            max_depth=8,
            random_state=42,
            n_jobs=-1
        )

        metrics = {}
        for name, model in model_configs.items():
            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)

                metrics[name] = {"RMSE": rmse, "MAE": mae, "R2": r2}
                self.models[name] = model

                # Salvar modelo
                joblib.dump(model, self.config.MODELS_DIR / f"{name}.pkl")
                self.logger.info(
                    f"Modelo {name} treinado — RMSE: {rmse:.6f}, "
                    f"MAE: {mae:.6f}, R²: {r2:.4f}"
                )
            except Exception as e:
                self.logger.error(f"Erro ao treinar {name}: {e}")

        # Salvar scaler e feature cols
        joblib.dump(self.scaler, self.config.SCALER_FILE)
        with open(self.config.FEATURE_COLS_FILE, "w") as f:
            json.dump(available_cols, f)

        return metrics

    def predict(self, current_df: pd.DataFrame) -> pd.DataFrame:
        """Faz predições de lucratividade para os dados atuais."""
        if not self.models:
            # Sem modelos treinados, usar estimativa direta
            return current_df[["coin_key", "symbol", "estimated_profit_usd"]].rename(
                columns={"estimated_profit_usd": "predicted_profit_usd"}
            )

        available_cols = [c for c in self.feature_cols if c in current_df.columns]
        X = current_df[available_cols].fillna(0)

        if self.scaler is not None:
            X_scaled = pd.DataFrame(
                self.scaler.transform(X),
                columns=available_cols,
                index=X.index
            )
        else:
            X_scaled = X

        # Ensemble: média ponderada das predições
        predictions = []
        weights = []
        for name, model in self.models.items():
            try:
                pred = model.predict(X_scaled)
                predictions.append(pred)
                # Peso baseado no tipo de modelo
                w = {"xgboost": 0.4, "lightgbm": 0.35, "random_forest": 0.25}
                weights.append(w.get(name, 0.33))
            except Exception as e:
                self.logger.error(f"Erro na predição com {name}: {e}")

        if predictions:
            weights = np.array(weights)
            weights /= weights.sum()
            ensemble_pred = np.average(predictions, axis=0, weights=weights)
        else:
            ensemble_pred = current_df["estimated_profit_usd"].values

        result = current_df[["coin_key", "symbol"]].copy()
        result["predicted_profit_usd"] = ensemble_pred
        return result

    def load_models(self) -> bool:
        """Carrega modelos previamente treinados."""
        try:
            if self.config.FEATURE_COLS_FILE.exists():
                with open(self.config.FEATURE_COLS_FILE) as f:
                    self.feature_cols = json.load(f)

            if self.config.SCALER_FILE.exists():
                self.scaler = joblib.load(self.config.SCALER_FILE)

            for name in ["xgboost", "lightgbm", "random_forest"]:
                path = self.config.MODELS_DIR / f"{name}.pkl"
                if path.exists():
                    self.models[name] = joblib.load(path)
                    self.logger.info(f"Modelo {name} carregado.")

            return bool(self.models)
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelos: {e}")
            return False


# ============================================================================
# DECISION ENGINE
# ============================================================================

class DecisionEngine:
    """Motor de decisão com hysteresis para evitar trocas excessivas."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger("DecisionEngine")
        self.current_coin: Optional[str] = None
        self.current_profit: float = 0.0
        self.last_switch_time: datetime = datetime.min
        self.switches_this_hour: int = 0
        self.hour_start: datetime = datetime.utcnow()

    def decide(self, predictions: pd.DataFrame) -> Tuple[str, str, float, str]:
        """
        Decide se deve trocar de moeda.

        Returns:
            Tuple[action, coin_key, predicted_profit, reason]
            action: "switch" ou "hold"
        """
        if predictions.empty:
            return "hold", self.current_coin or "", 0.0, "Sem dados de predição"

        # Ordenar por lucro previsto
        predictions = predictions.sort_values("predicted_profit_usd", ascending=False)
        best = predictions.iloc[0]
        best_coin = best["coin_key"]
        best_profit = best["predicted_profit_usd"]

        # Se não há moeda atual, trocar para a melhor
        if self.current_coin is None:
            self.current_coin = best_coin
            self.current_profit = best_profit
            self.last_switch_time = datetime.utcnow()
            return "switch", best_coin, best_profit, "Início — selecionando moeda mais lucrativa"

        # Verificar limites de troca por hora
        now = datetime.utcnow()
        if (now - self.hour_start).total_seconds() > 3600:
            self.switches_this_hour = 0
            self.hour_start = now

        if self.switches_this_hour >= self.config.MAX_SWITCHES_PER_HOUR:
            return "hold", self.current_coin, self.current_profit, \
                f"Limite de {self.config.MAX_SWITCHES_PER_HOUR} trocas/hora atingido"

        # Verificar tempo mínimo de mineração
        elapsed = (now - self.last_switch_time).total_seconds()
        if elapsed < self.config.MIN_MINING_TIME_SEC:
            remaining = self.config.MIN_MINING_TIME_SEC - elapsed
            return "hold", self.current_coin, self.current_profit, \
                f"Tempo mínimo não atingido ({remaining:.0f}s restantes)"

        # Verificar hysteresis
        if best_coin == self.current_coin:
            self.current_profit = best_profit
            return "hold", self.current_coin, best_profit, "Já minerando a moeda mais lucrativa"

        improvement = (best_profit - self.current_profit) / (abs(self.current_profit) + 1e-9)
        if improvement < self.config.HYSTERESIS_THRESHOLD_PCT:
            return "hold", self.current_coin, self.current_profit, \
                f"Melhoria insuficiente ({improvement:.1%} < {self.config.HYSTERESIS_THRESHOLD_PCT:.0%})"

        # Trocar!
        old_coin = self.current_coin
        self.current_coin = best_coin
        self.current_profit = best_profit
        self.last_switch_time = now
        self.switches_this_hour += 1

        return "switch", best_coin, best_profit, \
            f"Troca: {old_coin} → {best_coin} (melhoria de {improvement:.1%})"


# ============================================================================
# EXECUTOR
# ============================================================================

class Executor:
    """Executa comandos de troca no minerador."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger("Executor")

    def execute_switch(self, coin_key: str) -> bool:
        """Envia comando de troca para o minerador."""
        coin_info = MINEABLE_COINS.get(coin_key)
        if not coin_info:
            self.logger.error(f"Moeda desconhecida: {coin_key}")
            return False

        command = {
            "command": "switch_algorithm",
            "timestamp": datetime.utcnow().isoformat(),
            "coin": {
                "key": coin_key,
                "symbol": coin_info["symbol"],
                "algorithm": coin_info["algorithm"],
                "pool_url": coin_info["pool_url"],
            }
        }

        # Método 1: Arquivo JSON (mais simples e confiável)
        try:
            with open(self.config.MINER_CONFIG_FILE, "w") as f:
                json.dump(command, f, indent=2)
            self.logger.info(f"Comando de troca salvo: {coin_info['symbol']} ({coin_info['algorithm']})")
        except Exception as e:
            self.logger.error(f"Erro ao salvar comando: {e}")

        # Método 2: Unix Socket (se disponível)
        try:
            if os.path.exists(self.config.MINER_SOCKET_PATH):
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.settimeout(self.config.MINER_SOCKET_TIMEOUT)
                sock.connect(self.config.MINER_SOCKET_PATH)
                sock.sendall(json.dumps(command).encode() + b"\n")
                response = sock.recv(1024).decode()
                sock.close()
                self.logger.info(f"Resposta do minerador: {response}")
                return True
        except Exception as e:
            self.logger.debug(f"Socket não disponível: {e}")

        return True


# ============================================================================
# ORQUESTRADOR PRINCIPAL
# ============================================================================

class ProfitSwitcher:
    """Orquestrador principal do sistema de profit-switching."""

    def __init__(self, user_config: Optional[Dict] = None):
        self.config = Config()
        self.hardware = user_config or Config.DEFAULT_HARDWARE

        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.config.DATA_DIR / "profit_switcher.log")
            ]
        )
        self.logger = logging.getLogger("ProfitSwitcher")

        # Componentes
        self.collector = DataCollector(self.config)
        self.feature_eng = FeatureEngineer(self.config, self.hardware)
        self.predictor = MLPredictor(self.config)
        self.decision_engine = DecisionEngine(self.config)
        self.executor = Executor(self.config)

        # Estado
        self.historical_data = pd.DataFrame()
        self.last_train_time = datetime.min
        self.running = False

    def initialize(self):
        """Inicializa o sistema."""
        self.logger.info("=" * 60)
        self.logger.info("HyperMine Core — Profit Switcher v1.0")
        self.logger.info("=" * 60)
        self.logger.info(f"Hardware: {self.hardware}")
        self.logger.info(f"Moedas configuradas: {len(MINEABLE_COINS)}")
        self.logger.info(f"Custo energia: ${self.config.DEFAULT_ENERGY_COST_USD_KWH}/kWh")

        # Carregar dados históricos
        if self.config.HISTORICAL_DATA_FILE.exists():
            self.historical_data = pd.read_csv(
                self.config.HISTORICAL_DATA_FILE,
                parse_dates=["timestamp"]
            )
            self.logger.info(f"Dados históricos carregados: {len(self.historical_data)} registros")

        # Carregar modelos
        if self.predictor.load_models():
            self.logger.info("Modelos ML carregados com sucesso")
        else:
            self.logger.info("Sem modelos ML — usando estimativa direta até acumular dados")

    def run_cycle(self) -> Dict:
        """Executa um ciclo completo de coleta → predição → decisão."""
        cycle_result = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "hold",
            "coin": "",
            "profit": 0.0,
            "reason": "",
            "all_predictions": []
        }

        try:
            # 1. Coletar dados
            raw_data = self.collector.collect_all()
            if raw_data.empty:
                cycle_result["reason"] = "Sem dados coletados"
                return cycle_result

            # 2. Criar features
            featured_data = self.feature_eng.create_features(raw_data)

            # 3. Salvar no histórico
            self.historical_data = pd.concat(
                [self.historical_data, featured_data],
                ignore_index=True
            )
            self.historical_data.to_csv(
                self.config.HISTORICAL_DATA_FILE, index=False
            )

            # 4. Re-treinar se necessário
            now = datetime.utcnow()
            if (now - self.last_train_time).total_seconds() > self.config.RETRAIN_INTERVAL_SEC:
                if len(self.historical_data) >= self.config.MIN_DATA_POINTS_FOR_TRAINING:
                    self.logger.info("Re-treinando modelos ML...")
                    metrics = self.predictor.train(self.historical_data)
                    self.last_train_time = now
                    self.logger.info(f"Métricas: {json.dumps(metrics, indent=2)}")

            # 5. Predição
            predictions = self.predictor.predict(featured_data)

            # 6. Decisão
            action, coin, profit, reason = self.decision_engine.decide(predictions)

            # 7. Executar
            if action == "switch":
                self.executor.execute_switch(coin)

            # Resultado
            cycle_result.update({
                "action": action,
                "coin": coin,
                "profit": profit,
                "reason": reason,
                "all_predictions": predictions.to_dict("records")
            })

            # Log
            self.logger.info(
                f"[{action.upper()}] {coin} | "
                f"Lucro previsto: ${profit:.4f}/dia | {reason}"
            )

            # Top 5
            top5 = predictions.nlargest(5, "predicted_profit_usd")
            self.logger.info("Top 5 moedas:")
            for _, row in top5.iterrows():
                self.logger.info(
                    f"  {row['symbol']:>6s}: ${row['predicted_profit_usd']:.4f}/dia"
                )

        except Exception as e:
            self.logger.error(f"Erro no ciclo: {e}", exc_info=True)
            cycle_result["reason"] = f"Erro: {str(e)}"

        return cycle_result

    def run(self):
        """Loop principal de execução contínua."""
        self.initialize()
        self.running = True

        self.logger.info(
            f"Iniciando loop principal "
            f"(intervalo: {self.config.COLLECTION_INTERVAL_SEC}s)"
        )

        while self.running:
            try:
                result = self.run_cycle()

                # Salvar estado
                with open(self.config.STATE_FILE, "w") as f:
                    json.dump(result, f, indent=2, default=str)

                # Aguardar próximo ciclo
                time.sleep(self.config.COLLECTION_INTERVAL_SEC)

            except KeyboardInterrupt:
                self.logger.info("Interrompido pelo usuário")
                self.running = False
            except Exception as e:
                self.logger.error(f"Erro fatal: {e}", exc_info=True)
                time.sleep(60)

    def stop(self):
        """Para o loop principal."""
        self.running = False


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Ponto de entrada principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description="HyperMine Core — Profit Switcher Inteligente"
    )
    parser.add_argument(
        "--config", type=str, default=None,
        help="Caminho para arquivo de configuração JSON do hardware"
    )
    parser.add_argument(
        "--energy-cost", type=float, default=0.16,
        help="Custo de energia em USD/kWh (padrão: 0.16)"
    )
    parser.add_argument(
        "--interval", type=int, default=300,
        help="Intervalo de coleta em segundos (padrão: 300)"
    )
    parser.add_argument(
        "--single", action="store_true",
        help="Executar apenas um ciclo e sair"
    )

    args = parser.parse_args()

    # Configuração de hardware
    hardware = Config.DEFAULT_HARDWARE
    if args.config:
        with open(args.config) as f:
            hardware = json.load(f)

    Config.DEFAULT_ENERGY_COST_USD_KWH = args.energy_cost
    Config.COLLECTION_INTERVAL_SEC = args.interval

    # Criar e executar
    switcher = ProfitSwitcher(hardware)

    if args.single:
        switcher.initialize()
        result = switcher.run_cycle()
        print(json.dumps(result, indent=2, default=str))
    else:
        switcher.run()


if __name__ == "__main__":
    main()
