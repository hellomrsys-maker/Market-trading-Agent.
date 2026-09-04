#pragma once
/**
 * engine/cpp/hot_path.hpp
 * =======================
 * OptionAlpha Agent — Branch-Free Hot Path Risk Check (C++20)
 *
 * Microsecond-latency order pre-screening logic reading the 64-byte AtomicStateVector.
 */

#include <cstdint>
#include <atomic>

namespace optionalpha {

struct alignas(64) HotPathRiskState {
    std::atomic<int64_t>  daily_loss_limit_cents;
    std::atomic<int64_t>  current_daily_pnl_cents;
    std::atomic<uint32_t> max_open_positions;
    std::atomic<uint32_t> current_open_positions;
    std::atomic<float>    max_portfolio_delta;
    std::atomic<float>    current_portfolio_delta;
    std::atomic<uint32_t> circuit_breaker_tripped;
};

class HotPathRiskChecker {
public:
    static inline bool check_fast(
        const HotPathRiskState& state,
        int64_t order_collateral_cents,
        float order_delta
    ) noexcept {
        // 1. Check Circuit Breaker flag
        if (state.circuit_breaker_tripped.load(std::memory_order_relaxed) != 0) {
            return false;
        }

        // 2. Daily Loss Limit
        int64_t pnl = state.current_daily_pnl_cents.load(std::memory_order_relaxed);
        int64_t limit = state.daily_loss_limit_cents.load(std::memory_order_relaxed);
        if (pnl <= -limit) {
            return false;
        }

        // 3. Position Capacity
        uint32_t open_pos = state.current_open_positions.load(std::memory_order_relaxed);
        uint32_t max_pos = state.max_open_positions.load(std::memory_order_relaxed);
        if (open_pos >= max_pos) {
            return false;
        }

        // 4. Portfolio Delta Bounds
        float delta = state.current_portfolio_delta.load(std::memory_order_relaxed);
        float max_delta = state.max_portfolio_delta.load(std::memory_order_relaxed);
        if (std::abs(delta + order_delta) > max_delta) {
            return false;
        }

        return true;
    }
};

} // namespace optionalpha
