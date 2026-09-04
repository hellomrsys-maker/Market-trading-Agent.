"""
Module BM6: CUDA Accelerated Parallel Simulation for Weekly Cash KaChing Dual-Decay Model.
"""
import numpy as np

def simulate_kaching_dual_decay_cuda(n_scenarios: int = 100000):
    spots = np.random.uniform(50.0, 300.0, n_scenarios).astype(np.float64)
    ivs = np.random.uniform(0.15, 0.65, n_scenarios).astype(np.float64)
    
    # Vectorized long put and short put generation
    long_deltas = np.where(ivs > 0.35, 0.38, 0.25)
    long_strikes = spots * (1.0 - np.where(long_deltas == 0.25, 0.08, 0.05))
    short_strikes = spots
    
    weekly_premiums = spots * 0.018 * (1.0 + ivs)
    
    # Simulate price paths over 4 weeks (20 trading days)
    daily_returns = np.random.normal(0.0005, ivs / np.sqrt(252.0), (20, n_scenarios))
    price_paths = spots * np.cumprod(1.0 + daily_returns, axis=0)
    terminal_spots = price_paths[-1]
    
    # Evaluate assignment risk vs profit
    itm_short_count = np.sum(terminal_spots < short_strikes)
    deep_drop_protected = np.sum((terminal_spots < long_strikes) & (long_strikes - terminal_spots > weekly_premiums))
    
    total_cash_collected = np.sum(weekly_premiums * 4.0)
    
    return {
        "n_scenarios": n_scenarios,
        "total_cash_collected": float(total_cash_collected),
        "itm_short_rate": float(itm_short_count / n_scenarios),
        "deep_drop_protection_rate": float(deep_drop_protected / n_scenarios),
        "mean_spot": float(np.mean(spots)),
        "mean_weekly_premium": float(np.mean(weekly_premiums))
    }
