"""
Module AM6 (CUDA): Mass GPU Parallel COT Institutional Sentiment Kernels.
Vectorized batch calculation of COT percentile indices and volume/OI regime matrices.
"""

import numpy as np


def batch_compute_cot_sentiment_cuda(
    current_net_arr: np.ndarray,
    min_net_arr: np.ndarray,
    max_net_arr: np.ndarray,
    price_change_arr: np.ndarray,
    oi_change_arr: np.ndarray
) -> np.ndarray:
    """
    Vectorized CUDA GPU kernel simulator:
    Computes COT index %, extreme flags, and institutional bias categories.
    """
    rng = np.maximum(1.0, max_net_arr - min_net_arr)
    cot_indices = np.clip(((current_net_arr - min_net_arr) / rng) * 100.0, 0.0, 100.0)
    extreme_flags = np.where((cot_indices >= 90.0) | (cot_indices <= 10.0), 1.0, 0.0)

    # 1 Strong Bull, 2 Weak Bull, 3 Strong Bear, 4 Weak Bear
    bias = np.where(
        (price_change_arr > 0) & (oi_change_arr > 0), 1.0,
        np.where(
            (price_change_arr > 0) & (oi_change_arr <= 0), 2.0,
            np.where(
                (price_change_arr < 0) & (oi_change_arr > 0), 3.0, 4.0
            )
        )
    )

    # Return shape (N, 3): [cot_index, extreme_flag, bias_category]
    return np.column_stack([cot_indices, extreme_flags, bias])
