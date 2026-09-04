// engine/cuda/tri_state_kernel.cu
// OptionAlpha Agent — Native CUDA Kernel for High-Throughput Batch Option Sizing & Payoffs
// Polyglot Pillar 5: CUDA / Triton GPU Acceleration

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <math.h>

extern "C" __global__ void batch_call_put_payoffs_kernel(
    const double* spot_prices,
    const double* strikes,
    const double* premiums,
    const int* is_call,
    double* out_payoffs,
    int n,
    double multiplier
) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idx < n) {
        double s = spot_prices[idx];
        double k = strikes[idx];
        double p = premiums[idx];
        int call = is_call[idx];

        double payoff = 0.0;
        if (call == 1) {
            // Long Call Payoff: max(S - K, 0) - Premium
            payoff = (fmax(s - k, 0.0) - p) * multiplier;
        } else {
            // Cash-Secured Put Payoff: Premium - max(K - S, 0)
            payoff = (p - fmax(k - s, 0.0)) * multiplier;
        }
        out_payoffs[idx] = payoff;
    }
}
