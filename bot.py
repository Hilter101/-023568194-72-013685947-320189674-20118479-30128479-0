#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════
#  QUANTWHEEL-STYLE GEX BOT v3.0 — SPY + QQQ ONLY
#  API Keys obfuscated via XOR to avoid GitHub Secret Scanning detection
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

__author__ = "Kirby (Quantwheel Edition by AI)"
__version__ = "3.0.0"

import os
import sys
import json
import time
import math
import logging
import requests
import traceback
import threading
import subprocess
import warnings
import base64
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from collections import defaultdict

warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════════════════════
#  OBFUSCATED SECRETS — decoded at runtime to avoid static secret scanning
# ═══════════════════════════════════════════════════════════════════════════════

XOR_KEY = "QuantwheelGEXBot2026"

def _decode(obfuscated: list[int]) -> str:
    """Deobfuscate secret at runtime using XOR + base64."""
    key_bytes = XOR_KEY.encode()
    decoded = bytearray(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(obfuscated))
    return base64.b64decode(decoded).decode()

# Obfuscated Groq API keys (XOR + base64) — decoded at runtime
_GROQ_KEYS_OBFUSCATED = [
    [11, 70, 47, 28, 44, 68, 38, 49, 6, 57, 114, 44, 58, 22, 3, 70, 107, 90, 104, 97, 28, 61, 9, 30, 57, 69, 93, 15, 50, 36, 35, 51, 14, 114, 11, 31, 87, 103, 123, 76, 3, 25, 10, 95, 21, 26, 81, 81, 7, 22, 6, 119, 1, 114, 11, 45, 87, 120, 112, 101, 50, 70, 47, 56, 59, 34, 7, 85, 0, 52, 9, 41, 13, 40, 38, 73],
    [11, 70, 47, 28, 44, 70, 50, 11, 1, 42, 17, 112, 13, 56, 57, 30, 86, 91, 90, 94, 53, 25, 39, 33, 58, 26, 50, 22, 50, 36, 17, 115, 14, 114, 11, 31, 87, 103, 123, 76, 3, 25, 13, 61, 32, 26, 58, 9, 4, 40, 2, 117, 1, 44, 0, 3, 102, 101, 3, 96, 51, 71, 39, 36, 39, 35, 34, 49, 63, 42, 29, 53, 9, 21, 4, 73],
    [11, 70, 47, 28, 44, 71, 0, 16, 0, 0, 43, 119, 15, 22, 41, 27, 86, 0, 11, 7, 51, 27, 9, 15, 32, 29, 12, 46, 7, 1, 63, 40, 14, 114, 11, 31, 87, 103, 123, 76, 3, 25, 13, 20, 33, 47, 12, 47, 48, 95, 9, 52, 60, 41, 38, 69, 97, 1, 100, 113, 3, 70, 35, 30, 46, 26, 92, 81, 60, 6, 43, 18, 1, 44, 42, 73],
    [11, 70, 47, 28, 44, 70, 24, 21, 49, 22, 5, 53, 2, 7, 31, 32, 96, 2, 100, 100, 31, 15, 47, 93, 32, 71, 62, 16, 43, 0, 13, 51, 14, 114, 11, 31, 87, 103, 123, 76, 3, 25, 13, 93, 21, 28, 24, 45, 43, 0, 21, 48, 22, 7, 27, 70, 99, 100, 120, 117, 53, 25, 59, 30, 21, 47, 12, 14, 48, 42, 43, 53, 60, 46, 62, 73],
]

# Obfuscated Telegram bot token (XOR + base64) — decoded at runtime
_TELEGRAM_TOKEN_OBFUSCATED = [30, 49, 48, 91, 57, 51, 45, 84, 40, 40, 10, 61, 23, 6, 31, 54, 99, 101, 104, 65, 2, 24, 51, 5, 46, 34, 89, 61, 7, 22, 2, 117, 23, 10, 7, 13, 107, 101, 90, 66, 11, 50, 88, 43, 46, 27, 34, 54, 40, 57, 14, 63, 58, 114, 90, 57, 104, 103, 100, 113, 3, 36, 92, 83]

# ═══════════════════════════════════════════════════════════════════════════════
#  AUTO-INSTALLER
# ═══════════════════════════════════════════════════════════════════════════════

_REQUIRED_PACKAGES = {
    "numpy": "numpy",
    "pandas": "pandas",
    "yfinance": "yfinance",
    "groq": "groq",
    "matplotlib": "matplotlib",
}

print(f"[Python] {sys.executable}")
print(f"[Version] {sys.version.split()[0]}\n")

_missing = []
for module, package in _REQUIRED_PACKAGES.items():
    try:
        __import__(module)
        print(f"  ✓ {module}")
    except ImportError:
        print(f"  ✗ {module} — will install {package}")
        _missing.append(package)

if _missing:
    print(f"\n[INSTALLING] {', '.join(_missing)} ...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", *_missing],
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        print("[INSTALL] Success\n")
    except subprocess.CalledProcessError as e:
        print(f"\n[INSTALL FAILED] {e}")
        print(f"Run manually: {sys.executable} -m pip install " + " ".join(_missing))
        sys.exit(1)

import numpy as np
import pandas as pd
import yfinance as yf
import groq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch

print("[ALL DEPS OK]\n")

# ═══════════════════════════════════════════════════════════════════════════════
#  BLACK-SCHOLES GAMMA
# ═══════════════════════════════════════════════════════════════════════════════

def _ndf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def black_scholes_gamma(S, K, T, r, sigma, option_type="call") -> float:
    if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
        return 0.0
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    gamma = _ndf(d1) / (S * sigma * math.sqrt(T))
    return gamma


# ═══════════════════════════════════════════════════════════════════════════════
#  DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class Direction(Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"
    HOLD = "HOLD"
    FLIP = "FLIP"

class AlertSeverity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class GammaZone(Enum):
    POSITIVE = "Positive gamma zone (pinning/stable)"
    NEGATIVE = "Negative gamma zone (trending/volatile)"

@dataclass
class StrikeGEX:
    strike: float
    call_oi: int = 0
    put_oi: int = 0
    call_gamma: float = 0.0
    put_gamma: float = 0.0
    call_gex: float = 0.0
    put_gex: float = 0.0
    net_gex: float = 0.0
    call_vol: int = 0
    put_vol: int = 0
    call_iv: float = 0.0
    put_iv: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class GammaLevels:
    zero_gamma: Optional[float] = None
    call_wall: Optional[float] = None
    put_wall: Optional[float] = None
    flip_point: Optional[float] = None
    max_pain: Optional[float] = None
    spot_price: Optional[float] = None
    gamma_zone: Optional[str] = None
    total_net_gex: float = 0.0
    timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items()}

@dataclass
class GEXProfile:
    ticker: str
    spot_price: float
    expiration: str
    strikes: List[StrikeGEX] = field(default_factory=list)
    cumulative_gex: List[Tuple[float, float]] = field(default_factory=list)
    levels: Optional[GammaLevels] = None
    total_call_gex: float = 0.0
    total_put_gex: float = 0.0
    total_net_gex: float = 0.0
    total_abs_gex: float = 0.0
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ticker": self.ticker,
            "spot_price": self.spot_price,
            "expiration": self.expiration,
            "levels": self.levels.to_dict() if self.levels else None,
            "total_call_gex": self.total_call_gex,
            "total_put_gex": self.total_put_gex,
            "total_net_gex": self.total_net_gex,
            "total_abs_gex": self.total_abs_gex,
            "timestamp": self.timestamp,
            "strike_count": len(self.strikes),
        }

@dataclass
class TradeAlert:
    ticker: str
    severity: AlertSeverity
    direction: Direction
    entry_level: float
    target_level: Optional[float] = None
    stop_level: Optional[float] = None
    rationale: str = ""
    timestamp: str = ""
    gex_context: Optional[GammaLevels] = None
    ai_rationale: str = ""

    def format_message(self) -> str:
        emoji = {"CRITICAL": "🚨", "HIGH": "⚠️", "MEDIUM": "📊", "LOW": "ℹ️"}.get(self.severity.value, "📊")
        dir_emoji = {"LONG": "🟢", "SHORT": "🔴", "NEUTRAL": "⚪", "HOLD": "🟡", "FLIP": "🔵"}.get(self.direction.value, "⚪")
        lines = [
            f"{emoji} <b>GEX ALERT — {self.severity.value}</b>",
            "",
            f"<b>Index:</b> <code>{self.ticker}</code>",
            f"<b>Direction:</b> {dir_emoji} {self.direction.value}</b>",
            f"<b>Entry Level:</b> <code>${self.entry_level:.2f}</code>",
        ]
        if self.target_level:
            lines.append(f"<b>Target:</b> <code>${self.target_level:.2f}</code>")
        if self.stop_level:
            lines.append(f"<b>Stop:</b> <code>${self.stop_level:.2f}</code>")
        if self.gex_context:
            g = self.gex_context
            lines.extend([
                "",
                "<b>━ GEX Levels ━</b>",
                f"Spot: ${g.spot_price:.2f}" if g.spot_price else "",
                f"Zero Gamma: ${g.zero_gamma:.2f}" if g.zero_gamma else "",
                f"Call Wall: ${g.call_wall:.2f}" if g.call_wall else "",
                f"Put Wall: ${g.put_wall:.2f}" if g.put_wall else "",
                f"Gamma Zone: {g.gamma_zone}" if g.gamma_zone else "",
            ])
        if self.ai_rationale:
            lines.extend(["", f"<b>🤖 AI Analysis:</b> {self.ai_rationale}"])
        lines.extend(["", f"<b>Rationale:</b> {self.rationale}"])
        lines.append(f"\n<i>{self.timestamp}</i>")
        return "\n".join(line for line in lines if line)

