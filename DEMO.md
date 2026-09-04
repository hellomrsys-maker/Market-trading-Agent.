# OptionAlpha Agent — Quick Evaluation & Demo Guide

> A 5-minute evaluation guide for hackathon judges to verify and test OptionAlpha.

---

## ⚡ Option 1: Instant 60-Second Simulated Demo (Zero Setup Required)

Run the automated full-day simulation:

```powershell
# From project root:
python scripts/demo_mode.py
```

This runs an accelerated simulation through all 4 market periods:
1. **09:40 ET:** Macro regime classification (285K Transformer)
2. **10:30 ET:** Candidate scoring & order submission (Wheel CSP + Iron Condor)
3. **14:00 ET:** Greeks tracking & 50% profit-taking trigger
4. **15:45 ET:** Daily reconciliation & Markdown P&L report generation

---

## 📊 Option 2: Live Web Dashboard & Local Server

Launch the web dashboard to see real-time charts and metrics:

```powershell
python run_agent.py --dashboard-only
```
- Open browser at: **`http://127.0.0.1:8080`**
- API Documentation: **`http://127.0.0.1:8080/api/docs`**

---

## 📈 Option 3: Strategy Backtesting & Quantitative Verification

Execute the event-driven backtesting engine over historical bars:

```powershell
# 30-day quick validation:
python -m backtest.run_backtest --smoke-test

# Full 2-year (504 trading days) simulation:
python -m backtest.run_backtest --days 504 --symbols SPY QQQ NVDA AAPL MSFT
```

Reports are automatically generated and saved to `data/backtest/backtest_summary.md`.

---

## 🧪 Option 4: Full Automated Unit Test Suite

Run the complete test suite:

```powershell
python -m pytest tests/ -v --tb=short
```

**39/39 passing unit tests** covering:
- Feature matrix calculations & sliding sequence generators
- Trade episodic memory, win rates, and JSON persistence
- 6-tier circuit breaker logic and position sizing
- Regime Transformer forward pass & auto-labeling

---

## 🚀 Option 5: Live Paper Trading on Alpaca

To run live against your Alpaca Paper Trading account:

1. Configure `.env` with your API keys:
   ```env
   ALPACA_API_KEY=PKxxxxxxxxxxxxxxxxxxxx
   ALPACA_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ALPACA_BASE_URL=https://paper-api.alpaca.markets
   ```
2. Start the autonomous agent scheduler:
   ```powershell
   python run_agent.py
   ```
