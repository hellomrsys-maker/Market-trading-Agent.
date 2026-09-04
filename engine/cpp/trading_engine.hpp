/*
 * engine/cpp/trading_engine.hpp
 * ==============================
 * OptionAlpha Agent — C++ Core Trading Engine
 *
 * Responsibilities:
 *  - Order lifecycle management (state machine)
 *  - Lock-free position book (atomic operations)
 *  - Nanosecond-resolution timestamping
 *  - In-process risk pre-check before sending to Alpaca
 *  - Circular buffer for tick data (zero-copy)
 *
 * Thread model: one producer thread (data ingest) + N consumer
 * threads (strategy workers). All shared state is lock-free.
 *
 * Python binding: exposed via ctypes / cffi as a shared library.
 * Build: cmake -DCMAKE_BUILD_TYPE=Release -S engine/cpp -B build/cpp
 */

#pragma once

#include <atomic>
#include <array>
#include <cstdint>
#include <cstring>
#include <chrono>
#include <functional>
#include <optional>
#include <string_view>

namespace optionalpha {

// ─────────────────────────────────────────────────────────────
// Timestamp (nanoseconds since Unix epoch)
// ─────────────────────────────────────────────────────────────
using Nanos = std::int64_t;

inline Nanos now_ns() noexcept {
    return std::chrono::duration_cast<std::chrono::nanoseconds>(
        std::chrono::system_clock::now().time_since_epoch()
    ).count();
}

// ─────────────────────────────────────────────────────────────
// Atomic Memory State Vector (64 bytes, cache-line aligned)
// The Zero-Bridge synchronous memory interface: Python and C++
// share EXACTLY these addresses. No serialisation. No copy.
// ─────────────────────────────────────────────────────────────
struct alignas(64) AtomicStateVector {
    std::atomic<double>   equity{0.0};          // bytes  0-7
    std::atomic<double>   daily_pnl{0.0};       // bytes  8-15
    std::atomic<double>   delta_exposure{0.0};  // bytes 16-23
    std::atomic<int32_t>  open_positions{0};    // bytes 24-27
    std::atomic<int32_t>  orders_today{0};      // bytes 28-31
    std::atomic<bool>     halted{false};        // byte  32
    std::atomic<bool>     market_open{false};   // byte  33
    std::atomic<uint8_t>  regime{0};            // byte  34: 0=neutral,1=bull,2=bear,3=highIV
    std::atomic<uint8_t>  pad0{0};             // byte  35
    std::atomic<double>   vix{0.0};            // bytes 36-43
    std::atomic<Nanos>    last_update_ns{0};   // bytes 44-51
    std::atomic<uint64_t> sequence{0};         // bytes 52-59  (monotonic order ID)
    std::atomic<int32_t>  pad1{0};            // bytes 60-63
};
static_assert(sizeof(AtomicStateVector) == 64, "Must be exactly one cache line");

// ─────────────────────────────────────────────────────────────
// Order States
// ─────────────────────────────────────────────────────────────
enum class OrderStatus : uint8_t {
    PENDING   = 0,
    SUBMITTED = 1,
    FILLED    = 2,
    CANCELLED = 3,
    REJECTED  = 4,
    EXPIRED   = 5,
};

enum class OptionSide : uint8_t { CALL = 0, PUT = 1 };
enum class OrderSide  : uint8_t { BUY  = 0, SELL = 1 };
enum class OrderType  : uint8_t { MARKET = 0, LIMIT = 1, DEBIT_SPREAD = 2, CREDIT_SPREAD = 3 };
enum class Strategy   : uint8_t { WHEEL_CSP = 0, WHEEL_CC = 1, IRON_CONDOR = 2, CLOSE = 3 };

// ─────────────────────────────────────────────────────────────
// Compact Order Record (128 bytes, fits 2 cache lines)
// ─────────────────────────────────────────────────────────────
struct alignas(64) OrderRecord {
    char          symbol[8];         // underlying, e.g. "SPY\0"
    char          contract_id[24];   // OCC symbol, e.g. "SPY251121C00550000"
    uint64_t      order_id;          // local sequence number
    Nanos         created_ns;
    Nanos         filled_ns;
    double        strike;
    double        premium_received;  // credit (positive) or debit (negative)
    double        unrealized_pnl;
    double        delta;
    double        theta;
    double        vega;
    int32_t       quantity;          // number of contracts (negative = short)
    int16_t       dte_at_open;
    OrderStatus   status;
    OptionSide    option_side;
    OrderSide     order_side;
    OrderType     order_type;
    Strategy      strategy;
    uint8_t       legs;              // 1 = single, 4 = iron condor
    uint8_t       _pad[5];
};
static_assert(sizeof(OrderRecord) == 128);

// ─────────────────────────────────────────────────────────────
// Lock-free circular ring buffer for tick / quote data
// ─────────────────────────────────────────────────────────────
template <typename T, std::size_t Capacity>
class alignas(64) RingBuffer {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be power of 2");
public:
    bool push(const T& item) noexcept {
        const auto head = head_.load(std::memory_order_relaxed);
        const auto next = (head + 1) & mask_;
        if (next == tail_.load(std::memory_order_acquire)) return false; // full
        data_[head] = item;
        head_.store(next, std::memory_order_release);
        return true;
    }

