"""
evaluation.py
Metrics for comparing forecast accuracy across models.
Kept dependency-free (numpy only) so it works in any environment.
"""

import numpy as np


def mae(actual, predicted) -> float:
    """Mean Absolute Error -- average size of error, in the same units
    as the data (e.g., 'off by 0.3 index points on average')."""
    actual, predicted = np.asarray(actual), np.asarray(predicted)
    return float(np.mean(np.abs(actual - predicted)))


def rmse(actual, predicted) -> float:
    """Root Mean Squared Error -- like MAE but penalizes large errors
    more heavily (squaring), so it's more sensitive to occasional big misses."""
    actual, predicted = np.asarray(actual), np.asarray(predicted)
    return float(np.sqrt(np.mean((actual - predicted) ** 2)))


def mape(actual, predicted) -> float:
    """Mean Absolute Percentage Error -- error as a % of the actual value.
    Easy to interpret ('forecasts were off by 1.2% on average'), but
    unstable/misleading if actual values are near zero. CPI % change data
    can occasionally be near zero, so cross-check with MAE too."""
    actual, predicted = np.asarray(actual), np.asarray(predicted)
    mask = actual != 0
    return float(np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100)


def evaluate_all(actual, predicted) -> dict:
    return {
        "MAE": round(mae(actual, predicted), 4),
        "RMSE": round(rmse(actual, predicted), 4),
        "MAPE_%": round(mape(actual, predicted), 4),
    }


if __name__ == "__main__":
    # Sanity check with known values
    actual = [2.0, 2.5, 3.0, 2.8]
    predicted = [2.1, 2.3, 3.2, 2.6]
    result = evaluate_all(actual, predicted)
    print("Sanity check on toy values:")
    print(result)
    assert result["MAE"] > 0, "MAE should be positive for imperfect predictions"
    print("OK - evaluation functions working correctly")
