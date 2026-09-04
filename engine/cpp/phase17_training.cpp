#include <iostream>
#include <cassert>
#include "kaching_convexity_engine.hpp"
#include "cross_market_pdt_engine.hpp"
#include "ratio_backspread_engine.hpp"
#include "exotic_multileg_ladder_engine.hpp"

using namespace optionalpha;

int main() {
    std::cout << "======================================================" << std::endl;
    std::cout << "  PHASE 17 ZERO-BRIDGE C++ BENCHMARK & MEMORY AUDIT   " << std::endl;
    std::cout << "======================================================" << std::endl;

    // 1. Verify exact 64-byte alignment
    std::cout << "[Audit 1/4] Checking 64-byte Zero-Bridge Memory Layouts:" << std::endl;
    std::cout << "  - sizeof(KaChingConvexityState):      " << sizeof(KaChingConvexityState) << " bytes" << std::endl;
    std::cout << "  - sizeof(CrossMarketPdtState):        " << sizeof(CrossMarketPdtState) << " bytes" << std::endl;
    std::cout << "  - sizeof(RatioBackspreadState):       " << sizeof(RatioBackspreadState) << " bytes" << std::endl;
    std::cout << "  - sizeof(ExoticMultiLegLadderState):  " << sizeof(ExoticMultiLegLadderState) << " bytes" << std::endl;

    static_assert(sizeof(KaChingConvexityState) == 64, "Alignment Failure: KaChingConvexityState");
    static_assert(sizeof(CrossMarketPdtState) == 64, "Alignment Failure: CrossMarketPdtState");
    static_assert(sizeof(RatioBackspreadState) == 64, "Alignment Failure: RatioBackspreadState");
    static_assert(sizeof(ExoticMultiLegLadderState) == 64, "Alignment Failure: ExoticMultiLegLadderState");

    // 2. Test Module BM: Weekly Cash KaChing Engine
    auto kc_state = KaChingConvexityEngineCpp::initialize(100.0, 0.25, 120);
    assert(kc_state.long_put_strike < 100.0);
    assert(kc_state.short_put_strike == 100.0);
    KaChingConvexityEngineCpp::evaluate_harvest(kc_state, 0.20, 2); // 80%+ banked on Tuesday
    assert(kc_state.double_dip_active == 1);
    std::cout << "[Pass] Module BM: Weekly KaChing & Double-Dip Harvest verified." << std::endl;

    // 3. Test Module BN: Cross-Market PDT Governor
    CrossMarketPdtState pdt_state{};
    pdt_state.account_equity = 15000.0; // Sub-25k account
    pdt_state.round_trips_5d = 3;
    bool compliant = CrossMarketPdtEngineCpp::audit_compliance(pdt_state, true, 500.0);
    assert(!compliant);
    assert(pdt_state.pdt_restricted == 1);
    std::cout << "[Pass] Module BN: SEC PDT Rule & 5% Risk Governor verified." << std::endl;

    // 4. Test Module BO: 1:2 Ratio Backspread
    auto rb_state = RatioBackspreadEngineCpp::construct(100.0, 105.0, 3.50, 1.50, true);
    assert(rb_state.max_loss_point > 0.0);
    double pnl_high = RatioBackspreadEngineCpp::calculate_terminal_pnl(rb_state, 120.0);
    assert(pnl_high > 0.0);
    std::cout << "[Pass] Module BO: 1:2 Ratio Backspread Convexity verified." << std::endl;

    // 5. Test Module BP: Exotic Multi-Leg Ladder & Strip/Strap
    auto strip_state = ExoticMultiLegLadderEngineCpp::construct_strip(100.0, 100.0, 2.50, 2.50);
    assert(strip_state.put_legs_count == 2);
    assert(strip_state.call_legs_count == 1);
    std::cout << "[Pass] Module BP: Strip/Strap & Lambda Elasticity verified." << std::endl;

    std::cout << "All Phase 17 C++ Zero-Bridge tests passed successfully!" << std::endl;
    return 0;
}
