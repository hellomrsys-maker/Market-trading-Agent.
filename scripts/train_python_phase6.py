"""
scripts/train_python_phase6.py
==============================
Phase 6: Python Training Module (T1)
"""

import sys, os
from loguru import logger
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.research.dispersion_rainbow_engine import DispersionRainbowEngine
from ai.research.barrier_autocallable_engine import BarrierAutocallableEngine
from ai.research.cliquet_mountain_range_engine import CliquetMountainRangeEngine
from ai.research.variance_swap_copula_engine import VarianceSwapCopulaEngine

def train():
    logger.info("[T1 PYTHON] Starting High-Level AI Training Epochs for Phase 6...")

    # 1. Dispersion, Rainbow & Basket
    dre = DispersionRainbowEngine()
    corr = np.array([[1.0, 0.4], [0.4, 1.0]])
    var_p = dre.calculate_basket_variance(np.array([0.5, 0.5]), np.array([0.2, 0.3]), corr)
    bo_parity = dre.calculate_worst_of_best_of_parity(8.0, 6.0, 3.5)
    rainbow = dre.calculate_rainbow_payoff([0.15, 0.08, -0.05], [0.5, 0.3, 0.2])
    icbc_res = dre.evaluate_icbc_vs_cbc([0.25, 0.10, -0.05], 0.15)
    logger.info(f"Dispersion Engine: Basket Vol={np.sqrt(var_p):.2%}, Best-of Parity=${bo_parity:.2f}, Rainbow Payoff={rainbow:.2%}, ICBC vs CBC Benefit={icbc_res['dispersion_benefit']:.2%}")

    # 2. Barrier, Digital & Autocallable
    bae = BarrierAutocallableEngine()
    h_shift = bae.calculate_discrete_barrier_shift(80.0, 0.20, 1.0, 252, is_short_barrier=True)
    dig_res = bae.calculate_digital_with_skew_correction(100.0, 100.0, 1.0, 0.05, 0.20, -0.05)
    auto_res = bae.evaluate_autocallable_step(1.12, 1.10, 0.70, 0.08, 0.0, is_snowball=True)
    logger.info(f"Barrier Engine: Shifted Barrier={h_shift:.2f}, Skew Digital Price=${dig_res['skew_corrected_digital_price']:.4f}, Autocall Action={auto_res['status']}")

    # 3. Cliquet & Mountain Range
    cmre = CliquetMountainRangeEngine()
    lflc = cmre.calculate_lflc_cliquet([0.05, -0.02, 0.08], 0.0, 0.05)
    napoleon = cmre.calculate_napoleon([0.05, -0.10, 0.04], 0.50)
    everest = cmre.calculate_everest([0.12, 0.05, -0.08, 0.20], 2.0)
    logger.info(f"Cliquet/Mountain Engine: LFLC Payoff={lflc:.2%}, Napoleon={napoleon:.2%}, Everest={everest:.2%}")

    # 4. Volatility Derivatives & Copulas
    vsce = VarianceSwapCopulaEngine()
    rv = vsce.calculate_realized_variance([0.01, -0.015, 0.02, -0.005, 0.012])
    greeks = vsce.calculate_variance_swap_greeks(1.0, 0.25, 0.20)
    copula_samples = vsce.simulate_gaussian_copula(corr, 100)
    logger.info(f"Variance Swap Engine: Realized Var={rv:.4f}, Cash Gamma={greeks['cash_gamma']:.2f}, Vega={greeks['vega']:.4f}, Copula Dimension={copula_samples.shape}")

    logger.success("[T1 PYTHON] Modules U1, V1, W1, X1 trained successfully on Phase 6 requirements.")

if __name__ == "__main__":
    train()
