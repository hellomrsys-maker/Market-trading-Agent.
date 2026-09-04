"""
engine/cuda/kernels.py
=======================
OptionAlpha Agent — Custom CUDA/Triton GPU Kernels

Self-developed high-performance GPU kernels for:
  1. Fused LayerNorm + GELU activation (Transformer forward pass)
  2. Scaled Dot-Product Attention (flash-attention style, tiled)
  3. GARCH volatility forecast (parallelised over universe)
  4. Monte Carlo path simulation (batched random walks on GPU)
  5. Feature normalisation (online z-score, GPU-accelerated)

All kernels use OpenAI Triton (JIT-compiled to CUDA/HIP).
They fall back gracefully to pure PyTorch if CUDA is unavailable.
No external API calls. Fully self-contained.

Usage:
    from engine.cuda.kernels import (
        fused_layernorm_gelu,
        flash_attention_forward,
        garch_forecast_batch,
        mc_paths_gpu,
    )
"""

from __future__ import annotations

import math
import warnings
from typing import Optional, Tuple

import torch
import torch.nn.functional as F


# ─────────────────────────────────────────────────────────────
# Triton availability check
# ─────────────────────────────────────────────────────────────
try:
    import triton
    import triton.language as tl
    _TRITON_AVAILABLE = True
except ImportError:
    _TRITON_AVAILABLE = False
    warnings.warn(
        "Triton not available. CUDA kernels will fall back to PyTorch ops. "
        "Install triton>=2.3.0 for full GPU acceleration.",
        ImportWarning,
        stacklevel=2,
    )


# ─────────────────────────────────────────────────────────────
# 1. Fused LayerNorm + GELU (Triton kernel)
# ─────────────────────────────────────────────────────────────
if _TRITON_AVAILABLE:
    @triton.jit
    def _layernorm_gelu_kernel(
        x_ptr, y_ptr, w_ptr, b_ptr,
        N: tl.constexpr,
        eps: tl.constexpr,
        BLOCK: tl.constexpr,
    ):
        """
        Fused LayerNorm → GELU in a single kernel pass.
        Avoids a memory round-trip between the two ops.
        """
        row = tl.program_id(0)
        offs = tl.arange(0, BLOCK)
        mask = offs < N

        # Load row
        x = tl.load(x_ptr + row * N + offs, mask=mask, other=0.0).to(tl.float32)

        # LayerNorm
        mean  = tl.sum(x, axis=0) / N
        x_c   = x - mean
        var   = tl.sum(x_c * x_c, axis=0) / N
        x_hat = x_c * tl.rsqrt(var + eps)

        # Scale + shift
        w = tl.load(w_ptr + offs, mask=mask, other=1.0).to(tl.float32)
        b = tl.load(b_ptr + offs, mask=mask, other=0.0).to(tl.float32)
        x_scaled = w * x_hat + b

        # GELU approximation: x * 0.5 * (1 + tanh(sqrt(2/π) * (x + 0.044715*x³)))
        cdf = 0.5 * (1.0 + tl.libdevice.tanh(
            0.7978845608 * (x_scaled + 0.044715 * x_scaled * x_scaled * x_scaled)
        ))
        y = x_scaled * cdf
        tl.store(y_ptr + row * N + offs, y.to(tl.float16), mask=mask)


def fused_layernorm_gelu(
    x: torch.Tensor,
    weight: torch.Tensor,
    bias: torch.Tensor,
    eps: float = 1e-5,
) -> torch.Tensor:
    """
    Fused LayerNorm + GELU.
    x: (batch, seq_len, hidden_dim) or (batch, hidden_dim)
    """
    if not _TRITON_AVAILABLE or not x.is_cuda:
        # PyTorch fallback
        x_norm = F.layer_norm(x, (x.shape[-1],), weight, bias, eps)
        return F.gelu(x_norm)

    orig_shape = x.shape
    x = x.view(-1, x.shape[-1])
    B, N = x.shape
    BLOCK = triton.next_power_of_2(N)
    y = torch.empty_like(x, dtype=torch.float16)

    _layernorm_gelu_kernel[(B,)](
        x, y, weight, bias,
        N=N, eps=eps, BLOCK=BLOCK,
        num_warps=4,
    )
    return y.view(orig_shape)



