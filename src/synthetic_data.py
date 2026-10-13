import numpy as np
import pandas as pd


def make_synthetic_monthly_data(seed: int = 7) -> pd.DataFrame:
    """Return synthetic monthly volume and revenue for demo/testing only."""
    rng = np.random.default_rng(seed)
    months = pd.date_range("2024-01-01", periods=18, freq="MS")
    customers = ["C_STABLE", "C_DECLINE", "C_GROWTH", "C_NEW", "C_SEASONAL"]
    rows = []

    for customer in customers:
        for idx, month in enumerate(months):
            if customer == "C_STABLE":
                volume = 100 + rng.normal(0, 5)
            elif customer == "C_DECLINE":
                volume = (120 if idx < 12 else 65) + rng.normal(0, 4)
            elif customer == "C_GROWTH":
                volume = 70 + idx * 4 + rng.normal(0, 5)
            elif customer == "C_NEW":
                if idx < 15:
                    continue
                volume = 35 + rng.normal(0, 3)
            else:  # deliberately seasonal pattern, to expose a baseline limitation
                volume = (45 if month.month in [1, 2, 3] else 115) + rng.normal(0, 5)

            volume = max(0.0, float(volume))
            # Synthetic unit price only; not a Volz price adjustment.
            unit_price = 10.0 + 0.2 * idx
            rows.append({
                "customer_id": customer,
                "month": month,
                "real_volume": volume,
                "revenue_eur": volume * unit_price,
            })

    return pd.DataFrame(rows).sort_values(["customer_id", "month"]).reset_index(drop=True)
