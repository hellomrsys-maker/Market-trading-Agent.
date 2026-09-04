/*
 * engine/cpp/trading_engine.cpp
 * ==============================
 * C++ Core Trading Engine — Implementation + C ABI exports
 */

#include "trading_engine.hpp"
#include <new>
#include <cstdlib>

namespace optionalpha {
// All implementation is header-inline. Nothing additional needed.
}

// ─────────────────────────────────────────────────────────────
// C ABI Implementation
// ─────────────────────────────────────────────────────────────
extern "C" {

void* OA_Engine_create(const OA_RiskConfig* cfg) {
    optionalpha::RiskConfig rc{
        cfg->max_position_pct,
        cfg->daily_loss_limit,
        cfg->max_delta_exposure,
        cfg->max_open_positions,
        cfg->vix_halt_threshold,
        cfg->ic_min_iv_rank,
    };
    return new (std::nothrow) optionalpha::TradingEngine(rc);
}

void OA_Engine_destroy(void* engine) {
    delete static_cast<optionalpha::TradingEngine*>(engine);
}

void OA_Engine_update_equity(void* engine, double equity) {
    static_cast<optionalpha::TradingEngine*>(engine)->update_equity(equity);
}

void OA_Engine_update_daily_pnl(void* engine, double pnl) {
    static_cast<optionalpha::TradingEngine*>(engine)->update_daily_pnl(pnl);
}

void OA_Engine_update_delta(void* engine, double delta) {
    static_cast<optionalpha::TradingEngine*>(engine)->update_delta(delta);
}

void OA_Engine_update_vix(void* engine, double vix) {
    static_cast<optionalpha::TradingEngine*>(engine)->update_vix(vix);
}

void OA_Engine_set_regime(void* engine, uint8_t regime) {
    static_cast<optionalpha::TradingEngine*>(engine)->set_regime(regime);
}

void OA_Engine_set_market_open(void* engine, bool open) {
    static_cast<optionalpha::TradingEngine*>(engine)->set_market_open(open);
}

void OA_Engine_set_halted(void* engine, bool halt) {
    static_cast<optionalpha::TradingEngine*>(engine)->set_halted(halt);
}

void OA_Engine_increment_positions(void* engine, int delta) {
    static_cast<optionalpha::TradingEngine*>(engine)->increment_positions(delta);
}

OA_RiskResult OA_Engine_evaluate_order(void* engine, const optionalpha::OrderRecord* order) {
    auto result = static_cast<optionalpha::TradingEngine*>(engine)->evaluate_order(*order);
    OA_RiskResult out{};
    out.decision     = static_cast<uint8_t>(result.decision);
    out.suggested_qty = result.suggested_qty;
    std::strncpy(out.reason, result.reason, 64);
    return out;
}

void* OA_Engine_state_ptr(void* engine) {
    return static_cast<optionalpha::TradingEngine*>(engine)->state_ptr_mut();
}

} // extern "C"
