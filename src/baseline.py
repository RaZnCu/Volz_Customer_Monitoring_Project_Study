import pandas as pd


def score_customers(
    monthly_data: pd.DataFrame,
    cutoff_date: str | pd.Timestamp,
    recent_months: int = 3,
    baseline_months: int = 12,
    minimum_history_months: int = 12,
    minimum_baseline_volume: float = 0.0,
) -> pd.DataFrame:
    """
    Score customers using a provisional, explainable rule.

    Recent period: the `recent_months` calendar months ending at cutoff_date.
    Baseline period: the `baseline_months` calendar months immediately before
    the recent period. This avoids overlap between baseline and recent windows.

    exposure_proxy_eur is a rough prioritisation proxy based on baseline-period
    average monthly invoiced revenue and the observed relative volume decline.
    It is NOT a validated estimate of future loss.
    """
    required = {"customer_id", "month", "real_volume", "revenue_eur"}
    missing = required - set(monthly_data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    data = monthly_data.copy()
    data["month"] = pd.to_datetime(data["month"]).dt.to_period("M").dt.to_timestamp()
    cutoff = pd.Timestamp(cutoff_date).to_period("M").to_timestamp()

    if recent_months <= 0 or baseline_months <= 0 or minimum_history_months <= 0:
        raise ValueError("Window lengths must be positive integers.")
    if data.duplicated(["customer_id", "month"]).any():
        raise ValueError("Expected one row per customer per month.")
    if (data[["real_volume", "revenue_eur"]].dropna() < 0).any().any():
        raise ValueError("Volume and revenue must be non-negative.")
    if data["month"].gt(cutoff).any():
        raise ValueError("Input contains observations after the cutoff date.")

    recent_start = cutoff - pd.DateOffset(months=recent_months - 1)
    baseline_end = recent_start - pd.DateOffset(months=1)
    baseline_start = baseline_end - pd.DateOffset(months=baseline_months - 1)

    baseline = data[data["month"].between(baseline_start, baseline_end)]
    recent = data[data["month"].between(recent_start, cutoff)]

    rows = []
    for customer_id, hist in data.groupby("customer_id"):
        base = baseline[baseline["customer_id"] == customer_id]
        rec = recent[recent["customer_id"] == customer_id]

        # Count observed months; sparse/intermittent customers need separate review.
        history_months = hist["month"].nunique()
        base_months_observed = base["month"].nunique()
        recent_months_observed = rec["month"].nunique()

        if (
            history_months < minimum_history_months
            or base_months_observed < baseline_months
            or recent_months_observed < recent_months
        ):
            rows.append({
                "customer_id": customer_id,
                "baseline_avg_monthly_volume": float("nan"),
                "recent_avg_monthly_volume": float("nan"),
                "decline_ratio": float("nan"),
                "exposure_proxy_eur": float("nan"),
                "status": "insufficient_month_coverage",
                "reason": "Insufficient complete monthly coverage for chosen windows",
            })
            continue

        baseline_avg_volume = float(base["real_volume"].mean())
        recent_avg_volume = float(rec["real_volume"].mean())
        baseline_avg_revenue = float(base["revenue_eur"].mean())

        if baseline_avg_volume <= minimum_baseline_volume:
            decline_ratio = float("nan")
            exposure = float("nan")
            status = "not_scored_zero_or_tiny_baseline"
            reason = "Baseline volume is zero or below configured minimum"
        else:
            decline_ratio = max(0.0, 1.0 - recent_avg_volume / baseline_avg_volume)
            exposure = baseline_avg_revenue * recent_months * decline_ratio
            status = "scored"
            reason = (
                f"Recent {recent_months}-month average volume is "
                f"{decline_ratio:.0%} below the preceding baseline average"
                if decline_ratio > 0 else
                "No decline versus the preceding baseline average"
            )

        rows.append({
            "customer_id": customer_id,
            "baseline_avg_monthly_volume": baseline_avg_volume,
            "recent_avg_monthly_volume": recent_avg_volume,
            "decline_ratio": decline_ratio,
            "exposure_proxy_eur": exposure,
            "status": status,
            "reason": reason,
        })

    result = pd.DataFrame(rows)
    result["rank"] = pd.NA
    eligible = result["status"].eq("scored")
    ranked = result.loc[eligible].sort_values(
        ["exposure_proxy_eur", "decline_ratio"], ascending=False
    )
    result.loc[ranked.index, "rank"] = range(1, len(ranked) + 1)
    return result.sort_values(
        ["status", "rank"], ascending=[True, True], na_position="last"
    ).reset_index(drop=True)
