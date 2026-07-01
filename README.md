# AI Inflation Advisor — Phase 2: The Forecaster

Real India CPI data (MoSPI/NSO, Base 2012=100, Jan 2013 – Mar 2025, 147 months),
transcribed from the official government press release Annexure-V.

## What's here

- `data/india_cpi_2013_2025.csv` — the real time series
- `src/data_loader.py` — loading, % change transform, chronological train/test split
- `src/evaluation.py` — MAE / RMSE / MAPE metrics
- `src/forecasting.py` — 4 models:
  - **Linear AR benchmark** (sklearn) — tested and confirmed working end-to-end
  - **ARIMA** (statsmodels) — written, needs `pip install statsmodels` to run
  - **Prophet** (prophet) — written, needs `pip install prophet` to run
  - **XGBoost** (xgboost) — written, needs `pip install xgboost` to run
- `src/app.py` — Streamlit dashboard wrapping all of the above

## Honesty note on testing

This was built in a sandbox with **no internet access**, so `statsmodels`,
`prophet`, `xgboost`, and `streamlit` could not be installed or run here.

**What was actually tested, with real output, on your real data:**
- Data loading and the % change transform (147 months, verified)
- Chronological train/test split (134 train / 12 test, verified — the test
  months are the most recent 12, never shuffled in)
- The Linear AR benchmark — ran end-to-end, produced real forecasts,
  MAE ≈ 0.53 percentage points on held-out data

**What's written correctly but not run here:** ARIMA, Prophet, XGBoost, and
the Streamlit app. The code follows each library's real, current API — but
you should run it yourself and treat the first run as a debugging pass, not
assume it's flawless just because it looks right.

## How to run it yourself

```bash
cd ai-inflation-advisor
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Test the pipeline first (fast, no UI):
python3 src/forecasting.py

# Then launch the dashboard:
streamlit run src/app.py
```

## Known things to check on your first run

- ARIMA's `order=(2,0,2)` is a reasonable starting default for the % change
  series, but you should verify it against your own ADF test and ACF/PACF
  plots (see the stationarity lesson) rather than trust it blindly.
- Prophet expects `ds`/`y` column names — already handled in the code, but
  worth knowing if you extend it.
- 147 months is decent but not huge for CPI forecasting — treat model
  comparisons as directional, not gospel, especially with only a 12-month
  test window.

## Next steps (Phase 3+)

- RAG pipeline over RBI monetary policy documents
- LangChain tool-calling so an LLM can call these forecasting functions
  and explain results, grounded in retrieved policy context
- Guardrails against the LLM inventing numbers not backed by the forecast
