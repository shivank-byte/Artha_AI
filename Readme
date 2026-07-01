# AI Inflation Advisor — Phase 2: The Forecaster

A forecasting engine for India's Consumer Price Index (CPI), comparing classical
statistical, additive, and machine learning approaches on real government data.

Data: All-India Combined General CPI, Base 2012=100, Jan 2013 – Mar 2025 (147 months).
Source: MoSPI/NSO official press release (Annexure-V, Time Series Data for All India
General CPI).

## What this does

- Loads and cleans the raw CPI index series
- Transforms it into month-over-month % change (the series actually used for modeling —
  the raw index trends upward and isn't stationary)
- Splits data chronologically into train/test (no shuffling — that would leak future
  information into training)
- Runs and compares four forecasting approaches:
  - **Linear AR** — autoregression via least squares (sklearn)
  - **ARIMA** — classical time-series forecasting (statsmodels)
  - **Prophet** — trend + seasonality decomposition (Meta's Prophet)
  - **XGBoost** — gradient-boosted trees on lag features
- Evaluates each with MAE, RMSE, and MAPE
- Visualizes everything in an interactive Streamlit dashboard

## Project structure

```
ai-inflation-advisor/
├── data/
│   └── india_cpi_2013_2025.csv
├── src/
│   ├── data_loader.py     # loading, % change transform, train/test split
│   ├── evaluation.py      # MAE / RMSE / MAPE metrics
│   ├── forecasting.py     # the four forecasting models
│   └── app.py              # Streamlit dashboard
├── requirements.txt
└── README.md
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
# Run the forecasting pipeline directly (terminal output)
python3 src/forecasting.py

# Launch the full dashboard
streamlit run src/app.py
```

## Notes

- ARIMA's default order `(2,0,2)` is a reasonable starting point for the % change
  series but should be tuned per-dataset using ACF/PACF plots and an ADF stationarity
  test rather than trusted blindly.
- MAPE can be misleading when actual values are near zero, which happens with
  month-over-month inflation data — cross-check against MAE/RMSE.
- 147 months is a workable sample size for CPI forecasting, but treat model
  comparisons as directional rather than definitive, especially with a short
  test window.

## Roadmap

- [x] Data pipeline on real MoSPI CPI data
- [x] Forecasting engine (AR, ARIMA, Prophet, XGBoost)
- [x] Streamlit dashboard
- [ ] RAG pipeline over RBI monetary policy documents
- [ ] LangChain agent to generate plain-language, policy-grounded forecast explanations
- [ ] Anti-hallucination guardrails on LLM output
- [ ] Deployment

## Stack

Python · pandas · scikit-learn · statsmodels · Prophet · XGBoost · Streamlit · Plotly
