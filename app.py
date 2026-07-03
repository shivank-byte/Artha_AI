"""
app.py
Streamlit dashboard for the AI Inflation Advisor -- Phase 2 (The Forecaster).
Run with: streamlit run src/app.py

This wraps forecasting.py's models. Kept separate from forecasting.py
deliberately -- forecasting logic must be testable and importable without
spinning up a UI (see docx/SmartCalc-style logic/interface separation
principle from your other projects).
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from data_loader import load_cpi_series, add_pct_change, chronological_split
from forecasting import linear_ar_benchmark, arima_forecast, prophet_forecast, xgboost_forecast
from evaluation import evaluate_all
import theme

st.set_page_config(page_title="AI Inflation Advisor", page_icon="₹", layout="wide")
theme.inject_theme()

st.title("₹ AI Inflation Advisor")
st.caption("India CPI (General, Base 2012=100) · Source: MoSPI/NSO · Jan 2013 – Mar 2025")

# ---------------------------------------------------------------------------
# Load & prep data
# ---------------------------------------------------------------------------
df = add_pct_change(load_cpi_series())

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("CPI Index Level (Raw)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["cpi"], mode="lines", name="CPI"))
    fig.update_layout(height=350, margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Snapshot")
    latest = df.iloc[-1]
    st.metric("Latest CPI Index", f"{latest['cpi']:.2f}")
    st.metric("Latest Monthly Change", f"{latest['cpi_pct_change']:+.2f}%")
    st.metric("Mean Monthly Change (full history)", f"{df['cpi_pct_change'].mean():+.3f}%")

st.subheader("Month-over-Month % Change")
st.caption("This is the series the forecasting models are actually trained on -- "
           "the raw index trends upward and isn't stationary; % change is much closer to it.")
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df.index, y=df["cpi_pct_change"], mode="lines", name="% change"))
fig2.add_hline(y=0, line_dash="dot", line_color="gray")
fig2.update_layout(height=300, margin=dict(t=20, b=20))
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Forecasting comparison
# ---------------------------------------------------------------------------
st.subheader("Model Comparison — Forecast vs. Held-Out Actuals")
st.caption("Test set = last 12 months, never seen during training. Chronological split -- no shuffling.")

test_months = st.slider("Test set size (months)", 6, 24, 12)

series = df["cpi_pct_change"].dropna()
train, test = chronological_split(series.to_frame("v"), test_months=test_months)
train, test = train["v"], test["v"]

models_to_run = st.multiselect(
    "Models to run",
    ["Linear AR (benchmark)", "ARIMA", "Prophet", "XGBoost"],
    default=["Linear AR (benchmark)"],
    help="ARIMA / Prophet / XGBoost require their packages installed (see requirements.txt).",
)

results = {}
errors = {}

if "Linear AR (benchmark)" in models_to_run:
    preds, actual, _ = linear_ar_benchmark(train, test)
    results["Linear AR"] = (preds, actual)

if "ARIMA" in models_to_run:
    try:
        preds, actual, _ = arima_forecast(train, test)
        results["ARIMA"] = (preds, actual)
    except ImportError:
        errors["ARIMA"] = "statsmodels not installed -- run `pip install statsmodels`"

if "Prophet" in models_to_run:
    try:
        preds, actual, _ = prophet_forecast(train, test)
        results["Prophet"] = (preds, actual)
    except ImportError:
        errors["Prophet"] = "prophet not installed -- run `pip install prophet`"

if "XGBoost" in models_to_run:
    try:
        preds, actual, _ = xgboost_forecast(train, test)
        results["XGBoost"] = (preds, actual)
    except ImportError:
        errors["XGBoost"] = "xgboost not installed -- run `pip install xgboost`"

for name, msg in errors.items():
    st.warning(f"{name}: {msg}")

if results:
    metrics_table = []
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=test.index, y=test.values, mode="lines+markers", name="Actual", line=dict(color="black", width=3)))

    for name, (preds, actual) in results.items():
        m = evaluate_all(actual, preds)
        metrics_table.append({"Model": name, **m})
        fig3.add_trace(go.Scatter(x=test.index, y=preds, mode="lines+markers", name=name))

    fig3.update_layout(height=400, margin=dict(t=20, b=20))
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Accuracy Metrics")
    st.dataframe(pd.DataFrame(metrics_table).set_index("Model"), use_container_width=True)
    st.caption("MAPE can be misleading when actual values are near zero (common in month-over-month "
               "inflation data) -- cross-check against MAE/RMSE, don't trust MAPE alone.")
else:
    st.info("Select at least one model above to see results.")

st.divider()
st.caption(
    "Phase 2 (\"The Forecaster\") — four models compared on real MoSPI CPI data. "
    "Phase 3 (\"The Advisor\") — RAG-grounded LLM explanations — is live below."
)

# ---------------------------------------------------------------------------
# Phase 3: AI Advisor - ask a question, grounded in RBI policy + the forecast
# ---------------------------------------------------------------------------
st.divider()
st.markdown(theme.advisor_header_html(), unsafe_allow_html=True)
st.caption("Answers are grounded in the forecast above and real RBI policy statements "
           "(Apr & Jun 2026 reviews) — not generated freely by the model.")

user_question = st.text_input(
    "Ask about the inflation outlook",
    placeholder="e.g. Why might inflation be rising, and what is the RBI's official forecast?",
)

if st.button("Ask", type="primary") and user_question:
    with st.spinner("Running forecast, retrieving RBI context, and generating explanation..."):
        try:
            from agent import run_advisor
            answer, report, retrieval_mode = run_advisor(user_question)
            st.success(answer)

            mode_label = "🧠 Semantic retrieval" if retrieval_mode == "semantic" else "🔤 Keyword (TF-IDF) retrieval"
            badges = theme.chip_html(mode_label)

            if report.overall_flag == "grounded":
                badges += " " + theme.chip_html(
                    f"✓ Grounded — overlap {report.semantic_overlap_score}", "good")
            elif report.overall_flag == "review":
                badges += " " + theme.chip_html(
                    f"⚠ Review — overlap {report.semantic_overlap_score}", "warn")
            else:
                badges += " " + theme.chip_html(
                    f"⚠ Ungrounded — check: {report.ungrounded_numbers}", "warn")

            st.markdown(badges, unsafe_allow_html=True)
        except Exception as e:
            st.error(
                f"Could not get an answer: {e}\n\n"
                "Make sure GEMINI_API_KEY is set in this app's Secrets "
                "(App settings → Secrets)."
            )
