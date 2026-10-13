import pandas as pd
import pytest

from src.baseline import score_customers
from src.synthetic_data import make_synthetic_monthly_data


def test_synthetic_data_has_expected_columns():
    data = make_synthetic_monthly_data()
    assert {"customer_id", "month", "real_volume", "revenue_eur"} <= set(data.columns)


def test_declining_customer_is_scored_as_declining():
    data = make_synthetic_monthly_data()
    result = score_customers(data, cutoff_date=data["month"].max())
    row = result.loc[result["customer_id"] == "C_DECLINE"].iloc[0]
    assert row["status"] == "scored"
    assert row["decline_ratio"] > 0.2


def test_new_customer_is_not_scored_with_insufficient_history():
    data = make_synthetic_monthly_data()
    result = score_customers(data, cutoff_date=data["month"].max())
    row = result.loc[result["customer_id"] == "C_NEW"].iloc[0]
    assert row["status"] == "insufficient_month_coverage"


def test_duplicate_customer_month_is_rejected():
    data = make_synthetic_monthly_data()
    duplicated = pd.concat([data, data.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="one row per customer per month"):
        score_customers(duplicated, cutoff_date=data["month"].max())


def test_future_rows_after_cutoff_are_rejected():
    data = make_synthetic_monthly_data()
    with pytest.raises(ValueError, match="after the cutoff"):
        score_customers(data, cutoff_date="2024-12-01")
