"""
Module BN1: Multi-Asset Cross-Market Liquidity and PDT Governor Engine
Synthesized from Matthew Gray's 'Options Trading For Beginners'.
"""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class CrossMarketPdtState:
    account_equity: float
    margin_borrowed: float
    forex_leverage_ratio: float
    futures_tick_value: float
    max_risk_per_trade: float
    current_drawdown_pct: float
    round_trips_5d: int
    asset_class_id: int
    pdt_restricted: bool
    circuit_breaker_tripped: bool

class CrossMarketPdtEngine:
    def __init__(self, pdt_equity_threshold: float = 25000.0, max_pdt_trips: int = 3):
        self.pdt_threshold = pdt_equity_threshold
        self.max_trips = max_pdt_trips

    def audit_trade_compliance(self, state: CrossMarketPdtState, is_day_trade: bool, proposed_risk: float) -> Dict[str, Any]:
        risk_limit = state.account_equity * 0.05
        approved = True
        reason = 'APPROVED'
        
        if state.current_drawdown_pct >= 0.10:
            state.circuit_breaker_tripped = True
            return {'approved': False, 'reason': 'CIRCUIT_BREAKER_MAX_DRAWDOWN'}
            
        if proposed_risk > risk_limit:
            return {'approved': False, 'reason': f'RISK_EXCEEDS_5_PCT_CAP (${risk_limit:.2f})'}
            
        if state.account_equity < self.pdt_threshold and is_day_trade:
            if state.round_trips_5d >= self.max_trips:
                state.pdt_restricted = True
                return {'approved': False, 'reason': 'SEC_PDT_RULE_VIOLATION_SUB_25K'}
            state.round_trips_5d += 1
            
        return {'approved': approved, 'reason': reason, 'state': state}