# ─────────────────────────────────────────────────────────────
# 2. Scaled Dot-Product Attention (Triton flash-attention style)
# ─────────────────────────────────────────────────────────────
if _TRITON_AVAILABLE:
    @triton.jit
    def _flash_attn_fwd_kernel(
        Q_ptr, K_ptr, V_ptr, O_ptr,
        seq_len: tl.constexpr,
        d_head: tl.constexpr,
        scale: tl.constexpr,
        BLOCK_M: tl.constexpr,
        BLOCK_N: tl.constexpr,
    ):
        """
        Tiled flash-attention forward pass.
        Computes attention in O(N) memory instead of O(N²).
        """
        start_m = tl.program_id(0) * BLOCK_M
        offs_m = start_m + tl.arange(0, BLOCK_M)
        offs_d = tl.arange(0, d_head)

        # Load Q block
        Q = tl.load(Q_ptr + offs_m[:, None] * d_head + offs_d[None, :],
                    mask=offs_m[:, None] < seq_len)

        acc   = tl.zeros([BLOCK_M, d_head], dtype=tl.float32)
        l_i   = tl.zeros([BLOCK_M], dtype=tl.float32)
        m_i   = tl.full([BLOCK_M], float('-inf'), dtype=tl.float32)

        for start_n in range(0, seq_len, BLOCK_N):
            offs_n = start_n + tl.arange(0, BLOCK_N)
            mask_n = offs_n < seq_len

            K = tl.load(K_ptr + offs_n[None, :] * d_head + offs_d[:, None],
                        mask=mask_n[None, :])
            V = tl.load(V_ptr + offs_n[:, None] * d_head + offs_d[None, :],
                        mask=mask_n[:, None])

            # QK^T / sqrt(d)
            S = tl.dot(Q, K) * scale  # (BLOCK_M, BLOCK_N)

            # Online softmax
            m_new = tl.maximum(m_i, tl.max(S, axis=1))
            alpha  = tl.exp(m_i - m_new)
            p      = tl.exp(S - m_new[:, None])
            l_i    = alpha * l_i + tl.sum(p, axis=1)
            acc    = alpha[:, None] * acc + tl.dot(p, V)
            m_i    = m_new

        acc = acc / l_i[:, None]
        tl.store(O_ptr + offs_m[:, None] * d_head + offs_d[None, :],
                 acc, mask=offs_m[:, None] < seq_len)


def flash_attention_forward(
    q: torch.Tensor, k: torch.Tensor, v: torch.Tensor,
) -> torch.Tensor:
    """
    Flash attention: q/k/v shape (batch, heads, seq, d_head).
    Falls back to torch.nn.functional.scaled_dot_product_attention
    when Triton is unavailable.
    """
    if not _TRITON_AVAILABLE or not q.is_cuda:
        return F.scaled_dot_product_attention(q, k, v)

    B, H, S, D = q.shape
    scale = 1.0 / math.sqrt(D)
    out   = torch.empty_like(q)
    BLOCK_M = min(64, S)
    BLOCK_N = min(64, S)
    grid = (math.ceil(S / BLOCK_M), B * H)
    _flash_attn_fwd_kernel[grid](
        q.reshape(B * H, S, D), k.reshape(B * H, S, D), v.reshape(B * H, S, D),
        out.reshape(B * H, S, D),
        seq_len=S, d_head=D, scale=scale,
        BLOCK_M=BLOCK_M, BLOCK_N=BLOCK_N,
    )
    return out




# ─────────────────────────────────────────────────────────────
# 3. GARCH(1,1) Volatility Forecast — batched on GPU
# Pure PyTorch (no Triton kernel needed; vectorised over symbols)
# ─────────────────────────────────────────────────────────────

