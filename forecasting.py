"""
forecasting.py
Three forecasting approaches on India CPI month-over-month % change,
evaluated on a chronological (never shuffled) train/test split.

NOTE ON THIS SANDBOX: statsmodels, prophet, and xgboost are not installed
here (no internet access in this environment to pip install them). The
ARIMA / Prophet / XGBoost functions below are written correctly against
their real APIs and are meant to run on your machine via
`pip install -r requirements.txt`. The `linear_ar_benchmark` function uses
only sklearn (confirmed available) and IS fully tested in this sandbox --
run this file directly to see it work end-to-end on your real data.
"""

import numpy as np
import pandas as pd
from data_loader import load_cpi_series, add_pct_change, add_lag_features, chronological_split
from evaluation import evaluate_all


# ---------------------------------------------------------------------------
# TESTED BENCHMARK: Linear autoregression via sklearn (works in any env)
# ---------------------------------------------------------------------------
def linear_ar_benchmark(train: pd.Series, test: pd.Series, n_lags: int = 6):
    """A simple, honest baseline: predict next month's % change as a linear
    combination of the last n_lags months. This is essentially an AR(p)
    model fit by least squares instead of MLE -- not as principled as
    statsmodels' ARIMA, but a real, working, testable model with zero
    exotic dependencies. Good sanity-check baseline: if ARIMA/XGBoost can't
    beat this, they're not adding value.
    """
    from sklearn.linear_model import LinearRegression

    full = pd.concat([train, test])
    lagged = pd.DataFrame({f"lag_{i}": full.shift(i) for i in range(1, n_lags + 1)})
    lagged["target"] = full
    lagged = lagged.dropna()

    train_end = train.index[-1]
    train_rows = lagged.loc[:train_end]
    test_rows = lagged.loc[test.index[0]:]

    X_train, y_train = train_rows.drop(columns="target"), train_rows["target"]
    X_test, y_test = test_rows.drop(columns="target"), test_rows["target"]

    model = LinearRegression()
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    return preds, y_test.values, model


# ---------------------------------------------------------------------------
# REAL MODEL 1: ARIMA (requires statsmodels -- run on your machine)
# ---------------------------------------------------------------------------
def arima_forecast(train: pd.Series, test: pd.Series, order=(2, 0, 2)):
    """
    Classical ARIMA on the % change series (already close to stationary,
    so d=0 is often right here -- verify with ADF test on your own run
    before trusting this default; see the stationarity lesson).

    order=(p,d,q):
      p = number of autoregressive (lag) terms -- read off PACF cutoff
      d = differencing order -- 0 here since we're already using % change
      q = number of moving-average terms -- read off ACF cutoff
    """
    from statsmodels.tsa.arima.model import ARIMA

    model = ARIMA(train, order=order)
    fitted = model.fit()
    preds = fitted.forecast(steps=len(test))
    return preds.values, test.values, fitted


# ---------------------------------------------------------------------------
# REAL MODEL 2: Prophet (requires prophet -- run on your machine)
# ---------------------------------------------------------------------------
def prophet_forecast(train: pd.Series, test: pd.Series):
    """
    Facebook/Meta Prophet: decomposes the series into trend + seasonality
    + residual. Good at capturing yearly seasonal patterns (e.g. festival-
    season food price spikes) automatically, less good at short, sharp
    shocks compared to ARIMA.
    """
    from prophet import Prophet

    train_df = train.reset_index()
    train_df.columns = ["ds", "y"]

    model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    model.fit(train_df)

    future = pd.DataFrame({"ds": test.index})
    forecast = model.predict(future)
    preds = forecast["yhat"].values
    return preds, test.values, model


# ---------------------------------------------------------------------------
# REAL MODEL 3: XGBoost (requires xgboost -- run on your machine)
# ---------------------------------------------------------------------------
def xgboost_forecast(train: pd.Series, test: pd.Series, n_lags: int = 6):
    """
    Gradient-boosted trees on lag features. Turns the forecasting problem
    into ordinary supervised learning: predict month t's % change from
    months t-1 ... t-n_lags. Captures nonlinear relationships ARIMA can't,
    but has no built-in notion of trend/seasonality -- lag features have
    to carry all of that information.
    """
    from xgboost import XGBRegressor

    full = pd.concat([train, test])
    lagged = pd.DataFrame({f"lag_{i}": full.shift(i) for i in range(1, n_lags + 1)})
    lagged["target"] = full
    lagged = lagged.dropna()

    train_end = train.index[-1]
    train_rows = lagged.loc[:train_end]
    test_rows = lagged.loc[test.index[0]:]

    X_train, y_train = train_rows.drop(columns="target"), train_rows["target"]
    X_test, y_test = test_rows.drop(columns="target"), test_rows["target"]

    model = XGBRegressor(n_estimators=200, max_depth=3, learning_rate=0.05, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    return preds, y_test.values, model


if __name__ == "__main__":
    df = add_pct_change(load_cpi_series())
    series = df["cpi_pct_change"].dropna()

    train, test = chronological_split(series.to_frame("v"), test_months=12)
    train, test = train["v"], test["v"]

    print(f"Train: {len(train)} months, Test: {len(test)} months\n")

    print("=" * 60)
    print("TESTED: Linear AR benchmark (sklearn -- runs in any environment)")
    print("=" * 60)
    preds, actual, _ = linear_ar_benchmark(train, test, n_lags=6)
    print("Predicted vs Actual (last 5 months of test set):")
    for p, a in zip(preds[-5:], actual[-5:]):
        print(f"  predicted {p:+.3f}%   actual {a:+.3f}%")
    print("\nMetrics:", evaluate_all(actual, preds))

    print("\n" + "=" * 60)
    print("ARIMA / Prophet / XGBoost: written and ready, but require")
    print("statsmodels / prophet / xgboost -- install and run on your")
    print("machine with: pip install -r requirements.txt")
    print("=" * 60)
