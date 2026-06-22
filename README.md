# Mutual Fund Analysis Project

This repository contains the data and initial analysis for a comprehensive study of Mutual Funds, focusing on historical NAVs, SIP inflows, fund performance, portfolio holdings, and investor transactions.

## 📂 Project Structure

```text
mutual-fund-analysis/
├── data/
│   ├── raw/                  # Raw CSV datasets and fetched API data
│   └── processed/            # Cleaned and transformed datasets (to be generated)
├── notebooks/                # Jupyter notebooks for EDA and modeling
├── sql/                      # SQL scripts for database querying and analysis
├── dashboard/                # Code for interactive dashboards (e.g., Streamlit, Plotly Dash)
├── reports/                  # Generated analysis reports and data quality summaries
├── data_analysis.py          # Script for initial data loading, validation, and API fetching
├── requirements.txt          # Python dependencies
└── README.md                 # Project overview and setup instructions
```

## 🛠️ Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd mutual-fund-analysis
   ```

2. **Set up a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 📊 Datasets Available (`data/raw/`)

- `01_fund_master.csv`: Metadata for 40 key mutual funds across 10 fund houses.
- `02_nav_history.csv`: Historical Daily NAV data (~46,000 records) corresponding to the funds in the master list.
- `03_aum_by_fund_house.csv`: Assets Under Management (AUM) aggregated by fund house.
- `04_monthly_sip_inflows.csv`: Monthly SIP inflow amounts and active SIP accounts.
- `05_category_inflows.csv`: Net inflows categorized by fund type (Large Cap, Mid Cap, etc.).
- `06_industry_folio_count.csv`: Overall mutual fund folio counts by category (Equity, Debt, Hybrid).
- `07_scheme_performance.csv`: Performance metrics (1yr, 3yr, 5yr returns, Sharpe ratio, Alpha, Beta).
- `08_investor_transactions.csv`: Sample transactions of mutual fund investors.
- `09_portfolio_holdings.csv`: Detailed stock holdings and weightages for the funds.
- `10_benchmark_indices.csv`: Historical data for benchmark indices (e.g., NIFTY 50, NIFTY 100).

**Live API Data:**
The `data_analysis.py` script automatically fetches live NAV data for 6 specific Bluechip/Large Cap schemes from the `mfapi.in` API and saves them in `data/raw/`.

## 📈 Initial Analysis & Data Quality

An initial data quality check was performed (see `reports/data_quality_summary.md` and `reports/data_quality_summary.json` for details):
- All 40 funds in the `01_fund_master.csv` correctly map to historical data in the `02_nav_history.csv`. 
- No orphaned AMFI codes were found.
- Handled anomalies such as expected `NaN` values for initial Year-over-Year (YoY) growth calculations in SIP data.