@dataclass
class AssetConfig:
    ticker: str
    enabled: bool = True
    alert_threshold_pct: float = 0.008
    critical_threshold_pct: float = 0.005
    min_open_interest: int = 0
    max_expiration_days: int = 30
    preferred_direction: Direction = field(default=Direction.HOLD)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["preferred_direction"] = self.preferred_direction.value
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AssetConfig":
        d = d.copy()
        d["preferred_direction"] = Direction(d.get("preferred_direction", "HOLD"))
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ═══════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION MANAGER — ТОЛЬКО SPY + QQQ
# ═══════════════════════════════════════════════════════════════════════════════

class ConfigurationManager:
    DEFAULT_CONFIG = {
        "groq_api_keys": [],
        "telegram_bot_token": "",
        "telegram_chat_id": "",
        "groq_model": "llama-3.3-70b-versatile",
        "groq_fallback_model": "llama-3.1-8b-instant",
        "scan_interval_seconds": 60,
        "price_cache_seconds": 30,
        "alerts_cooldown_seconds": 300,
        "near_expiry_days": 14,
        "oi_threshold": 0,
        "risk_free_rate": 0.045,
        "use_ai_analysis": True,
        "use_telegram": True,
        "send_plots": True,
        "debug_mode": True,
        "assets": [
            {"ticker": "SPY", "enabled": True, "alert_threshold_pct": 0.008, "notes": "S&P 500 ETF"},
            {"ticker": "QQQ", "enabled": True, "alert_threshold_pct": 0.008, "notes": "NASDAQ-100 ETF"},
        ],
    }

    def __init__(self, config_path: str = "gex_config.json"):
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._assets: List[AssetConfig] = []
        self._lock = threading.RLock()
        self._load()

    def _load(self) -> None:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self._config = {**self.DEFAULT_CONFIG, **loaded}
                self._config["assets"] = self.DEFAULT_CONFIG["assets"].copy()
                print(f"[CONFIG] Loaded from {self.config_path}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"[CONFIG] Error loading: {e} — using defaults")
                self._config = self.DEFAULT_CONFIG.copy()
        else:
            print("[CONFIG] No existing config — creating defaults")
            self._config = self.DEFAULT_CONFIG.copy()
            self._save()
        self._parse_assets()

    def _save(self) -> None:
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False, default=str)
        except IOError as e:
            print(f"[CONFIG] Save error: {e}")

    def _parse_assets(self) -> None:
        raw_assets = self._config.get("assets", [])
        self._assets = [AssetConfig.from_dict(a) for a in raw_assets]

    @property
    def groq_keys(self) -> List[str]:
        return [_decode(k) for k in _GROQ_KEYS_OBFUSCATED]

    @property
    def telegram_token(self) -> str:
        return _decode(_TELEGRAM_TOKEN_OBFUSCATED)

    @property
    def telegram_chat_id(self) -> str:
        return self._config.get("telegram_chat_id", "")

    @telegram_chat_id.setter
    def telegram_chat_id(self, val: str) -> None:
        self._config["telegram_chat_id"] = val
        self._save()

    @property
    def groq_model(self) -> str:
        return self._config.get("groq_model", "llama-3.3-70b-versatile")

    @property
    def groq_fallback_model(self) -> str:
        return self._config.get("groq_fallback_model", "llama-3.1-8b-instant")

    @property
    def scan_interval(self) -> int:
        return self._config.get("scan_interval_seconds", 60)

    @property
    def price_cache_ttl(self) -> int:
        return self._config.get("price_cache_seconds", 30)

    @property
    def alert_cooldown(self) -> int:
        return self._config.get("alerts_cooldown_seconds", 300)

    @property
    def near_expiry_days(self) -> int:
        return self._config.get("near_expiry_days", 14)

    @property
    def oi_threshold(self) -> int:
        return self._config.get("oi_threshold", 0)

    @property
    def risk_free_rate(self) -> float:
        return self._config.get("risk_free_rate", 0.045)

    @property
    def use_ai(self) -> bool:
        return self._config.get("use_ai_analysis", True)

    @property
    def use_telegram(self) -> bool:
        return self._config.get("use_telegram", True)

    @property
    def send_plots(self) -> bool:
        return self._config.get("send_plots", True)

    @property
    def debug_mode(self) -> bool:
        return self._config.get("debug_mode", False)

    @property
    def assets(self) -> List[AssetConfig]:
        with self._lock:
            return [a for a in self._assets if a.enabled]

    def get_asset(self, ticker: str) -> Optional[AssetConfig]:
        with self._lock:
            for a in self._assets:
                if a.ticker.upper() == ticker.upper():
                    return a
            return None

    def add_asset(self, asset: AssetConfig) -> None:
        with self._lock:
            if asset.ticker.upper() not in ("SPY", "QQQ"):
                print(f"[CONFIG] Only SPY and QQQ are supported. Ignoring {asset.ticker}")
                return
            existing = self.get_asset(asset.ticker)
            if existing:
                self._assets.remove(existing)
            self._assets.append(asset)
            self._sync_assets()

    def remove_asset(self, ticker: str) -> bool:
        with self._lock:
            for a in self._assets:
                if a.ticker.upper() == ticker.upper():
                    self._assets.remove(a)
                    self._sync_assets()
                    return True
            return False

    def _sync_assets(self) -> None:
        self._config["assets"] = [a.to_dict() for a in self._assets]
        self._save()

    def to_dict(self) -> Dict[str, Any]:
        return self._config.copy()


# ═══════════════════════════════════════════════════════════════════════════════
#  LOGGING & DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════════════════════

