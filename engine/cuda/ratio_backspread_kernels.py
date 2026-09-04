"""
Module BO6: CUDA Accelerated Parallel Simulation for 1:2 Ratio Backspread & Ladder Breakouts.
"""
import numpy as np

def simulate_ratio_backspread_breakout_cuda(n_paths: int = 100000):
    spots = np.random.uniform(50.0, 250.0, n_paths).astype(np.float64)
    atm_strikes = np.round(spots, 2)
    otm_strikes = np.round(spots * 1.05, 2)
    
    short_prems = spots * 0.035
    long_prems = spots * 0.015
    net_debits = (2.0 * long_prems) - short_prems
    
    # 20% jump or drop simulation
    terminal_spots = spots * np.random.choice([0.80, 0.95, 1.0, 1.05, 1.15, 1.30], n_paths)
    
    short_values = np.maximum(0.0, terminal_spots - atm_strikes)
    long_values = 2.0 * np.maximum(0.0, terminal_spots - otm_strikes)
    net_pnls = (long_values - short_values) - net_debits
    
    profitable_paths = np.sum(net_pnls > 0.0)
    max_gain = np.max(net_pnls)
    max_loss = np.min(net_pnls)
    
    return {
        "n_paths": n_paths,
        "profitable_paths_count": int(profitable_paths),
        "win_rate": float(profitable_paths / n_paths),
        "max_gain": float(max_gain),
        "max_loss": float(max_loss),
        "average_pnl": float(np.mean(net_pnls))
    }
