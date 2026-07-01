"""
data_loader.py
Loads the All-India Combined General CPI series (Base 2012=100, MoSPI/NSO)
and prepares it for forecasting: % change transform, stationarity-friendly
train/test split (chronological, never shuffled).

Source: MoSPI Press Release Annexure-V, "Time Series Data for All India
General CPI (Base 2012=100) Since January 2013". Real government data,
transcribed by hand from the official PDF -- no synthetic values.
"""

import pandas as pd
import numpy as np
from pathlib import Path

FILENAME = "india_cpi_2013_2025.csv"


def _find_data_file() -> Path:
    """Locate the CPI CSV regardless of exact repo layout (handles both the
    intended src/ + data/ structure and a flattened single-folder layout,
    which can happen after uploading files via GitHub mobile)."""
    here = Path(__file__).parent
    candidates = [
        here.parent / "data" / FILENAME,   # intended layout: src/ + data/
        here / "data" / FILENAME,          # data/ alongside this file
        here / FILENAME,                   # flattened: everything in one folder
        here.parent / FILENAME,            # csv one level up
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError(
        f"Could not find {FILENAME}. Looked in: {[str(c) for c in candidates]}. "
        f"Make sure the CSV was uploaded to your repo."
    )


def load_cpi_series(path: Path = None) -> pd.DataFrame:
    """Load raw CPI level data, sorted chronologically, with a proper
    monthly DatetimeIndex (required by ARIMA/Prophet/most TS tooling)."""
    if path is None:
        path = _find_data_file()
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df = df.set_index("date")
    df.index.freq = "MS"  # explicit monthly-start frequency
    return df[["cpi"]]


def add_pct_change(df: pd.DataFrame) -> pd.DataFrame:
    """Add month-over-month % change column. This is the column most
    forecasting models should actually be trained on -- raw CPI level is
    non-stationary (trending), % change is much closer to stationary."""
    out = df.copy()
    out["cpi_pct_change"] = out["cpi"].pct_change() * 100
    return out


def add_lag_features(df: pd.DataFrame, target_col: str, n_lags: int = 6) -> pd.DataFrame:
    """Turn the time series into a supervised-learning table: each row gets
    columns for the previous n_lags values of target_col. Required for
    tree-based models (XGBoost) which have no native notion of 'time'."""
    out = df.copy()
    for lag in range(1, n_lags + 1):
        out[f"lag_{lag}"] = out[target_col].shift(lag)
    return out


def chronological_split(df: pd.DataFrame, test_months: int = 12):
    """Time-series-safe train/test split: the LAST `test_months` months
    become the test set. Never shuffle time series data -- shuffling would
    let the model 'see the future' during training via leakage."""
    train = df.iloc[:-test_months].copy()
    test = df.iloc[-test_months:].copy()
    return train, test


if __name__ == "__main__":
    df = load_cpi_series()
    df = add_pct_change(df)
    print(f"Loaded {len(df)} months: {df.index.min().date()} to {df.index.max().date()}")
    print(df.tail())

    train, test = chronological_split(df, test_months=12)
    print(f"\nTrain: {len(train)} months ({train.index.min().date()} to {train.index.max().date()})")
    print(f"Test:  {len(test)} months ({test.index.min().date()} to {test.index.max().date()})")
    