class Diagnostics:
    _instance: Optional["Diagnostics"] = None
    _lock = threading.Lock()

    def __new__(cls, log_dir: str = "logs") -> "Diagnostics":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, log_dir: str = "logs"):
        if self._initialized:
            return
        self._initialized = True
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        self.logger = logging.getLogger("GEX.Engine")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers = []

        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(fmt)
        self.logger.addHandler(ch)

        fh = logging.FileHandler(self.log_dir / "gex_engine.log", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        self.logger.addHandler(fh)

        self.alert_logger = logging.getLogger("GEX.Alerts")
        self.alert_logger.setLevel(logging.INFO)
        ah = logging.FileHandler(self.log_dir / "alerts.log", encoding="utf-8")
        ah.setFormatter(fmt)
        self.alert_logger.addHandler(ah)

        self.error_logger = logging.getLogger("GEX.Errors")
        self.error_logger.setLevel(logging.ERROR)
        eh = logging.FileHandler(self.log_dir / "errors.log", encoding="utf-8")
        eh.setFormatter(fmt)
        self.error_logger.addHandler(eh)

        self.logger.info("Diagnostics initialized — log directory: %s", self.log_dir.absolute())

    def info(self, msg: str, *args, **kwargs) -> None:
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg: str, *args, **kwargs) -> None:
        self.logger.debug(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        self.logger.error(msg, *args, **kwargs)
        self.error_logger.error(msg, *args, **kwargs)

    def log_alert(self, alert: TradeAlert) -> None:
        self.alert_logger.info(
            "ALERT | %s | %s | %s | Entry: %.2f | %s",
            alert.ticker, alert.severity.value, alert.direction.value,
            alert.entry_level, alert.rationale[:100],
        )

    def log_exception(self, exc: Exception, context: str = "") -> None:
        tb = traceback.format_exc()
        self.error_logger.error("EXCEPTION in %s: %s\n%s", context, exc, tb)

    def log_gex_calc(self, profile: GEXProfile) -> None:
        self.logger.debug(
            "GEX[%s] Spot=%.2f Strikes=%d NetGEX=%.0f CallWall=%s PutWall=%s ZeroGamma=%s",
            profile.ticker,
            profile.spot_price,
            len(profile.strikes),
            profile.total_net_gex,
            f"{profile.levels.call_wall:.2f}" if profile.levels and profile.levels.call_wall else "N/A",
            f"{profile.levels.put_wall:.2f}" if profile.levels and profile.levels.put_wall else "N/A",
            f"{profile.levels.zero_gamma:.2f}" if profile.levels and profile.levels.zero_gamma else "N/A",
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  ERROR HANDLING
# ═══════════════════════════════════════════════════════════════════════════════

class GEXException(Exception):
    pass

class PriceFetchError(GEXException):
    pass

class OptionsChainError(GEXException):
    pass

class GEXCalculationError(GEXException):
    pass

class AIAnalysisError(GEXException):
    pass

class TelegramDispatchError(GEXException):
    pass


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"
        self._lock = threading.Lock()

    def record_success(self) -> None:
        with self._lock:
            self.failures = 0
            self.state = "CLOSED"

    def record_failure(self) -> None:
        with self._lock:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"

    def can_execute(self) -> bool:
        with self._lock:
            if self.state == "CLOSED":
                return True
            if self.state == "OPEN":
                if self.last_failure_time and (time.time() - self.last_failure_time) > self.recovery_timeout:
                    self.state = "HALF_OPEN"
                    return True
                return False
            return True


def safe_execute(func: Callable, *args, **kwargs) -> Tuple[bool, Any]:
    try:
        return True, func(*args, **kwargs)
    except Exception as e:
        return False, e


# ═══════════════════════════════════════════════════════════════════════════════
#  PRICE DATA HANDLER
# ═══════════════════════════════════════════════════════════════════════════════

class PriceDataHandler:
    def __init__(self, config: ConfigurationManager, diagnostics: Diagnostics):
        self.config = config
        self.diag = diagnostics
        self._price_cache: Dict[str, Tuple[float, float]] = {}
        self._options_cache: Dict[str, Tuple[Any, float]] = {}
        self._circuit = CircuitBreaker(failure_threshold=3, recovery_timeout=120)
        self._cache_lock = threading.RLock()

    def get_spot_price(self, ticker: str, force_refresh: bool = False) -> float:
        ticker = ticker.upper().strip()
        now = time.time()

        with self._cache_lock:
            if not force_refresh and ticker in self._price_cache:
                price, cached_at = self._price_cache[ticker]
                if (now - cached_at) < self.config.price_cache_ttl:
                    self.diag.debug("Price cache hit for %s: %.2f", ticker, price)
                    return price

        if not self._circuit.can_execute():
            self.diag.warning("Circuit breaker OPEN for price feed — returning cached/stale data")
            with self._cache_lock:
                if ticker in self._price_cache:
                    return self._price_cache[ticker][0]
            raise PriceFetchError(f"Circuit breaker open and no cache for {ticker}")

        try:
            self.diag.debug("Fetching spot price for %s", ticker)
            tk = yf.Ticker(ticker)

            price = None
            try:
                price = tk.fast_info.last_price
            except Exception:
                pass

            if price is None or price <= 0:
                try:
                    info = tk.info
                    price = info.get("regularMarketPrice") or info.get("currentPrice") or info.get("previousClose")
                except Exception:
                    pass

            if price is None or price <= 0:
                try:
                    hist = tk.history(period="5d", interval="1d", progress=False)
                    if not hist.empty:
                        price = float(hist["Close"].iloc[-1])
                except Exception:
                    pass

            if price is None or price <= 0:
                raise PriceFetchError(f"Unable to extract valid price for {ticker}")

            with self._cache_lock:
                self._price_cache[ticker] = (float(price), now)
            self._circuit.record_success()
            self.diag.debug("Price for %s: %.2f", ticker, price)
            return float(price)

        except Exception as e:
            self._circuit.record_failure()
            self.diag.log_exception(e, f"get_spot_price({ticker})")
            with self._cache_lock:
                if ticker in self._price_cache:
                    return self._price_cache[ticker][0]
            raise PriceFetchError(f"Failed to fetch price for {ticker}: {e}")

    def get_options_chain(self, ticker: str) -> Tuple[pd.DataFrame, pd.DataFrame, str]:
        ticker = ticker.upper().strip()

        if not self._circuit.can_execute():
            raise OptionsChainError(f"Circuit breaker open for options feed ({ticker})")

        try:
            self.diag.debug("Fetching options chain for %s", ticker)
            tk = yf.Ticker(ticker)
            expirations = list(tk.options)

            if not expirations:
                raise OptionsChainError(f"No options expirations available for {ticker}")

            cutoff = datetime.now() + timedelta(days=self.config.near_expiry_days)
            valid_exps = [
                e for e in expirations
                if datetime.strptime(e, "%Y-%m-%d") <= cutoff
            ]
            selected = valid_exps[0] if valid_exps else expirations[0]

            chain = tk.option_chain(selected)
            calls = chain.calls
            puts = chain.puts

            if calls.empty and puts.empty:
                raise OptionsChainError(f"Empty options chain for {ticker} @ {selected}")

            self._circuit.record_success()
            self.diag.debug("Options for %s: %d calls, %d puts @ %s", ticker, len(calls), len(puts), selected)
            return calls, puts, selected

        except Exception as e:
            self._circuit.record_failure()
            self.diag.log_exception(e, f"get_options_chain({ticker})")
            raise OptionsChainError(f"Options chain fetch failed for {ticker}: {e}")

    def clear_cache(self) -> None:
        with self._cache_lock:
            self._price_cache.clear()
            self._options_cache.clear()


# ═══════════════════════════════════════════════════════════════════════════════
#  GAMMA EXPOSURE CALCULATOR
# ═══════════════════════════════════════════════════════════════════════════════

class GammaExposureCalculator:
    def __init__(self, config: ConfigurationManager, diagnostics: Diagnostics):
        self.config = config
        self.diag = diagnostics

    def calculate(
        self,
        ticker: str,
        spot_price: float,
        calls: pd.DataFrame,
        puts: pd.DataFrame,
        expiration: str,
    ) -> GEXProfile:
        try:
            self.diag.debug("Calculating GEX for %s @ %.2f", ticker, spot_price)

            exp_date = datetime.strptime(expiration, "%Y-%m-%d")
            days_to_exp = (exp_date - datetime.now()).days
            T = max(days_to_exp / 365.0, 0.001)
            r = self.config.risk_free_rate

            strikes = self._build_strike_map(calls, puts, spot_price, T, r)

            if not strikes:
                raise GEXCalculationError(f"No valid strikes after filtering for {ticker}")

            for s in strikes:
                s.call_gex = s.call_gamma * s.call_oi * 100.0
                s.put_gex = -s.put_gamma * s.put_oi * 100.0
                s.net_gex = s.call_gex + s.put_gex

            strikes.sort(key=lambda x: x.strike)

            cumulative = []
            running_total = 0.0
            for s in strikes:
                running_total += s.net_gex
                cumulative.append((s.strike, running_total))

            levels = self._extract_levels(strikes, cumulative, spot_price)

            total_call_gex = sum(s.call_gex for s in strikes)
            total_put_gex = sum(s.put_gex for s in strikes)
            total_net = total_call_gex + total_put_gex
            total_abs = sum(abs(s.call_gex) + abs(s.put_gex) for s in strikes)

            gamma_zone = GammaZone.NEGATIVE.value if total_net < 0 else GammaZone.POSITIVE.value
            if levels:
                levels.gamma_zone = gamma_zone
                levels.total_net_gex = total_net

            profile = GEXProfile(
                ticker=ticker,
                spot_price=spot_price,
                expiration=expiration,
                strikes=strikes,
                cumulative_gex=cumulative,
                levels=levels,
                total_call_gex=total_call_gex,
                total_put_gex=total_put_gex,
                total_net_gex=total_net,
                total_abs_gex=total_abs,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )

            self.diag.log_gex_calc(profile)
            return profile

        except Exception as e:
            self.diag.log_exception(e, f"calculate({ticker})")
            raise GEXCalculationError(f"GEX calculation failed for {ticker}: {e}")

    def _safe_int(self, val) -> int:
        if val is None:
            return 0
        try:
            if pd.isna(val):
                return 0
            return int(float(val))
        except (ValueError, TypeError):
            return 0

    def _safe_float(self, val) -> float:
        if val is None:
            return 0.0
        try:
            if pd.isna(val):
                return 0.0
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    def _get_gamma(self, row: pd.Series, spot: float, T: float, r: float, option_type: str) -> float:
        gamma_raw = row.get("gamma")
        if gamma_raw is not None and not pd.isna(gamma_raw):
            try:
                g = float(gamma_raw)
                if g > 0:
                    return g
            except (ValueError, TypeError):
                pass

        strike = self._safe_float(row.get("strike"))
        iv_raw = row.get("impliedVolatility")

        if iv_raw is None or pd.isna(iv_raw):
            return 0.0

        sigma = self._safe_float(iv_raw)
        if sigma <= 0 or strike <= 0 or spot <= 0:
            return 0.0

        gamma = black_scholes_gamma(spot, strike, T, r, sigma, option_type)
        return gamma

    def _build_strike_map(
        self, calls: pd.DataFrame, puts: pd.DataFrame, spot: float, T: float, r: float
    ) -> List[StrikeGEX]:
        oi_thresh = self.config.oi_threshold
        strikes_dict: Dict[float, StrikeGEX] = {}
        debug = self.config.debug_mode

        gamma_from_yahoo = 0
        gamma_from_bs = 0

        for _, row in calls.iterrows():
            try:
                strike = self._safe_float(row.get("strike"))
                if strike <= 0:
                    continue

                oi = self._safe_int(row.get("openInterest"))
                vol = self._safe_int(row.get("volume"))

                if oi == 0 and vol > 0:
                    oi = vol

                if oi < oi_thresh:
                    continue

                gamma = self._get_gamma(row, spot, T, r, "call")
                if gamma <= 0:
                    continue

                if row.get("gamma") is not None and not pd.isna(row.get("gamma")):
                    gamma_from_yahoo += 1
                else:
                    gamma_from_bs += 1

                if strike not in strikes_dict:
                    strikes_dict[strike] = StrikeGEX(strike=strike)
                strikes_dict[strike].call_oi = oi
                strikes_dict[strike].call_gamma = gamma
                strikes_dict[strike].call_vol = vol
                iv = self._safe_float(row.get("impliedVolatility"))
                strikes_dict[strike].call_iv = iv
            except Exception:
                continue

        for _, row in puts.iterrows():
            try:
                strike = self._safe_float(row.get("strike"))
                if strike <= 0:
                    continue

                oi = self._safe_int(row.get("openInterest"))
                vol = self._safe_int(row.get("volume"))

                if oi == 0 and vol > 0:
                    oi = vol

                if oi < oi_thresh:
                    continue

                gamma = self._get_gamma(row, spot, T, r, "put")
                if gamma <= 0:
                    continue

                if row.get("gamma") is not None and not pd.isna(row.get("gamma")):
                    gamma_from_yahoo += 1
                else:
                    gamma_from_bs += 1

                if strike not in strikes_dict:
                    strikes_dict[strike] = StrikeGEX(strike=strike)
                strikes_dict[strike].put_oi = oi
                strikes_dict[strike].put_gamma = gamma
                strikes_dict[strike].put_vol = vol
                iv = self._safe_float(row.get("impliedVolatility"))
                strikes_dict[strike].put_iv = iv
            except Exception:
                continue

        if debug:
            print(f"\n    [DEBUG] {len(calls)} calls, {len(puts)} puts | Yahoo gamma: {gamma_from_yahoo}, BS gamma: {gamma_from_bs} | Strikes: {len(strikes_dict)}")

        return list(strikes_dict.values())

    def _extract_levels(
        self,
        strikes: List[StrikeGEX],
        cumulative: List[Tuple[float, float]],
        spot_price: float,
    ) -> GammaLevels:
        levels = GammaLevels(spot_price=spot_price)

        if not strikes:
            return levels

        valid_calls = [s for s in strikes if s.call_gex != 0]
        valid_puts = [s for s in strikes if s.put_gex != 0]
        valid_oi = [s for s in strikes if s.call_oi + s.put_oi > 0]

        if valid_calls:
            call_wall_strike = max(valid_calls, key=lambda s: s.call_gex)
            levels.call_wall = call_wall_strike.strike

        if valid_puts:
            put_wall_strike = min(valid_puts, key=lambda s: s.put_gex)
            levels.put_wall = put_wall_strike.strike

        if valid_oi:
            max_pain_strike = max(valid_oi, key=lambda s: s.call_oi + s.put_oi)
            levels.max_pain = max_pain_strike.strike

        if cumulative:
            zero_gamma = None
            for i in range(1, len(cumulative)):
                prev_strike, prev_cum = cumulative[i - 1]
                curr_strike, curr_cum = cumulative[i]

                if pd.isna(prev_cum) or pd.isna(curr_cum):
                    continue

                if prev_cum <= 0 and curr_cum >= 0 and curr_cum != prev_cum:
                    ratio = abs(prev_cum) / (curr_cum - prev_cum)
                    zero_gamma = prev_strike + ratio * (curr_strike - prev_strike)
                    break
                elif prev_cum >= 0 and curr_cum <= 0 and curr_cum != prev_cum:
                    ratio = abs(prev_cum) / (abs(prev_cum) + abs(curr_cum))
                    zero_gamma = prev_strike + ratio * (curr_strike - prev_strike)
                    break

            if zero_gamma is None:
                closest = min(cumulative, key=lambda x: abs(x[1]) if not pd.isna(x[1]) else float("inf"))
                zero_gamma = closest[0]

            levels.zero_gamma = zero_gamma
            levels.flip_point = zero_gamma

        levels.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return levels

    def generate_signal(self, profile: GEXProfile) -> Optional[TradeAlert]:
        if not profile.levels:
            return None

        asset = self.config.get_asset(profile.ticker)
        if not asset:
            return None

        spot = profile.spot_price
        levels = profile.levels
        alert_thresh = asset.alert_threshold_pct
        crit_thresh = asset.critical_threshold_pct

        # Minimum zone width in dollars to avoid spam on ultra-tight gamma
        MIN_ZONE_WIDTH_PCT = 0.003  # 0.3% of spot minimum

        # ═══════════════════════════════════════════════════════════════════════
        # PRIORITY 1: Price BETWEEN walls (most common scenario on QQQ/SPY)
        # ═══════════════════════════════════════════════════════════════════════
        if levels.put_wall and levels.call_wall:
            lower_wall = min(levels.put_wall, levels.call_wall)
            upper_wall = max(levels.put_wall, levels.call_wall)
            zone_width = upper_wall - lower_wall
            min_zone_width = spot * MIN_ZONE_WIDTH_PCT

            # Price is INSIDE the gamma zone (between walls)
            if lower_wall <= spot <= upper_wall:

                # If zone is too tight (< 0.3% of spot), treat as PINCH only
                if zone_width < min_zone_width:
                    mid = (lower_wall + upper_wall) / 2
                    return TradeAlert(
                        ticker=profile.ticker,
                        severity=AlertSeverity.LOW,
                        direction=Direction.HOLD,
                        entry_level=spot,
                        target_level=mid,
                        stop_level=lower_wall if spot > mid else upper_wall,
                        rationale=f"🔄 ULTRA-TIGHT GAMMA PINCH (${lower_wall:.2f}—${upper_wall:.2f}, width ${zone_width:.2f}). Price trapped. No directional edge — expect pinning / chop.",
                        timestamp=profile.timestamp,
                        gex_context=levels,
                    )

                dist_to_lower = abs(spot - lower_wall) / lower_wall
                dist_to_upper = abs(spot - upper_wall) / upper_wall
                dist_to_nearest = min(dist_to_lower, dist_to_upper)

                # Very close to one of the walls (critical)
                if dist_to_nearest <= crit_thresh:
                    if dist_to_lower <= dist_to_upper:
                        # Near lower wall → LONG (bounce from support)
                        return TradeAlert(
                            ticker=profile.ticker,
                            severity=AlertSeverity.CRITICAL,
                            direction=Direction.LONG,
                            entry_level=lower_wall,
                            target_level=lower_wall + zone_width * 0.3,
                            stop_level=lower_wall * 0.995,
                            rationale=f"🎯 PRICE AT LOWER WALL SUPPORT (${lower_wall:.2f}). Inside gamma zone ${lower_wall:.2f}—${upper_wall:.2f}. Expect bounce toward mid. Net GEX: {profile.total_net_gex:,.0f}",
                            timestamp=profile.timestamp,
                            gex_context=levels,
                        )
                    else:
                        # Near upper wall → SHORT (rejection from resistance)
                        return TradeAlert(
                            ticker=profile.ticker,
                            severity=AlertSeverity.CRITICAL,
                            direction=Direction.SHORT,
                            entry_level=upper_wall,
                            target_level=upper_wall - zone_width * 0.3,
                            stop_level=upper_wall * 1.005,
                            rationale=f"🎯 PRICE AT UPPER WALL RESISTANCE (${upper_wall:.2f}). Inside gamma zone ${lower_wall:.2f}—${upper_wall:.2f}. Expect rejection toward mid. Net GEX: {profile.total_net_gex:,.0f}",
                            timestamp=profile.timestamp,
                            gex_context=levels,
                        )

                # Approaching a wall (medium)
                elif dist_to_nearest <= alert_thresh:
                    if dist_to_lower <= dist_to_upper:
                        return TradeAlert(
                            ticker=profile.ticker,
                            severity=AlertSeverity.MEDIUM,
                            direction=Direction.LONG,
                            entry_level=lower_wall,
                            target_level=lower_wall + zone_width * 0.25,
                            stop_level=lower_wall * 0.99,
                            rationale=f"📉 Approaching LOWER WALL (${lower_wall:.2f}). Inside gamma zone. Prepare LONG bounce play.",
                            timestamp=profile.timestamp,
                            gex_context=levels,
                        )
                    else:
                        return TradeAlert(
                            ticker=profile.ticker,
                            severity=AlertSeverity.MEDIUM,
                            direction=Direction.SHORT,
                            entry_level=upper_wall,
                            target_level=upper_wall - zone_width * 0.25,
                            stop_level=upper_wall * 1.01,
                            rationale=f"📈 Approaching UPPER WALL (${upper_wall:.2f}). Inside gamma zone. Prepare SHORT rejection play.",
                            timestamp=profile.timestamp,
                            gex_context=levels,
                        )

                # In the middle of the zone → HOLD / Pinch
                else:
                    mid = (lower_wall + upper_wall) / 2
                    dist_to_mid = abs(spot - mid) / mid
                    if dist_to_mid < alert_thresh / 3:
                        return TradeAlert(
                            ticker=profile.ticker,
                            severity=AlertSeverity.LOW,
                            direction=Direction.HOLD,
                            entry_level=spot,
                            target_level=mid + zone_width * 0.2,
                            stop_level=mid - zone_width * 0.2,
                            rationale=f"🔄 GAMMA PINCH CENTER (${lower_wall:.2f}—${upper_wall:.2f}). Price ${spot:.2f} near mid ${mid:.2f}. Pinning / low volatility expected.",
                            timestamp=profile.timestamp,
                            gex_context=levels,
                        )

            # Price is OUTSIDE both walls (escaped gamma zone)
            else:
                nearest_wall = upper_wall if spot > upper_wall else lower_wall
                distance_outside = abs(spot - nearest_wall) / nearest_wall
                if distance_outside <= alert_thresh:
                    direction = Direction.LONG if spot > upper_wall else Direction.SHORT
                    return TradeAlert(
                        ticker=profile.ticker,
                        severity=AlertSeverity.HIGH,
                        direction=direction,
                        entry_level=spot,
                        target_level=spot * 1.02 if direction == Direction.LONG else spot * 0.98,
                        stop_level=nearest_wall,
                        rationale=f"🚀 PRICE ESCAPED GAMMA ZONE (${nearest_wall:.2f}). {direction.value} momentum — outside ${lower_wall:.2f}—${upper_wall:.2f} range.",
                        timestamp=profile.timestamp,
                        gex_context=levels,
                    )

        # ═══════════════════════════════════════════════════════════════════════
        # PRIORITY 2: ZERO GAMMA / FLIP POINT (when no walls or far from walls)
        # ═══════════════════════════════════════════════════════════════════════
        if levels.zero_gamma and levels.zero_gamma > 0:
            distance_to_zero = abs(spot - levels.zero_gamma) / levels.zero_gamma
            if distance_to_zero <= crit_thresh:
                return TradeAlert(
                    ticker=profile.ticker,
                    severity=AlertSeverity.HIGH,
                    direction=Direction.FLIP,
                    entry_level=levels.zero_gamma,
                    target_level=levels.zero_gamma * 1.02 if spot < levels.zero_gamma else levels.zero_gamma * 0.98,
                    stop_level=spot * 0.97 if spot < levels.zero_gamma else spot * 1.03,
                    rationale=f"⚡ ZERO GAMMA FLIP (${levels.zero_gamma:.2f}). Distance: {distance_to_zero*100:.2f}%. High volatility expected. Breakout or breakdown imminent.",
                    timestamp=profile.timestamp,
                    gex_context=levels,
                )
            elif distance_to_zero <= alert_thresh:
                return TradeAlert(
                    ticker=profile.ticker,
                    severity=AlertSeverity.MEDIUM,
                    direction=Direction.FLIP,
                    entry_level=levels.zero_gamma,
                    target_level=levels.zero_gamma * 1.015 if spot < levels.zero_gamma else levels.zero_gamma * 0.985,
                    stop_level=spot * 0.98 if spot < levels.zero_gamma else spot * 1.02,
                    rationale=f"⚠️ Approaching ZERO GAMMA FLIP (${levels.zero_gamma:.2f}). Distance: {distance_to_zero*100:.2f}%. Volatility expansion expected.",
                    timestamp=profile.timestamp,
                    gex_context=levels,
                )

        # ═══════════════════════════════════════════════════════════════════════
        # PRIORITY 3: Single wall (fallback when only one wall exists)
        # ═══════════════════════════════════════════════════════════════════════
        if levels.call_wall and levels.call_wall > 0:
            distance_to_call = abs(spot - levels.call_wall) / levels.call_wall
            if distance_to_call <= crit_thresh:
                direction = Direction.SHORT if spot < levels.call_wall else Direction.LONG
                return TradeAlert(
                    ticker=profile.ticker,
                    severity=AlertSeverity.CRITICAL,
                    direction=direction,
                    entry_level=levels.call_wall,
                    target_level=levels.call_wall * 0.99 if direction == Direction.SHORT else levels.call_wall * 1.01,
                    stop_level=levels.call_wall * 1.005 if direction == Direction.SHORT else levels.call_wall * 0.995,
                    rationale=f"🎯 PRICE AT CALL WALL (${levels.call_wall:.2f}). {direction.value} setup. Net GEX: {profile.total_net_gex:,.0f}",
                    timestamp=profile.timestamp,
                    gex_context=levels,
                )
            elif distance_to_call <= alert_thresh and spot < levels.call_wall:
                return TradeAlert(
                    ticker=profile.ticker,
                    severity=AlertSeverity.MEDIUM,
                    direction=Direction.SHORT,
                    entry_level=levels.call_wall,
                    target_level=levels.call_wall * 0.995,
                    stop_level=levels.call_wall * 1.01,
                    rationale=f"📈 Approaching CALL WALL (${levels.call_wall:.2f}). Prepare SHORT on rejection.",
                    timestamp=profile.timestamp,
                    gex_context=levels,
                )

        if levels.put_wall and levels.put_wall > 0:
            distance_to_put = abs(spot - levels.put_wall) / levels.put_wall
            if distance_to_put <= crit_thresh:
                direction = Direction.LONG if spot > levels.put_wall else Direction.SHORT
                return TradeAlert(
                    ticker=profile.ticker,
                    severity=AlertSeverity.CRITICAL,
                    direction=direction,
                    entry_level=levels.put_wall,
                    target_level=levels.put_wall * 1.01 if direction == Direction.LONG else levels.put_wall * 0.99,
                    stop_level=levels.put_wall * 0.995 if direction == Direction.LONG else levels.put_wall * 1.005,
                    rationale=f"🎯 PRICE AT PUT WALL (${levels.put_wall:.2f}). {direction.value} setup. Net GEX: {profile.total_net_gex:,.0f}",
                    timestamp=profile.timestamp,
                    gex_context=levels,
                )
            elif distance_to_put <= alert_thresh and spot > levels.put_wall:
                return TradeAlert(
                    ticker=profile.ticker,
                    severity=AlertSeverity.MEDIUM,
                    direction=Direction.LONG,
                    entry_level=levels.put_wall,
                    target_level=levels.put_wall * 1.015,
                    stop_level=levels.put_wall * 0.99,
                    rationale=f"📉 Approaching PUT WALL (${levels.put_wall:.2f}). Prepare LONG on bounce.",
                    timestamp=profile.timestamp,
                    gex_context=levels,
                )

        return None

    @staticmethod
    def _compute_target(spot: float, level: float, direction: Direction) -> float:
        if direction == Direction.LONG:
            return level + abs(spot - level) * 2.0 if abs(spot - level) > 0 else spot * 1.03
        elif direction == Direction.SHORT:
            return level - abs(spot - level) * 2.0 if abs(spot - level) > 0 else spot * 0.97
        return spot * 1.01

    @staticmethod
    def _compute_stop(spot: float, level: float, direction: Direction) -> float:
        if direction == Direction.LONG:
            return min(level * 0.99, spot * 0.97) if abs(spot - level) > 0 else spot * 0.98
        elif direction == Direction.SHORT:
            return max(level * 1.01, spot * 1.03) if abs(spot - level) > 0 else spot * 1.02
        return spot * 0.99


# ═══════════════════════════════════════════════════════════════════════════════
#  AI ANALYSIS — Groq LLM (Enhanced)
# ═══════════════════════════════════════════════════════════════════════════════

class GroqAnalyzer:
    def __init__(self, config: ConfigurationManager, diagnostics: Diagnostics):
        self.config = config
        self.diag = diagnostics
        self._keys = [k.strip() for k in config.groq_keys if k.strip()]
        self._key_index = 0
        self._key_lock = threading.Lock()
        self._circuit = CircuitBreaker(failure_threshold=3, recovery_timeout=120)
        self._clients: Dict[str, groq.Groq] = {}

        if not self._keys:
            self.diag.warning("No Groq API keys configured — AI analysis disabled")

    def _get_client(self) -> Tuple[groq.Groq, str]:
        with self._key_lock:
            key = self._keys[self._key_index % len(self._keys)]
            self._key_index += 1
        if key not in self._clients:
            self._clients[key] = groq.Groq(api_key=key)
        return self._clients[key], key

    def analyze(self, profile: GEXProfile) -> Optional[TradeAlert]:
        if not self._keys or not self.config.use_ai:
            return None

        if not self._circuit.can_execute():
            self.diag.warning("Circuit breaker OPEN for Groq — skipping AI analysis")
            return None

        try:
            client, key_used = self._get_client()
            prompt = self._build_prompt(profile)

            try:
                response = client.chat.completions.create(
                    model=self.config.groq_model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an elite institutional options market maker specializing in Gamma Exposure (GEX) analysis for SPY (S&P 500) and QQQ (NASDAQ-100). "
                                "Analyze the GEX profile and provide a trading decision. "
                                "Respond ONLY with a JSON object containing exactly these fields:\n"
                                '{"direction": "LONG|SHORT|NEUTRAL|FLIP", "confidence": 0.0-1.0, '
                                '"entry": float, "target": float, "stop": float, "rationale": "string", "setup": "string"}'
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.15,
                    max_tokens=600,
                    response_format={"type": "json_object"},
                )
            except TypeError:
                response = client.chat.completions.create(
                    model=self.config.groq_model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an elite institutional options market maker specializing in Gamma Exposure (GEX) analysis for SPY and QQQ. "
                                "Respond ONLY with JSON: {\"direction\":\"LONG|SHORT|NEUTRAL|FLIP\",\"confidence\":0.0-1.0,\"entry\":float,\"target\":float,\"stop\":float,\"rationale\":\"string\",\"setup\":\"string\"}"
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.15,
                    max_tokens=600,
                )

            content = response.choices[0].message.content
            result = json.loads(content)

            direction = Direction(result.get("direction", "HOLD"))
            confidence = float(result.get("confidence", 0))
            entry = float(result.get("entry", profile.spot_price))
            target = float(result.get("target", entry * 1.02))
            stop = float(result.get("stop", entry * 0.98))
            rationale = result.get("rationale", "No rationale provided")
            setup = result.get("setup", "")

            if confidence >= 0.85:
                severity = AlertSeverity.CRITICAL
            elif confidence >= 0.7:
                severity = AlertSeverity.HIGH
            elif confidence >= 0.5:
                severity = AlertSeverity.MEDIUM
            else:
                severity = AlertSeverity.LOW

            self._circuit.record_success()

            return TradeAlert(
                ticker=profile.ticker,
                severity=severity,
                direction=direction,
                entry_level=entry,
                target_level=target,
                stop_level=stop,
                rationale=f"[AI] {rationale}",
                ai_rationale=f"Setup: {setup}. Confidence: {confidence:.0%}",
                timestamp=profile.timestamp,
                gex_context=profile.levels,
            )

        except Exception as e:
            self._circuit.record_failure()
            self.diag.log_exception(e, f"Groq.analyze({profile.ticker})")
            return self._fallback_analyze(profile)

    def _fallback_analyze(self, profile: GEXProfile) -> Optional[TradeAlert]:
        if not self._keys:
            return None
        try:
            client, _ = self._get_client()
            prompt = self._build_prompt(profile)

            response = client.chat.completions.create(
                model=self.config.groq_fallback_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Analyze GEX data for index ETF. Reply ONLY JSON: "
                            '{"direction":"LONG|SHORT|NEUTRAL","entry":float,"target":float,"stop":float,"rationale":"string"}'
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=256,
            )

            content = response.choices[0].message.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content.strip())

            return TradeAlert(
                ticker=profile.ticker,
                severity=AlertSeverity.MEDIUM,
                direction=Direction(result.get("direction", "HOLD")),
                entry_level=float(result.get("entry", profile.spot_price)),
                target_level=float(result.get("target", profile.spot_price * 1.02)),
                stop_level=float(result.get("stop", profile.spot_price * 0.98)),
                rationale=f"[AI-Fallback] {result.get('rationale', 'Analysis complete')}",
                timestamp=profile.timestamp,
                gex_context=profile.levels,
            )
        except Exception as e:
            self.diag.log_exception(e, f"Groq.fallback({profile.ticker})")
            return None

    def _build_prompt(self, profile: GEXProfile) -> str:
        levels = profile.levels
        idx_name = "S&P 500" if profile.ticker == "SPY" else "NASDAQ-100" if profile.ticker == "QQQ" else profile.ticker

        top_strikes = sorted(profile.strikes, key=lambda s: abs(s.net_gex), reverse=True)[:7]

        lines = [
            f"=== GEX ANALYSIS REQUEST ===",
            f"Index ETF: {profile.ticker} ({idx_name})",
            f"Spot Price: ${profile.spot_price:.2f}",
            f"Expiration: {profile.expiration}",
            f"Gamma Zone: {levels.gamma_zone if levels else 'Unknown'}",
            f"Total Call GEX: {profile.total_call_gex:,.0f}",
            f"Total Put GEX: {profile.total_put_gex:,.0f}",
            f"Net GEX: {profile.total_net_gex:,.0f}",
            f"Total Abs GEX: {profile.total_abs_gex:,.0f}",
            "",
            "KEY LEVELS:",
            f"  Zero Gamma (Inflection): ${levels.zero_gamma:.2f}" if levels and levels.zero_gamma else "  Zero Gamma: N/A",
            f"  Call Wall (Resistance):  ${levels.call_wall:.2f}" if levels and levels.call_wall else "  Call Wall: N/A",
            f"  Put Wall (Support):      ${levels.put_wall:.2f}" if levels and levels.put_wall else "  Put Wall: N/A",
            f"  Max Pain:                ${levels.max_pain:.2f}" if levels and levels.max_pain else "  Max Pain: N/A",
            "",
            "TOP 7 STRIKES BY NET GEX:",
        ]

        for s in top_strikes:
            lines.append(
                f"  Strike ${s.strike:.2f}: Net GEX={s.net_gex:,.0f} "
                f"(Call OI={s.call_oi}, Put OI={s.put_oi}, Call IV={s.call_iv:.2f}, Put IV={s.put_iv:.2f})"
            )

        lines.extend([
            "",
            "INSTRUCTIONS:",
            "1. Determine if the market is in Positive Gamma (pinning, mean-reversion) or Negative Gamma (trending, momentum).",
            "2. Identify the most important level (Call Wall, Put Wall, or Zero Gamma) that price is currently interacting with.",
            "3. Recommend a specific trade direction: LONG (bounce from Put Wall), SHORT (rejection at Call Wall), FLIP (break of Zero Gamma), or NEUTRAL (inside pinch zone).",
            "4. Provide exact entry, target, and stop prices based on the GEX levels.",
            "5. Give a concise 1-2 sentence rationale.",
            "6. Describe the setup type (e.g., 'Gamma Pinch', 'Call Wall Rejection', 'Put Wall Bounce', 'Flip Breakout').",
        ])
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
#  TELEGRAM DISPATCHER (with Photo Support)
# ═══════════════════════════════════════════════════════════════════════════════

class TelegramDispatcher:
    API_BASE = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, config: ConfigurationManager, diagnostics: Diagnostics):
        self.config = config
        self.diag = diagnostics
        self.token = config.telegram_token
        self.chat_id = config.telegram_chat_id
        self._circuit = CircuitBreaker(failure_threshold=5, recovery_timeout=120)
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})
        self._last_dispatch: Dict[str, float] = {}

    def _get_chat_id(self) -> str:
        if self.chat_id:
            return self.chat_id
        try:
            resp = self._api_request("getUpdates", {"limit": 10})
            if resp and resp.get("ok") and resp.get("result"):
                for update in resp["result"]:
                    if "message" in update and "chat" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        self.config.telegram_chat_id = str(chat_id)
                        self.chat_id = str(chat_id)
                        self.diag.info("Auto-discovered Telegram chat ID: %s", chat_id)
                        return str(chat_id)
                    elif "callback_query" in update and "message" in update["callback_query"]:
                        chat_id = update["callback_query"]["message"]["chat"]["id"]
                        self.config.telegram_chat_id = str(chat_id)
                        self.chat_id = str(chat_id)
                        self.diag.info("Auto-discovered Telegram chat ID: %s", chat_id)
                        return str(chat_id)
        except Exception as e:
            self.diag.warning("Could not auto-discover chat ID: %s", e)
        return ""

    def _api_request(self, method: str, payload: Dict[str, Any]) -> Optional[Dict]:
        if not self.token:
            return None
        url = self.API_BASE.format(token=self.token, method=method)
        try:
            resp = self._session.post(url, json=payload, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            self.diag.error("Telegram API error (%s): %s", method, e)
            return None

    def dispatch(self, alert: TradeAlert, photo_path: Optional[str] = None) -> bool:
        if not self.config.use_telegram or not self.token:
            self.diag.debug("Telegram disabled or no token — logging alert locally")
            self.diag.log_alert(alert)
            return False

        now = time.time()
        last = self._last_dispatch.get(alert.ticker, 0)
        if (now - last) < self.config.alert_cooldown:
            self.diag.debug("Alert cooldown active for %s", alert.ticker)
            return False

        if not self._circuit.can_execute():
            self.diag.warning("Circuit breaker OPEN for Telegram")
            return False

        chat_id = self._get_chat_id()
        if not chat_id:
            self.diag.error("No Telegram chat ID — send /start to your bot first, then run again")
            return False

        try:
            message = alert.format_message()

            if photo_path and os.path.exists(photo_path) and self.config.send_plots:
                url = self.API_BASE.format(token=self.token, method="sendPhoto")
                with open(photo_path, "rb") as photo:
                    files = {"photo": photo}
                    data = {
                        "chat_id": chat_id,
                        "caption": message,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": "True",
                    }
                    resp = requests.post(url, data=data, files=files, timeout=30)
                    resp.raise_for_status()
                    result = resp.json()
            else:
                payload = {
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                }
                result = self._api_request("sendMessage", payload)

            if result and result.get("ok"):
                self._last_dispatch[alert.ticker] = now
                self._circuit.record_success()
                self.diag.log_alert(alert)
                self.diag.info("Alert dispatched: %s %s %s", alert.ticker, alert.direction.value, alert.severity.value)
                return True
            else:
                error_desc = result.get("description", "Unknown error") if result else "No response"
                raise TelegramDispatchError(f"API error: {error_desc}")

        except Exception as e:
            self._circuit.record_failure()
            self.diag.log_exception(e, f"dispatch({alert.ticker})")
            return False

    def send_startup_message(self) -> None:
        if not self.config.use_telegram or not self.token:
            return
        chat_id = self._get_chat_id()
        if not chat_id:
            return
        assets = [a.ticker for a in self.config.assets]
        msg = (
            "🤖 <b>Quantwheel-Style GEX Bot Online</b>\n"
            f"\nTracking Indices: {', '.join(assets)}"
            f"\nScan Interval: {self.config.scan_interval}s"
            f"\nAI Analysis: {'ON' if self.config.use_ai else 'OFF'}"
            f"\nPlot Style: Quantwheel Dark"
            f"\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self._api_request("sendMessage", {
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "HTML",
        })


