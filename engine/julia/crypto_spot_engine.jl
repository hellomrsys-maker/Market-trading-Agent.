# Module BQ: 24/7 Crypto Spot Engine (Julia Tier)
# Cross-Rate Synthetic Arbitrage & Order Book Microstructure Solver

struct CryptoSpotState
    spot_price::Float64
    bid_depth_usd::Float64
    ask_depth_usd::Float64
    order_book_imbalance::Float64
    triangular_arb_spread::Float64
    non_marginable_buying_power::Float64
    asset_pair_id::UInt32
    max_notional_k::UInt16
    is_tradable::UInt8
    is_fractionable::UInt8
    fee_bps::UInt16
    status_flags::UInt16
end

function compute_order_book_imbalance(bid_vol::Float64, ask_vol::Float64)::Float64
    total = bid_vol + ask_vol
    if total <= 1e-4
        return 0.0
    end
    return (bid_vol - ask_vol) / total
end

function evaluate_triangular_arbitrage(btc_usd::Float64, eth_btc::Float64, eth_usd::Float64)::Float64
    synthetic_eth_usd = eth_btc * btc_usd
    if eth_usd <= 1e-4
        return 0.0
    end
    return (eth_usd - synthetic_eth_usd) / eth_usd
end
