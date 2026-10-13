from pathlib import Path

from src.baseline import score_customers
from src.synthetic_data import make_synthetic_monthly_data


def main() -> None:
    data = make_synthetic_monthly_data()
    cutoff = data["month"].max()
    results = score_customers(data, cutoff_date=cutoff)

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "baseline_ranked.csv"
    results.to_csv(output_path, index=False)

    print(f"Cutoff date: {cutoff:%Y-%m-%d}")
    print(f"Saved: {output_path}")
    print(results.to_string(index=False))


if __name__ == "__main__":
    main()