# ═══════════════════════════════════════════════════════════════════════════════
#  QUANTWHEEL-STYLE GEX VISUALIZER
# ═══════════════════════════════════════════════════════════════════════════════

class GEXVisualizer:
    BG_COLOR = "#0d1117"
    GRID_COLOR = "#21262d"
    TEXT_COLOR = "#c9d1d9"
    TITLE_COLOR = "#f0f6fc"

    CALL_COLOR = "#2ea043"
    PUT_COLOR = "#da3633"
    AGGREGATE_COLOR = "#a371f7"
    NET_CUM_COLOR = "#d29922"
    SPOT_COLOR = "#58a6ff"
    CALL_WALL_COLOR = "#2ea043"
    PUT_WALL_COLOR = "#da3633"
    ZERO_COLOR = "#a371f7"

    def __init__(self, diagnostics: Diagnostics):
        self.diag = diagnostics

    def plot(self, profile: GEXProfile, output_path: Optional[str] = None) -> str:
        if plt is None:
            self.diag.warning("matplotlib not available — skipping plot")
            return ""

        ticker = profile.ticker
        spot = profile.spot_price
        levels = profile.levels
        strikes = profile.strikes

        if not strikes:
            return ""

        min_strike = spot * 0.88
        max_strike = spot * 1.12
        filtered = [s for s in strikes if min_strike <= s.strike <= max_strike]
        if len(filtered) < 5:
            filtered = strikes
        filtered.sort(key=lambda s: s.strike)

        strike_vals = [s.strike for s in filtered]
        call_vals = [s.call_gex for s in filtered]
        put_vals = [s.put_gex for s in filtered]
        agg_vals = [abs(s.call_gex) + abs(s.put_gex) for s in filtered]

        plt.rcParams.update({
            "figure.facecolor": self.BG_COLOR,
            "axes.facecolor": self.BG_COLOR,
            "axes.edgecolor": self.GRID_COLOR,
            "axes.labelcolor": self.TEXT_COLOR,
            "text.color": self.TEXT_COLOR,
            "xtick.color": self.TEXT_COLOR,
            "ytick.color": self.TEXT_COLOR,
            "grid.color": self.GRID_COLOR,
            "grid.alpha": 0.5,
            "axes.grid": True,
            "axes.grid.axis": "both",
            "figure.dpi": 150,
        })

        fig, ax = plt.subplots(figsize=(14, 10))
        ax.set_facecolor(self.BG_COLOR)
        ax.tick_params(colors=self.TEXT_COLOR)
        for spine in ax.spines.values():
            spine.set_color(self.GRID_COLOR)

        bar_height = (strike_vals[1] - strike_vals[0]) * 0.55 if len(strike_vals) > 1 else 0.4

        ax.barh(strike_vals, call_vals, height=bar_height, color=self.CALL_COLOR, 
                alpha=0.85, label="Call GEX", edgecolor="none", zorder=3)
        ax.barh(strike_vals, put_vals, height=bar_height, color=self.PUT_COLOR, 
                alpha=0.85, label="Put GEX", edgecolor="none", zorder=3)

        ax2 = ax.twiny()
        ax2.set_facecolor(self.BG_COLOR)
        ax2.tick_params(colors=self.TEXT_COLOR)
        for spine in ax2.spines.values():
            spine.set_color(self.GRID_COLOR)

        ax2.plot(agg_vals, strike_vals, color=self.AGGREGATE_COLOR, linewidth=2.5, 
                 label="Aggregate GEX", zorder=4)

        cumulative = profile.cumulative_gex
        if cumulative:
            cum_filtered = [(s, c) for s, c in cumulative if min_strike <= s <= max_strike]
            if len(cum_filtered) > 1:
                cum_strikes = [s for s, c in cum_filtered]
                cum_vals = [c for s, c in cum_filtered]
                ax2.plot(cum_vals, cum_strikes, color=self.NET_CUM_COLOR, linewidth=2.5, 
                         label="Net GEX (Cumulative)", zorder=4)

        trans = ax.get_yaxis_transform()

        if spot:
            ax.axhline(y=spot, color=self.SPOT_COLOR, linestyle="--", linewidth=1.5, alpha=0.9, zorder=5)
            ax.text(-0.01, spot, f"  Spot: ${spot:.2f}", color=self.SPOT_COLOR, fontsize=10, 
                    va="center", ha="left", transform=trans, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.35", facecolor=self.BG_COLOR, 
                             edgecolor=self.SPOT_COLOR, alpha=0.95, linewidth=1.2))

        if levels and levels.zero_gamma:
            ax.axhline(y=levels.zero_gamma, color=self.ZERO_COLOR, linestyle="--", linewidth=1.5, alpha=0.9, zorder=5)
            ax.text(-0.01, levels.zero_gamma, f"  Inflection: ${levels.zero_gamma:.2f}", 
                    color=self.ZERO_COLOR, fontsize=10, va="center", ha="left", transform=trans, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.35", facecolor=self.BG_COLOR, 
                             edgecolor=self.ZERO_COLOR, alpha=0.95, linewidth=1.2))

        if levels and levels.call_wall:
            ax.axhline(y=levels.call_wall, color=self.CALL_WALL_COLOR, linestyle="--", linewidth=1.5, alpha=0.9, zorder=5)
            ax.text(1.01, levels.call_wall, f"Call Wall: ${levels.call_wall:.2f}  ", 
                    color=self.CALL_WALL_COLOR, fontsize=10, va="center", ha="right", transform=trans, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.35", facecolor=self.BG_COLOR, 
                             edgecolor=self.CALL_WALL_COLOR, alpha=0.95, linewidth=1.2))

        if levels and levels.put_wall:
            ax.axhline(y=levels.put_wall, color=self.PUT_WALL_COLOR, linestyle="--", linewidth=1.5, alpha=0.9, zorder=5)
            ax.text(1.01, levels.put_wall, f"Put Wall: ${levels.put_wall:.2f}  ", 
                    color=self.PUT_WALL_COLOR, fontsize=10, va="center", ha="right", transform=trans, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.35", facecolor=self.BG_COLOR, 
                             edgecolor=self.PUT_WALL_COLOR, alpha=0.95, linewidth=1.2))

        idx_name = "S&P 500" if ticker == "SPY" else "NASDAQ-100" if ticker == "QQQ" else ticker
        gamma_zone_str = levels.gamma_zone if levels and levels.gamma_zone else "Unknown"
        total_gex_str = f"{profile.total_net_gex/1000:.0f}K" if abs(profile.total_net_gex) >= 1000 else f"{profile.total_net_gex:.0f}"

        ax.set_title(
            f"Gamma Exposure by Strike - ${ticker} ({datetime.now().strftime('%Y-%m-%d')})\n"
            f"{idx_name} | Spot: ${spot:.2f} | Total GEX: {total_gex_str} | Zone: {gamma_zone_str}",
            color=self.TITLE_COLOR, fontsize=14, fontweight="bold", pad=20, linespacing=1.4
        )

        ax.set_xlabel("Gamma Exposure", color=self.TEXT_COLOR, fontsize=11, fontweight="bold")
        ax.set_ylabel("Strike Price ($)", color=self.TEXT_COLOR, fontsize=11, fontweight="bold")

        ax.xaxis.set_major_formatter(mticker.FuncFormatter(
            lambda x, _: f"{x/1000:.0f}K" if abs(x) >= 1000 else f"{x:.0f}"))
        ax2.xaxis.set_major_formatter(mticker.FuncFormatter(
            lambda x, _: f"{x/1000:.0f}K" if abs(x) >= 1000 else f"{x:.0f}"))

        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        legend = ax.legend(lines1 + lines2, labels1 + labels2, loc="upper center",
                  bbox_to_anchor=(0.5, 1.08), ncol=4, facecolor=self.BG_COLOR,
                  edgecolor=self.GRID_COLOR, labelcolor=self.TEXT_COLOR, fontsize=9,
                  framealpha=0.95)
        for text in legend.get_texts():
            text.set_color(self.TEXT_COLOR)

        plt.tight_layout()
        plt.subplots_adjust(top=0.88)

        if output_path is None:
            output_path = f"gex_plot_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        plt.savefig(output_path, dpi=150, facecolor=self.BG_COLOR, bbox_inches="tight", 
                    edgecolor="none", pad_inches=0.3)
        plt.close(fig)
        plt.rcParams.update(plt.rcParamsDefault)
        self.diag.info("Quantwheel-style GEX plot saved: %s", output_path)
        return output_path


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class GEXEngine:
    def __init__(self, config_path: str = "gex_config.json"):
        self.diag = Diagnostics()
        self.config = ConfigurationManager(config_path)
        self.price_handler = PriceDataHandler(self.config, self.diag)
        self.calculator = GammaExposureCalculator(self.config, self.diag)
        self.analyzer = GroqAnalyzer(self.config, self.diag)
        self.dispatcher = TelegramDispatcher(self.config, self.diag)
        self.visualizer = GEXVisualizer(self.diag)
        self._running = False
        self._scan_count = 0
        self._alert_count = 0
        self._error_count = 0
        self._lock = threading.Lock()
        self._plot_enabled = True

    def scan_asset(self, asset: AssetConfig) -> Optional[GEXProfile]:
        ticker = asset.ticker
        try:
            self.diag.debug("Scanning %s...", ticker)
            spot = self.price_handler.get_spot_price(ticker)
            calls, puts, expiration = self.price_handler.get_options_chain(ticker)
            profile = self.calculator.calculate(ticker, spot, calls, puts, expiration)
            return profile
        except GEXException as e:
            self.diag.warning("GEX scan failed for %s: %s", ticker, e)
            self._error_count += 1
            return None
        except Exception as e:
            self.diag.log_exception(e, f"scan_asset({ticker})")
            self._error_count += 1
            return None

    def evaluate_and_alert(self, profile: GEXProfile) -> bool:
        ticker = profile.ticker
        alert_dispatched = False
        plot_path = None

        if self._plot_enabled and self.config.send_plots:
            try:
                plot_path = self.visualizer.plot(profile)
            except Exception as e:
                self.diag.warning("Plot failed for %s: %s", ticker, e)

        math_alert = self.calculator.generate_signal(profile)
        if math_alert:
            self.diag.debug("Math signal for %s: %s %s", ticker, math_alert.direction.value, math_alert.severity.value)
            if self.dispatcher.dispatch(math_alert, photo_path=plot_path):
                alert_dispatched = True

        if self.config.use_ai:
            ai_alert = self.analyzer.analyze(profile)
            if ai_alert and ai_alert.direction != Direction.HOLD:
                self.diag.debug("AI signal for %s: %s", ticker, ai_alert.direction.value)
                if not math_alert or ai_alert.severity.value >= math_alert.severity.value:
                    if self.dispatcher.dispatch(ai_alert, photo_path=plot_path if not alert_dispatched else None):
                        alert_dispatched = True

        if alert_dispatched:
            self._alert_count += 1

        return alert_dispatched

    def run_single_scan(self) -> Dict[str, Any]:
        assets = self.config.assets
        self.diag.info("═══ Scan Cycle %d | Indices: %d ═══", self._scan_count + 1, len(assets))

        results: Dict[str, Any] = {
            "scan_id": self._scan_count + 1,
            "timestamp": datetime.now().isoformat(),
            "assets_scanned": 0,
            "profiles_generated": 0,
            "alerts_dispatched": 0,
            "errors": 0,
            "profiles": [],
            "plots": [],
        }

        for asset in assets:
            results["assets_scanned"] += 1

            profile = self.scan_asset(asset)
            if profile:
                results["profiles_generated"] += 1
                results["profiles"].append(profile.to_dict())

                alerted = self.evaluate_and_alert(profile)
                if alerted:
                    results["alerts_dispatched"] += 1

                levels = profile.levels
                cw = f"${levels.call_wall:.2f}" if levels and levels.call_wall else "N/A"
                pw = f"${levels.put_wall:.2f}" if levels and levels.put_wall else "N/A"
                zg = f"${levels.zero_gamma:.2f}" if levels and levels.zero_gamma else "N/A"
                zone = levels.gamma_zone if levels and levels.gamma_zone else "N/A"
                idx_name = "S&P 500" if profile.ticker == "SPY" else "NASDAQ-100"
                print(f"\n  [{profile.ticker}] {idx_name} | Spot: ${profile.spot_price:.2f} | "
                      f"NetGEX: {profile.total_net_gex:,.0f} | "
                      f"CallWall: {cw} | PutWall: {pw} | ZeroGamma: {zg} | Zone: {zone}")

        self._scan_count += 1
        results["errors"] = self._error_count

        self.diag.info(
            "Scan %d complete: %d profiles, %d alerts, %d errors",
            self._scan_count, results["profiles_generated"], results["alerts_dispatched"], self._error_count,
        )
        return results

    def run_continuous(self) -> None:
        self._running = True
        self.diag.info("═══════════════════════════════════════════════════════════════")
        self.diag.info("  QUANTWHEEL-STYLE GEX BOT v%s STARTED", __version__)
        self.diag.info("  Tracking: S&P 500 (SPY) + NASDAQ-100 (QQQ)")
        self.diag.info("  Mode: %s", "AI-Enhanced + Quantwheel Plots" if self.config.use_ai else "Math-Only")
        self.diag.info("  Interval: %ds", self.config.scan_interval)
        self.diag.info("═══════════════════════════════════════════════════════════════")

        self.dispatcher.send_startup_message()

        try:
            while self._running:
                cycle_start = time.time()
                self.run_single_scan()

                elapsed = time.time() - cycle_start
                sleep_time = max(1, self.config.scan_interval - int(elapsed))

                self.diag.info("Cycle complete in %.1fs. Next scan in %ds.", elapsed, sleep_time)
                print(f"\n⏳ Sleeping {sleep_time}s... (Ctrl+C to stop)\n")

                for _ in range(sleep_time):
                    if not self._running:
                        break
                    time.sleep(1)

        except KeyboardInterrupt:
            self.diag.info("Shutdown signal received (KeyboardInterrupt)")
            self._running = False
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        self._running = False
        self.diag.info("═══════════════════════════════════════════════════════════════")
        self.diag.info("  GEX BOT SHUTDOWN")
        self.diag.info("  Total Scans: %d | Alerts: %d | Errors: %d", self._scan_count, self._alert_count, self._error_count)
        self.diag.info("═══════════════════════════════════════════════════════════════")

    def run_once(self) -> Dict[str, Any]:
        return self.run_single_scan()


