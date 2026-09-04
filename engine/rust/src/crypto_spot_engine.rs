/*!
 * engine/rust/src/crypto_spot_engine.rs
 * =====================================
 * Module BQ: 24/7 Crypto Spot Trading & Arbitrage Engine
 *
 * Implements 64-byte #[repr(C, align(64))] zero-bridge memory layout for SIMD
 * orderbook imbalance and cross-rate triangular arbitrage.
 */

#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct CryptoSpotState {
    pub spot_price: f64,
    pub bid_depth_usd: f64,
    pub ask_depth_usd: f64,
    pub order_book_imbalance: f64,
    pub triangular_arb_spread: f64,
    pub non_marginable_buying_power: f64,
    pub asset_pair_id: u32,
    pub max_notional_k: u16,
    pub is_tradable: u8,
    pub is_fractionable: u8,
    pub fee_bps: u16,
    pub status_flags: u16,
    pub _padding: [u8; 4],
}

impl CryptoSpotState {
    pub fn new(spot: f64, cash: f64, pair_id: u32) -> Self {
        Self {
            spot_price: spot,
            bid_depth_usd: spot * 5.0,
            ask_depth_usd: spot * 5.0,
            order_book_imbalance: 0.0,
            triangular_arb_spread: 0.0,
            non_marginable_buying_power: cash,
            asset_pair_id: pair_id,
            max_notional_k: 200,
            is_tradable: 1,
            is_fractionable: 1,
            fee_bps: 25,
            status_flags: 1,
            _padding: [0; 4],
        }
    }

    pub fn compute_obi(&mut self, bid_vol: f64, ask_vol: f64) -> f64 {
        let total = bid_vol + ask_vol;
        if total <= 0.0001 {
            self.order_book_imbalance = 0.0;
        } else {
            self.order_book_imbalance = (bid_vol - ask_vol) / total;
        }
        self.order_book_imbalance
    }

    pub fn compute_triangular_arbitrage(&mut self, btc_usd: f64, eth_btc: f64, eth_usd: f64) -> f64 {
        let synthetic_eth_usd = eth_btc * btc_usd;
        if eth_usd <= 0.0001 {
            return 0.0;
        }
        let discrepancy = (eth_usd - synthetic_eth_usd) / eth_usd;
        self.triangular_arb_spread = discrepancy;
        if discrepancy.abs() > 0.0050 {
            self.status_flags |= 2;
        }
        discrepancy
    }
}
