"""
tests/test_options_foundations.py
=================================
Unit tests for Core Basics of Options, Contract Multipliers, Premiums, and Greeks.
"""

from __future__ import annotations

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai.research.options_foundations import OptionContractSpecification


class TestOptionFoundations:
    def test_call_option_intrinsic_and_pricing(self):
        call = OptionContractSpecification(
            symbol="SPY250620C00500000",
            underlying="SPY",
            option_type="CALL",
            strike_price=500.0,
            expiration_years=0.25,
            spot_price=510.0,  # In-The-Money Call
            risk_free_rate=0.05,
            implied_volatility=0.20,
            multiplier=100,
        )

        assert call.intrinsic_value == 10.0
        assert call.total_contract_multiplier == 100

        bsm = call.compute_bsm_analytical()
        assert bsm["theoretical_price"] > 10.0
        assert bsm["extrinsic_value"] > 0.0
        assert bsm["delta"] > 0.50  # ITM Call delta > 0.50
        assert bsm["contract_dollar_premium"] == round(bsm["theoretical_price"] * 100, 2)
        assert bsm["contract_notional_value"] == 510.0 * 100

    def test_put_option_intrinsic_and_pricing(self):
        put = OptionContractSpecification(
            symbol="SPY250620P00500000",
            underlying="SPY",
            option_type="PUT",
            strike_price=500.0,
            expiration_years=0.25,
            spot_price=490.0,  # In-The-Money Put
            risk_free_rate=0.05,
            implied_volatility=0.20,
            multiplier=100,
        )

        assert put.intrinsic_value == 10.0
        assert put.total_contract_multiplier == 100

        bsm = put.compute_bsm_analytical()
        assert bsm["theoretical_price"] > 10.0
        assert bsm["delta"] < -0.50  # ITM Put delta < -0.50
        assert bsm["theta_per_day"] < 0.0  # Option decay is negative

    def test_payoff_at_expiration(self):
        call = OptionContractSpecification(
            symbol="SPY250620C00500000",
            underlying="SPY",
            option_type="CALL",
            strike_price=500.0,
            expiration_years=0.10,
            spot_price=500.0,
            risk_free_rate=0.05,
            implied_volatility=0.20,
        )

        # Long Call when underlying rallies to $520
        long_payoff = call.compute_payoff_at_expiration(terminal_spot=520.0, position_side="LONG")
        assert long_payoff > 0.0

        # Short Call when underlying finishes OTM at $480
        short_payoff = call.compute_payoff_at_expiration(terminal_spot=480.0, position_side="SHORT")
        assert short_payoff > 0.0  # Kept 100% of upfront premium
