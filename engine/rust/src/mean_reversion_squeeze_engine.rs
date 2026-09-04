#[repr(C, align(64))]
#[derive(Debug, Clone, Copy)]
pub struct MeanReversionSqueezeState {
    pub pnr_threshold: f64,
    pub bollinger_upper: f64,
    pub bollinger_lower: f64,
    pub keltner_upper: f64,
    pub keltner_lower: f64,
    pub current_adx: f64,
    pub current_rsi: f32,
    pub current_atr: f32,
    pub dte: u16,
    pub is_squeeze_active: u8,
    pub is_pnr_breached: u8,
    pub dmi_bullish_cross: u8,
    pub dmi_bearish_cross: u8,
    pub cut_50pct_loss: u8,
    pub padding: [u8; 1],
}

pub struct MeanReversionSqueezeEngine;

impl MeanReversionSqueezeEngine {
    pub fn compute_pnr(
        long_strike: f64,
        short_strike: f64,
        dte: u16,
        atr: f32,
        current_price: f64
    ) -> MeanReversionSqueezeState {
        let pnr_offset = (long_strike * (dte as f64) * (atr as f64)) / 2000.0;
        let pnr_threshold = long_strike - pnr_offset;
        let is_pnr_breached = if current_price < pnr_threshold { 1 } else { 0 };
        let cut_50pct_loss = if is_pnr_breached == 1 && dte < 15 { 1 } else { 0 };

        MeanReversionSqueezeState {
            pnr_threshold,
            bollinger_upper: 0.0,
            bollinger_lower: 0.0,
            keltner_upper: 0.0,
            keltner_lower: 0.0,
            current_adx: 0.0,
            current_rsi: 50.0,
            current_atr: atr,
            dte,
            is_squeeze_active: 0,
            is_pnr_breached,
            dmi_bullish_cross: 0,
            dmi_bearish_cross: 0,
            cut_50pct_loss,
            padding: [0; 1],
        }
    }
}
