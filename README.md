# San Diego Medicare Plans 2026 — Streamlit Starter

Ready-to-deploy comparison tool for licensed agents.

## What's included

- `app.py` — Streamlit app with filters + table + side-by-side comparison
- `2026_San_Diego_Medicare_Plans_CLEANED.xlsx` — cleaned data
- `requirements.txt` — dependencies

## Run locally

```bash
cd medicare_streamlit_starter
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Railway

1. Create a GitHub repo and upload this folder
2. Go to https://railway.app → New Project → Deploy from GitHub
3. Select the repo
4. Railway will detect Python and install from `requirements.txt`
5. Add a start command if needed: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

(Most Railway Streamlit templates detect this automatically.)

## Features in this starter

- Filter by Carrier, Plan Type, Premium type ($0 / Rebate / Paid)
- Free-text search
- Option to show only flagged plans (Cancelled / Non-Commissionable / Crosswalk)
- Main table of key benefits
- Multi-select 2–4 plans for side-by-side comparison

## Next steps you can add later

- Login / password protection
- Stripe payments (e.g. with st-paywall)
- More benefit columns or custom scoring
- Export comparison to Excel/PDF
