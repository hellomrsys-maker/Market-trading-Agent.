"""
ai/features/vol_surface_features.py
====================================
OptionAlpha Agent — Implied Volatility Surface & Skew Feature Extractor

Extracts 8 advanced surface and skew metrics:
  1. skew_25d: 25-Delta Put Vol minus 25-Delta Call Vol
  2. term_spread: 30-Day ATM Vol minus 90-Day ATM Vol
  3. rv_iv_spread: Realized Vol minus Implied Vol (VRP indicator)
  4. put_skew_rank: Percentile rank of current put skew
  5. surface_curvature: Second derivative of IV w.r.t strike (butterfly value)
  6. vol_of_vol: Realized volatility of the ATM IV itself
  7. term_backwardation: Binary indicator (1 if front > back month IV)
  8. gamma_profile: Ratio of ATM gamma to 10-delta wing gamma
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional
import numpy as np


class VolatilitySurfaceFeatureExtractor:
    """
    Computes 8 volatility surface and term-structure features from option chains.
    """

    @staticmethod
    def extract_features(
        spot: float,
        chain_contracts: List[Dict],
        rv20: float = 0.20,
    ) -> np.ndarray:
        """
        Takes raw option contracts and extracts an 8-dimensional float32 vector.
        """
        if not chain_contracts:
            return np.zeros(8, dtype=np.float32)

        # 1. 25-Delta Put Vol vs 25-Delta Call Vol (Skew)
        puts_25d = [c for c in chain_contracts if not c.get("is_call", False) and abs(c.get("delta", 0) - (-0.25)) < 0.08]
        calls_25d = [c for c in chain_contracts if c.get("is_call", False) and abs(c.get("delta", 0) - 0.25) < 0.08]

        p_vol = puts_25d[0].get("implied_volatility", 0.22) if puts_25d else 0.22
        c_vol = calls_25d[0].get("implied_volatility", 0.18) if calls_25d else 0.18
        skew_25d = p_vol - c_vol

        # 2. Term Structure (30d vs 45d/90d)
        dtes = sorted(list({c.get("dte", 30) for c in chain_contracts}))
        near_dte = dtes[0] if dtes else 30
        far_dte = dtes[-1] if len(dtes) > 1 else near_dte

        near_atm = [c for c in chain_contracts if c.get("dte") == near_dte and abs(c.get("strike", spot) - spot) / spot < 0.03]
        far_atm = [c for c in chain_contracts if c.get("dte") == far_dte and abs(c.get("strike", spot) - spot) / spot < 0.03]

        near_iv = near_atm[0].get("implied_volatility", 0.20) if near_atm else 0.20
        far_iv = far_atm[0].get("implied_volatility", 0.20) if far_atm else 0.20
        term_spread = near_iv - far_iv

        # 3. RV - IV Spread (Volatility Risk Premium)
        rv_iv_spread = rv20 - near_iv

        # 4. Put Skew Rank (approx proxy)
        put_skew_rank = min(100.0, max(0.0, (skew_25d / 0.10) * 50.0 + 25.0))

        # 5. Surface Curvature (Convexity)
        surface_curvature = max(0.0, (p_vol + c_vol) / 2.0 - near_iv)

        # 6. Vol of Vol (proxy)
        vol_of_vol = abs(near_iv - far_iv) * 2.0

        # 7. Term Backwardation
        term_backwardation = 1.0 if near_iv > far_iv else 0.0

        # 8. Gamma Profile
        atm_gamma = near_atm[0].get("gamma", 0.03) if near_atm else 0.03
        wing_gamma = puts_25d[0].get("gamma", 0.01) if puts_25d else 0.01
        gamma_profile = atm_gamma / max(0.001, wing_gamma)

        feats = np.array([
            skew_25d,
            term_spread,
            rv_iv_spread,
            put_skew_rank / 100.0,
            surface_curvature,
            vol_of_vol,
            term_backwardation,
            min(5.0, gamma_profile) / 5.0,
        ], dtype=np.float32)

        return np.clip(feats, -5.0, 5.0)