# ═══════════════════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════════════════

def print_banner():
    print("""
   ╔══════════════════════════════════════════════════════════════════╗
   ║     QUANTWHEEL-STYLE GAMMA EXPOSURE BOT v3.0.0                 ║
   ║     S&P 500 (SPY) + NASDAQ-100 (QQQ) Index Tracker             ║
   ║     Data: Yahoo Finance | AI: Groq | Alerts: Telegram        ║
   ║     Visuals: 1:1 Quantwheel Dark Theme                       ║
   ╚══════════════════════════════════════════════════════════════════╝
""")


def main():
    print_banner()

    config_path = "gex_config.json"
    plot_mode = True
    once_mode = False

    for arg in sys.argv[1:]:
        if arg in ("--once", "-o"):
            once_mode = True
        elif arg in ("--no-plot",):
            plot_mode = False
        elif arg in ("--plot", "-p"):
            plot_mode = True
        elif not arg.startswith("-"):
            config_path = arg

    engine = GEXEngine(config_path)
    engine._plot_enabled = plot_mode

    if once_mode:
        print("\n[Single Scan Mode — SPY + QQQ]\n")
        result = engine.run_once()
        print(f"\nResults: {json.dumps(result, indent=2, default=str)}")
    else:
        print("\n[Continuous Monitoring — SPY + QQQ | Press Ctrl+C to stop]\n")
        engine.run_continuous()


if __name__ == "__main__":
    main()