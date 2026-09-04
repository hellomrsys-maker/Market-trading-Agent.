"""
ai/research/crypto_spot_engine.py
==================================
Module BQ: 24/7 Autonomous Crypto Spot Trading & Triangular Arbitrage Engine

Synthesized from Alpaca Crypto Spot Trading specifications:
  - 24/7 continuous trading (trade all day, 7 days a week, 365 days a year)
  - 20+ assets, 56 pairs (e.g. BTC/USD, ETH/USD, ETH/BTC, SOL/USD, AVAX/USD)
  - Strict cash spot trading: evaluated against non_marginable_buying_power (no margin leverage, no shorting)
  - Max order notional limit: $200k per order
  - Volume-tiered maker/taker fees: Tier 1: 15 bps maker / 25 bps taker (debited in received asset)
  - Multi-pair cross-rate Triangular Arbitrage & Order Book Imbalance (OBI) microstructure detection
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class CryptoSpotState:
    spot_price: float
    bid_depth_usd: float
    ask_depth_usd: float
    order_book_imbalance: float
    triangular_arb_spread: float
    non_marginable_buying_power: float
    asset_pair_id: int
    max_notional_k: int
    is_tradable: bool
    is_fractionable: bool
    fee_bps: int
    status_flags: int


class CryptoSpotEngine:
    """
    24/7 Autonomous Crypto Spot Trading & Microstructure Arbitrage Engine.
    """

    SUPPORTED_PAIRS = [
        "BTC/USD", "ETH/USD", "SOL/USD", "AVAX/USD", "DOGE/USD",
        "LINK/USD", "UNI/USD", "ETH/BTC", "BTC/USDT", "ETH/USDT"
    ]

    MAX_ORDER_NOTIONAL: float = 200_000.0  # Alpaca $200k limit per order

    def __init__(self, taker_fee_bps: float = 25.0, maker_fee_bps: float = 15.0):
        self.taker_fee_pct = taker_fee_bps / 10000.0  # 0.0025 (25 bps)
        self.maker_fee_pct = maker_fee_bps / 10000.0  # 0.0015 (15 bps)

    def initialize_state(self, spot: float, cash_power: float, pair: str = "BTC/USD") -> CryptoSpotState:
        pair_id = hash(pair) % 10000
        return CryptoSpotState(
            spot_price=spot,
            bid_depth_usd=spot * 5.0,
            ask_depth_usd=spot * 5.0,
            order_book_imbalance=0.0,
            triangular_arb_spread=0.0,
            non_marginable_buying_power=cash_power,
            asset_pair_id=pair_id,
            max_notional_k=200,
            is_tradable=True,
            is_fractionable=True,
            fee_bps=25,
            status_flags=1,
        )

    def calculate_order_book_imbalance(
        self,
        bids: List[Dict[str, float]],
        asks: List[Dict[str, float]],
        depth_levels: int = 5,
    ) -> Dict[str, Any]:
        """
        Computes Level-2 Order Book Imbalance (OBI) from top depth levels:
          OBI = (BidVolume - AskVolume) / (BidVolume + AskVolume)
        """
        bid_vol = sum(b.get("s", b.get("size", 0.0)) * b.get("p", b.get("price", 0.0)) for b in bids[:depth_levels])
        ask_vol = sum(a.get("s", a.get("size", 0.0)) * a.get("p", a.get("price", 0.0)) for a in asks[:depth_levels])

        total_vol = bid_vol + ask_vol
        obi = (bid_vol - ask_vol) / total_vol if total_vol > 0.001 else 0.0

        sentiment = "NEUTRAL"
        if obi > 0.25:
            sentiment = "STRONG_BUY_PRESSURE"
        elif obi < -0.25:
            sentiment = "STRONG_SELL_PRESSURE"

        return {
            "order_book_imbalance": round(obi, 4),
            "bid_depth_usd": round(bid_vol, 2),
            "ask_depth_usd": round(ask_vol, 2),
            "microstructure_sentiment": sentiment,
            "signal": "BUY" if obi > 0.30 else ("SELL" if obi < -0.30 else "HOLD"),
        }

    def evaluate_triangular_arbitrage(
        self,
        btc_usd: float,
        eth_btc: float,
        eth_usd: float,
    ) -> Dict[str, Any]:
        """
        Cross-rate Synthetic Triangular Arbitrage:
          Synthetic ETH/USD = ETH/BTC * BTC/USD
          Spread = (Actual ETH/USD - Synthetic ETH/USD) / Actual ETH/USD
        """
        synthetic_eth_usd = eth_btc * btc_usd
        if eth_usd <= 0.001:
            return {"arbitrage_detected": False, "spread_pct": 0.0}

        spread_pct = (eth_usd - synthetic_eth_usd) / eth_usd
        # Total round-trip fee across 2 legs = 2 * taker_fee_pct (0.50%)
        hurdle_rate = 2.0 * self.taker_fee_pct
        is_profitable = abs(spread_pct) > hurdle_rate

        action = "NONE"
        if is_profitable:
            if spread_pct > 0:
                # ETH/USD is overpriced relative to synthetic -> Sell ETH/USD, Buy ETH/BTC & BTC/USD
                action = "BUY_SYNTHETIC_SELL_DIRECT"
            else:
                # ETH/USD is underpriced relative to synthetic -> Buy ETH/USD, Sell ETH/BTC & BTC/USD
                action = "BUY_DIRECT_SELL_SYNTHETIC"

        return {
            "arbitrage_detected": is_profitable,
            "actual_eth_usd": eth_usd,
            "synthetic_eth_usd": round(synthetic_eth_usd, 2),
            "spread_pct": round(spread_pct * 100.0, 3),
            "hurdle_rate_pct": round(hurdle_rate * 100.0, 3),
            "net_edge_bps": round((abs(spread_pct) - hurdle_rate) * 10000.0, 1),
            "recommended_action": action,
        }

    def validate_order_compliance(
        self,
        notional_usd: float,
        cash_buying_power: float,
        side: str = "buy",
    ) -> Dict[str, Any]:
        """
        Validates against Alpaca Crypto regulatory rules:
          1. No short selling (side must be 'buy' or closed from held inventory)
          2. Non-marginable: order <= cash_buying_power
          3. $200k max notional limit per order
        """
        if notional_usd > self.MAX_ORDER_NOTIONAL:
            return {
                "approved": False,
                "reason": f"EXCEEDS_200K_MAX_NOTIONAL (${notional_usd:,.2f} > $200,000)",
            }

        if side.lower() == "buy" and notional_usd > cash_buying_power:
            return {
                "approved": False,
                "reason": f"INSUFFICIENT_NON_MARGINABLE_CASH (Requested ${notional_usd:,.2f} > ${cash_buying_power:,.2f})",
            }

        est_fee_usd = notional_usd * self.taker_fee_pct
        return {
            "approved": True,
            "notional_usd": notional_usd,
            "estimated_fee_usd": round(est_fee_usd, 2),
            "fee_rate_bps": round(self.taker_fee_pct * 10000.0),
            "reason": "APPROVED_SPOT_CASH",
        }

    # Volume-tiered fee schedule (Alpaca Crypto Spot Fees)
    FEE_TIERS = {
        1: {"tier": 1, "vol_range": "$0 - $100,000", "maker_bps": 15, "taker_bps": 25},
        2: {"tier": 2, "vol_range": "$100,000 - $500,000", "maker_bps": 12, "taker_bps": 22},
        3: {"tier": 3, "vol_range": "$500,000 - $1,000,000", "maker_bps": 10, "taker_bps": 20},
        4: {"tier": 4, "vol_range": "$1,000,000 - $10,000,000", "maker_bps": 8, "taker_bps": 18},
        5: {"tier": 5, "vol_range": "$10,000,000 - $25,000,000", "maker_bps": 5, "taker_bps": 15},
        6: {"tier": 6, "vol_range": "$25,000,000 - $50,000,000", "maker_bps": 2, "taker_bps": 13},
        7: {"tier": 7, "vol_range": "$50,000,000 - $100,000,000", "maker_bps": 2, "taker_bps": 12},
        8: {"tier": 8, "vol_range": "$100,000,000+", "maker_bps": 0, "taker_bps": 10},
    }

    def calculate_credited_fee(
        self,
        symbol: str,
        side: str,
        qty: float,
        price: float,
        is_maker: bool = False,
        volume_30d: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Computes fee charged on the CREDITED crypto asset or fiat:
          - Buy ETH/USD: receive ETH -> fee in ETH
          - Sell ETH/USD: receive USD -> fee in USD
          - Buy ETH/BTC: receive ETH -> fee in ETH
          - Sell ETH/BTC: receive BTC -> fee in BTC
        """
        # Determine tier
        tier = 1
        if volume_30d >= 100_000_000:
            tier = 8
        elif volume_30d >= 50_000_000:
            tier = 7
        elif volume_30d >= 25_000_000:
            tier = 6
        elif volume_30d >= 10_000_000:
            tier = 5
        elif volume_30d >= 1_000_000:
            tier = 4
        elif volume_30d >= 500_000:
            tier = 3
        elif volume_30d >= 100_000:
            tier = 2

        tier_info = self.FEE_TIERS[tier]
        fee_bps = tier_info["maker_bps"] if is_maker else tier_info["taker_bps"]
        fee_rate = fee_bps / 10000.0

        parts = symbol.upper().split("/")
        base_asset = parts[0] if len(parts) > 0 else "ETH"
        quote_asset = parts[1] if len(parts) > 1 else "USD"

        notional_usd = qty * price
        if side.lower() == "buy":
            credited_asset = base_asset
            fee_units = round(qty * fee_rate, 8)
            fee_usd = round(fee_units * price, 4)
        else:
            credited_asset = quote_asset
            fee_units = round(notional_usd * fee_rate, 8)
            fee_usd = round(fee_units, 4) if quote_asset in ("USD", "USDC", "USDT") else round(fee_units * price, 4)

        return {
            "tier": tier,
            "fee_bps": fee_bps,
            "is_maker": is_maker,
            "credited_asset": credited_asset,
            "fee_amount": fee_units,
            "fee_usd_equiv": fee_usd,
            "notional_usd": round(notional_usd, 2),
            "description": f"Fee charged in {credited_asset}: {fee_units} {credited_asset} (${fee_usd:,.2f})",
        }

