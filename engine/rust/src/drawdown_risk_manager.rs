// engine/rust/src/drawdown_risk_manager.rs
// OptionAlpha Agent — Module T_sys4: Rust Drawdown Risk Manager Engine

pub struct DrawdownRiskManagerRust {
    pub current_capital: f64,
    pub peak_equity: f64,
    pub max_dd_cutoff_pct: f64,
    pub consecutive_losses: usize,
}

impl DrawdownRiskManagerRust {
    pub fn new(initial_capital: f64, max_dd_cutoff_pct: f64) -> Self {
        Self {
            current_capital: initial_capital,
            peak_equity: initial_capital,
            max_dd_cutoff_pct,
            consecutive_losses: 0,
        }
    }

    pub fn position_size(&self, risk_pct: f64, max_loss_per_contract: f64) -> usize {
        let max_dollar_risk = self.current_capital * (risk_pct / 100.0);
        if max_loss_per_contract <= 0.0 { return 1; }
        (max_dollar_risk / max_loss_per_contract).floor().max(1.0) as usize
    }

    pub fn update_trade(&mut self, pnl: f64) -> (f64, f64, bool) {
        self.current_capital += pnl;
        if self.current_capital > self.peak_equity {
            self.peak_equity = self.current_capital;
        }

        if pnl < 0.0 {
            self.consecutive_losses += 1;
        } else {
            self.consecutive_losses = 0;
        }

        let dollar_dd = self.peak_equity - self.current_capital;
        let pct_dd = if self.peak_equity > 0.0 { (dollar_dd / self.peak_equity) * 100.0 } else { 0.0 };
        let is_halted = (pct_dd >= self.max_dd_cutoff_pct) || (self.consecutive_losses >= 6);

        (self.current_capital, pct_dd, is_halted)
    }
}
