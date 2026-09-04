"""
config/settings.py
==================
OptionAlpha Agent — Centralized Configuration
Loaded from .env via pydantic-settings. All modules import from here.
No hardcoded credentials anywhere in the codebase.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import List, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parent.parent


class AlpacaSettings(BaseSettings):
    """Alpaca paper trading credentials and endpoints."""

    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    api_key: str = Field("paper_demo_key", alias="ALPACA_API_KEY")
    secret_key: str = Field("paper_demo_secret", alias="ALPACA_SECRET_KEY")
    base_url: str = Field("https://paper-api.alpaca.markets", alias="ALPACA_BASE_URL")
    data_url: str = Field("https://data.alpaca.markets", alias="ALPACA_DATA_URL")
    paper_account_id: str = Field("", alias="ALPACA_PAPER_ACCOUNT_ID")

    @property
    def is_paper(self) -> bool:
        return "paper" in self.base_url


class StrategySettings(BaseSettings):
    """Trading strategy parameters."""

    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    starting_capital: float = Field(100_000.0, alias="STARTING_CAPITAL")
    max_position_size_pct: float = Field(5.0, alias="MAX_POSITION_SIZE_PCT")
    max_open_positions: int = Field(10, alias="MAX_OPEN_POSITIONS")
    daily_loss_limit: float = Field(2_000.0, alias="DAILY_LOSS_LIMIT")
    max_portfolio_delta: float = Field(500.0, alias="MAX_PORTFOLIO_DELTA")
    vix_circuit_breaker: float = Field(35.0, alias="VIX_CIRCUIT_BREAKER")

    # Wheel strategy
    wheel_csp_delta: float = Field(0.30, alias="WHEEL_TARGET_CSP_DELTA")
    wheel_cc_delta: float = Field(0.20, alias="WHEEL_TARGET_CC_DELTA")
    wheel_min_dte: int = Field(21, alias="WHEEL_MIN_DTE")
    wheel_max_dte: int = Field(45, alias="WHEEL_MAX_DTE")
    wheel_min_premium_pct: float = Field(1.0, alias="WHEEL_MIN_PREMIUM_PCT")
    wheel_profit_take_pct: float = Field(50.0, alias="WHEEL_PROFIT_TAKE_PCT")
    wheel_stop_loss_mult: float = Field(2.0, alias="WHEEL_STOP_LOSS_MULT")

    # Iron Condor
    ic_min_iv_rank: float = Field(30.0, alias="IC_MIN_IV_RANK")
    ic_wing_width: int = Field(5, alias="IC_WING_WIDTH")
    ic_short_delta: float = Field(0.15, alias="IC_SHORT_DELTA")
    ic_min_dte: int = Field(21, alias="IC_MIN_DTE")
    ic_max_dte: int = Field(45, alias="IC_MAX_DTE")

    # Universe
    trading_universe_raw: str = Field(
        "SPY,QQQ,AAPL,MSFT,NVDA,AMD,AMZN", alias="TRADING_UNIVERSE"
    )

    @property
    def trading_universe(self) -> List[str]:
        return [s.strip().upper() for s in self.trading_universe_raw.split(",") if s.strip()]


class AISettings(BaseSettings):
    """Self-developed AI / ML configuration — zero external API dependencies."""

    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    model_dir: Path = Field(ROOT_DIR / "data" / "models", alias="AI_MODEL_DIR")
    device: Literal["auto", "cpu", "cuda", "mps"] = Field("auto", alias="AI_DEVICE")
    training_epochs: int = Field(200, alias="AI_TRAINING_EPOCHS")
    rl_timesteps: int = Field(500_000, alias="AI_RL_TIMESTEPS")
    batch_size: int = Field(256, alias="AI_BATCH_SIZE")
    learning_rate: float = Field(3e-4, alias="AI_LEARNING_RATE")

    @field_validator("model_dir", mode="before")
    @classmethod
    def make_absolute(cls, v: str | Path) -> Path:
        p = Path(v)
        if not p.is_absolute():
            p = ROOT_DIR / p
        p.mkdir(parents=True, exist_ok=True)
        return p

    def resolve_device(self) -> str:
        """Auto-detect best available compute device."""
        if self.device != "auto":
            return self.device
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            elif torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            pass
        return "cpu"


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    database_url: str = Field(f"sqlite:///{ROOT_DIR}/data/optionalpha.db", alias="DATABASE_URL")
    redis_url: str = Field("redis://localhost:6379/0", alias="REDIS_URL")


class WebSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    host: str = Field("127.0.0.1", alias="WEB_HOST")
    port: int = Field(8080, alias="WEB_PORT")
    reload: bool = Field(False, alias="WEB_RELOAD")


class ScheduleSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    morning_scan_et: str = Field("09:40", alias="MORNING_SCAN_ET")
    execute_et: str = Field("10:30", alias="EXECUTE_ET")
    afternoon_review_et: str = Field("14:00", alias="AFTERNOON_REVIEW_ET")
    eod_review_et: str = Field("15:45", alias="EOD_REVIEW_ET")


class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field("INFO", alias="LOG_LEVEL")
    log_dir: Path = Field(ROOT_DIR / "data" / "logs", alias="LOG_DIR")

    @field_validator("log_dir", mode="before")
    @classmethod
    def ensure_log_dir(cls, v: str | Path) -> Path:
        p = Path(v)
        if not p.is_absolute():
            p = ROOT_DIR / p
        p.mkdir(parents=True, exist_ok=True)
        return p


# ─────────────────────────────────────────────────────────────
# Singleton accessors — cached for the process lifetime
# ─────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def get_alpaca_settings() -> AlpacaSettings:
    return AlpacaSettings()


@lru_cache(maxsize=1)
def get_strategy_settings() -> StrategySettings:
    return StrategySettings()


@lru_cache(maxsize=1)
def get_ai_settings() -> AISettings:
    return AISettings()


@lru_cache(maxsize=1)
def get_db_settings() -> DatabaseSettings:
    return DatabaseSettings()


@lru_cache(maxsize=1)
def get_web_settings() -> WebSettings:
    return WebSettings()


@lru_cache(maxsize=1)
def get_schedule_settings() -> ScheduleSettings:
    return ScheduleSettings()


@lru_cache(maxsize=1)
def get_logging_settings() -> LoggingSettings:
    return LoggingSettings()
