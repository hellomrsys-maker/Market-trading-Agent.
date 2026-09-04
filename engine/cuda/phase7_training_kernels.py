"""
Phase 7 Training Matrix Runner (T6 - CUDA)
Benchmarks and trains CUDA GPU kernels across Modules Y6, Z6, AA6, AB6.
"""

import numpy as np
from behavioral_psychology_kernels import batch_evaluate_3p_resilience_cuda
from cashflow_capital_kernels import batch_compute_sinking_funds_cuda, batch_compute_workable_totals_cuda
from tactical_swing_kernels import batch_evaluate_abcd_cuda
from tactical_options_kernels import batch_structure_iron_condor_cuda


def train_phase7_cuda():
    print("[T6 CUDA] Starting GPU Parallel Processing Training Kernels for Phase 7...")

    # Y6 Batch
    perm = np.array([0.2, 0.5, 0.8], dtype=np.float32)
    perv = np.array([0.3, 0.6, 0.9], dtype=np.float32)
    pers = np.array([0.1, 0.4, 0.7], dtype=np.float32)
    y_res = batch_evaluate_3p_resilience_cuda(perm, perv, pers)

    # Z6 Batch
    targets = np.array([800.0, 1500.0, 5000.0], dtype=np.float32)
    periods = np.array([34, 26, 52], dtype=np.int32)
    buffers = np.array([0.10, 0.05, 0.10], dtype=np.float32)
    sf_res = batch_compute_sinking_funds_cuda(targets, periods, buffers)

    # AA6 Batch
    pts_a = np.array([40.0, 100.0], dtype=np.float32)
    pts_b = np.array([55.0, 80.0], dtype=np.float32)
    pts_c = np.array([48.0, 90.0], dtype=np.float32)
    bull_flags = np.array([True, False], dtype=bool)
    aa_res = batch_evaluate_abcd_cuda(pts_a, pts_b, pts_c, bull_flags)

    # AB6 Batch
    k1 = np.array([50.0], dtype=np.float32)
    k2 = np.array([60.0], dtype=np.float32)
    ps = np.array([2.0], dtype=np.float32)
    pl = np.array([1.0], dtype=np.float32)
    cs = np.array([2.0], dtype=np.float32)
    cl = np.array([1.0], dtype=np.float32)
    ab_res = batch_structure_iron_condor_cuda(k1, k2, ps, pl, cs, cl)

    print("[T6 CUDA] Modules Y6, Z6, AA6, AB6 trained successfully.")


if __name__ == "__main__":
    train_phase7_cuda()