    bool pop(T& out) noexcept {
        const auto tail = tail_.load(std::memory_order_relaxed);
        if (tail == head_.load(std::memory_order_acquire)) return false; // empty
        out = data_[tail];
        tail_.store((tail + 1) & mask_, std::memory_order_release);
        return true;
    }

    std::size_t size() const noexcept {
        return (head_.load() - tail_.load()) & mask_;
    }

private:
    static constexpr std::size_t mask_ = Capacity - 1;
    std::array<T, Capacity>   data_{};
    alignas(64) std::atomic<std::size_t> head_{0};
    alignas(64) std::atomic<std::size_t> tail_{0};
};

// ─────────────────────────────────────────────────────────────
// Quote Tick (48 bytes)
// ─────────────────────────────────────────────────────────────
struct alignas(16) QuoteTick {
    Nanos    timestamp_ns;
    double   bid;
    double   ask;
    double   iv;         // implied volatility (from data layer)
    double   delta;
    float    iv_rank;    // 0-100
    uint32_t bid_sz;
    uint32_t ask_sz;
};

// Ring buffers: 4096 entries each underlying
using TickBuffer = RingBuffer<QuoteTick, 4096>;

// ─────────────────────────────────────────────────────────────
// Risk Pre-Checker (called synchronously before every order)
// ─────────────────────────────────────────────────────────────
struct RiskConfig {
    double   max_position_pct;    // fraction of equity per position
    double   daily_loss_limit;    // absolute $ loss allowed per day
    double   max_delta_exposure;  // absolute portfolio delta
    int32_t  max_open_positions;
    float    vix_halt_threshold;
    float    ic_min_iv_rank;
};

enum class RiskDecision : uint8_t {
    ALLOW   = 0,
    REJECT  = 1,  // hard block
    SCALE   = 2,  // reduce size and allow
};

struct RiskResult {
    RiskDecision decision;
    int32_t      suggested_qty;   // valid when decision == SCALE
    char         reason[64];
};

class RiskGate {
public:
    explicit RiskGate(const RiskConfig& cfg, const AtomicStateVector& state)
        : cfg_(cfg), state_(state) {}