def garch_forecast_batch(
    returns: torch.Tensor,    # (n_symbols, n_days) daily log-returns
    h0: Optional[torch.Tensor] = None,  # (n_symbols,) initial variance
    omega: float = 1e-6,
    alpha: float = 0.10,
    beta: float  = 0.85,
    horizon: int = 10,
) -> torch.Tensor:
    """
    GARCH(1,1) 10-day volatility forecast for each symbol (vectorised).

    h_{t+1} = omega + alpha * epsilon_t^2 + beta * h_t

    Returns annualised forecast volatility: (n_symbols, horizon).
    """
    n_sym, n_days = returns.shape
    device = returns.device

    if h0 is None:
        # Initialise with sample variance
        h0 = returns.var(dim=1, unbiased=False).clamp(min=1e-8)

    h = h0.clone()
    forecasts = torch.zeros(n_sym, horizon, device=device)

    # Warm-up pass over history
    for t in range(n_days):
        eps2 = returns[:, t] ** 2
        h    = omega + alpha * eps2 + beta * h

    # Multi-step forecast (iterate under constant expected eps² = h)
    h_fwd = h.clone()
    for k in range(horizon):
        h_fwd = omega + (alpha + beta) * h_fwd
        forecasts[:, k] = h_fwd

    # Annualise: σ_daily → σ_annual = σ_daily * sqrt(252)
    return (forecasts * 252).sqrt()


# ─────────────────────────────────────────────────────────────
# 4. Monte Carlo Path Simulation (GPU-accelerated)
# ─────────────────────────────────────────────────────────────

def mc_paths_gpu(
    S0:    float,
    mu:    float,           # drift (risk-neutral: mu = r)
    sigma: float,           # annualised vol
    T:     float,           # years to expiry
    n_paths: int = 100_000,
    n_steps: int = 252,
    device: str = "cpu",
) -> torch.Tensor:
    """
    Simulate n_paths GBM paths using Euler-Maruyama on GPU.
    Returns terminal prices: (n_paths,)

    Uses antithetic variates: first n_paths/2 are regular,
    second half are antithetic (−Z). Ensures E[S_T] = S₀ * exp(mu*T).
    """
    dev    = torch.device(device)
    dt     = T / n_steps
    half   = n_paths // 2

    # Generate antithetic Brownian increments
    Z = torch.randn(half, n_steps, device=dev)
    Z = torch.cat([Z, -Z], dim=0)  # (n_paths, n_steps)

    # Geometric Brownian Motion
    drift = (mu - 0.5 * sigma ** 2) * dt
    diff  = sigma * math.sqrt(dt) * Z

    log_returns = drift + diff            # (n_paths, n_steps)
    log_S_T     = log_returns.sum(dim=1)  # (n_paths,)
    return S0 * torch.exp(log_S_T)


# ─────────────────────────────────────────────────────────────
# 5. Online Feature Normalisation (GPU)
# ─────────────────────────────────────────────────────────────

class OnlineNormalizer:
    """
    Welford's online z-score normaliser running on GPU tensors.
    Updates incrementally — no need to store entire history.
    Thread-safe for single-writer use.
    """
    def __init__(self, n_features: int, device: str = "cpu"):
        dev = torch.device(device)
        self.n    = torch.zeros(1, device=dev)
        self.mean = torch.zeros(n_features, device=dev)
        self.M2   = torch.ones(n_features, device=dev)    # variance accumulator
        self.n_features = n_features

    def update(self, x: torch.Tensor) -> None:
        """x: (n_features,) — one observation."""
        self.n  += 1
        delta    = x - self.mean
        self.mean += delta / self.n
        delta2   = x - self.mean
        self.M2  += delta * delta2

    def normalize(self, x: torch.Tensor) -> torch.Tensor:
        """Returns z-score of x."""
        std = (self.M2 / self.n.clamp(min=1)).sqrt().clamp(min=1e-8)
        return (x - self.mean) / std

    def variance(self) -> torch.Tensor:
        return self.M2 / self.n.clamp(min=1)
