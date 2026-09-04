#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * Module BQ: 64-byte Zero-Bridge State Vector for 24/7 Crypto Spot Trading & Arbitrage Engine.
 * sizeof(CryptoSpotState) == 64 bytes exactly (Cache-line aligned, 0-nanosecond sync).
 */
struct alignas(64) CryptoSpotState {
    double spot_price;                  // 8 bytes: Current crypto spot price
    double bid_depth_usd;               // 8 bytes: Level-2 top-of-book bid liquidity
    double ask_depth_usd;               // 8 bytes: Level-2 top-of-book ask liquidity
    double order_book_imbalance;        // 8 bytes: OBI ratio = (Bid - Ask) / (Bid + Ask)
    double triangular_arb_spread;       // 8 bytes: Synthetic cross-rate discrepancy pct
    double non_marginable_buying_power; // 8 bytes: 100% cash buying power (no margin)
    uint32_t asset_pair_id;             // 4 bytes: Hash of pair e.g. BTC/USD = 1, ETH/USD = 2
    uint16_t max_notional_k;            // 2 bytes: Max order notional limit ($200k cap)
    uint8_t is_tradable;                // 1 byte: 1 if active, 0 if restricted
    uint8_t is_fractionable;            // 1 byte: 1 if fractional units allowed
    uint16_t fee_bps;                   // 2 bytes: Taker fee in basis points (e.g. 25 bps)
    uint16_t status_flags;              // 2 bytes: 1=ACTIVE, 2=ARB_DETECTED, 4=MOMENTUM_LONG
    uint8_t padding[4];                 // 4 bytes padding -> 64 bytes total
};

static_assert(sizeof(CryptoSpotState) == 64, "CryptoSpotState must be exactly 64 bytes!");

class CryptoSpotEngineCpp {
public:
    static CryptoSpotState initialize(double spot, double cash_power, uint32_t pair_id) {
        CryptoSpotState state{};
        state.spot_price = spot;
        state.bid_depth_usd = spot * 5.0;
        state.ask_depth_usd = spot * 5.0;
        state.order_book_imbalance = 0.0;
        state.triangular_arb_spread = 0.0;
        state.non_marginable_buying_power = cash_power;
        state.asset_pair_id = pair_id;
        state.max_notional_k = 200; // $200k limit per Alpaca rules
        state.is_tradable = 1;
        state.is_fractionable = 1;
        state.fee_bps = 25; // Tier 1 Taker fee: 25 bps
        state.status_flags = 1;
        return state;
    }

    static double compute_orderbook_imbalance(CryptoSpotState& state, double bid_vol, double ask_vol) {
        double total = bid_vol + ask_vol;
        if (total <= 0.0001) {
            state.order_book_imbalance = 0.0;
            return 0.0;
        }
        state.order_book_imbalance = (bid_vol - ask_vol) / total;
        return state.order_book_imbalance;
    }

    static double evaluate_triangular_arbitrage(
        CryptoSpotState& state,
        double btc_usd,
        double eth_btc,
        double eth_usd
    ) {
        // Synthetic cross-rate: P(ETH/USD) = P(ETH/BTC) * P(BTC/USD)
        double synthetic_eth_usd = eth_btc * btc_usd;
        if (eth_usd <= 0.0001) return 0.0;
        double discrepancy = (eth_usd - synthetic_eth_usd) / eth_usd;
        state.triangular_arb_spread = discrepancy;
        
        // Fee threshold: 2 legs * 25 bps = 50 bps (0.005)
        if (std::abs(discrepancy) > 0.0050) {
            state.status_flags |= 2; // ARB_DETECTED
        }
        return discrepancy;
    }
};

} // namespace optionalpha