    RiskResult check(const OrderRecord& order) const noexcept {
        RiskResult result{RiskDecision::ALLOW, order.quantity, {}};

        // 1. Halt gate
        if (state_.halted.load(std::memory_order_acquire)) {
            result.decision = RiskDecision::REJECT;
            std::strncpy(result.reason, "Agent halted (circuit breaker active)", 64);
            return result;
        }

        // 2. Daily loss limit
        const double daily_pnl = state_.daily_pnl.load(std::memory_order_relaxed);
        if (daily_pnl < -cfg_.daily_loss_limit) {
            result.decision = RiskDecision::REJECT;
            std::strncpy(result.reason, "Daily loss limit reached", 64);
            return result;
        }

        // 3. VIX circuit breaker (Iron Condors only)
        const double vix = state_.vix.load(std::memory_order_relaxed);
        if (vix > cfg_.vix_halt_threshold && order.strategy == Strategy::IRON_CONDOR) {
            result.decision = RiskDecision::REJECT;
            std::strncpy(result.reason, "VIX above threshold: Iron Condors halted", 64);
            return result;
        }

        // 4. Max open positions
        if (state_.open_positions.load() >= cfg_.max_open_positions) {
            result.decision = RiskDecision::REJECT;
            std::strncpy(result.reason, "Max open positions reached", 64);
            return result;
        }

        // 5. Position size check
        const double equity = state_.equity.load(std::memory_order_relaxed);
        const double max_notional = equity * cfg_.max_position_pct / 100.0;
        const double notional = std::abs(order.premium_received * 100.0 * order.quantity);
        if (notional > max_notional) {
            // Scale down
            const int32_t scaled_qty = std::max(1, static_cast<int32_t>(
                max_notional / (std::abs(order.premium_received) * 100.0)
            ));
            result.decision     = RiskDecision::SCALE;
            result.suggested_qty = scaled_qty;
            std::strncpy(result.reason, "Position scaled to fit size limit", 64);
        }

        return result;
    }

private:
    RiskConfig            cfg_;
    const AtomicStateVector& state_;
};

// ─────────────────────────────────────────────────────────────
// TradingEngine — top-level coordinator
// ─────────────────────────────────────────────────────────────
class TradingEngine {
public:
    TradingEngine(const RiskConfig& risk_cfg)
        : risk_gate_(risk_cfg, state_) {
        state_.last_update_ns.store(now_ns());
    }

    // Called by Python via ctypes to update shared state
    void update_equity(double equity) noexcept {
        state_.equity.store(equity);
        state_.last_update_ns.store(now_ns());
        state_.sequence.fetch_add(1, std::memory_order_relaxed);
    }

    void update_daily_pnl(double pnl) noexcept { state_.daily_pnl.store(pnl); }
    void update_delta(double delta)    noexcept { state_.delta_exposure.store(delta); }
    void update_vix(double vix)        noexcept { state_.vix.store(vix); }
    void set_regime(uint8_t regime)    noexcept { state_.regime.store(regime); }
    void set_market_open(bool open)    noexcept { state_.market_open.store(open); }
    void set_halted(bool halt)         noexcept { state_.halted.store(halt); }

    void increment_positions(int delta) noexcept {
        state_.open_positions.fetch_add(delta, std::memory_order_relaxed);
    }

    RiskResult evaluate_order(const OrderRecord& order) const noexcept {
        return risk_gate_.check(order);
    }

    // Direct pointer to the shared state vector (exported to Python)
    const AtomicStateVector* state_ptr() const noexcept { return &state_; }
    AtomicStateVector*       state_ptr_mut()  noexcept { return &state_; }

    // Tick buffer for a given symbol index (0–6 for universe)
    TickBuffer& tick_buffer(std::size_t symbol_idx) noexcept {
        return tick_buffers_[symbol_idx % MAX_SYMBOLS];
    }

    static constexpr std::size_t MAX_SYMBOLS = 16;

private:
    AtomicStateVector               state_;
    RiskGate                        risk_gate_;
    std::array<TickBuffer, MAX_SYMBOLS> tick_buffers_;
};

} // namespace optionalpha


// ─────────────────────────────────────────────────────────────
// C ABI exports for Python ctypes / cffi binding
// ─────────────────────────────────────────────────────────────
extern "C" {

struct OA_RiskConfig {
    double  max_position_pct;
    double  daily_loss_limit;
    double  max_delta_exposure;
    int32_t max_open_positions;
    float   vix_halt_threshold;
    float   ic_min_iv_rank;
};

struct OA_RiskResult {
    uint8_t decision;        // 0=ALLOW, 1=REJECT, 2=SCALE
    int32_t suggested_qty;
    char    reason[64];
};

void*         OA_Engine_create(const OA_RiskConfig* cfg);
void          OA_Engine_destroy(void* engine);
void          OA_Engine_update_equity(void* engine, double equity);
void          OA_Engine_update_daily_pnl(void* engine, double pnl);
void          OA_Engine_update_delta(void* engine, double delta);
void          OA_Engine_update_vix(void* engine, double vix);
void          OA_Engine_set_regime(void* engine, uint8_t regime);
void          OA_Engine_set_market_open(void* engine, bool open);
void          OA_Engine_set_halted(void* engine, bool halt);
void          OA_Engine_increment_positions(void* engine, int delta);
OA_RiskResult OA_Engine_evaluate_order(void* engine, const optionalpha::OrderRecord* order);
void*         OA_Engine_state_ptr(void* engine);

} // extern "C"
