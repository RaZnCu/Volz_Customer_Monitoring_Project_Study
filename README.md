# Volz Customer Monitoring — Modelling Work Package v0.1

This scaffold uses **synthetic data only**. It is not a result about Volz's real customers.

## Setup (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m src.run_baseline
pytest -q
```

If PowerShell blocks activation, use Command Prompt:
```bat
.venv\Scripts\activate.bat
```

## What the baseline does

- Creates synthetic monthly customer volume observations.
- Compares each customer's latest 3 months with the previous 12 months.
- Ranks customers by a simple estimated exposure proxy.
- Exports `outputs/baseline_ranked.csv`.

The rule is provisional. Before using real data, the team must agree on:
1. The definition of real volume and the price adjustment method.
2. The baseline window and minimum history.
3. How seasonality, irregular orders, new customers, and replacement items are handled.
4. What “euros at risk” means and how it is calculated.

## Project structure

- `src/synthetic_data.py`: synthetic test data generator
- `src/baseline.py`: baseline rule
- `src/run_baseline.py`: run the end-to-end demo
- `tests/test_baseline.py`: basic unit tests
- `outputs/`: generated output (ignored by Git)

## Data protection

Do not commit Volz raw data, exports, customer identifiers, credentials, or other confidential information to a public or unapproved repository. Confirm the approved storage and access arrangements with the team/company first.
