# Mutual Fund Analysis Project Documentation

## 1. Overview
This repository contains the data and initial analysis for a comprehensive study of Mutual Funds, focusing on historical NAVs, SIP inflows, fund performance, portfolio holdings, and investor transactions.

## 2. Project Structure
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

## 3. Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/tharun-7733/BLUESTOCK.git
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

## 4. Datasets Available (`data/raw/`)

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

---

# Data Quality & Setup Summary

## 5. Dataset Exploration & Anomalies
All 10 provided datasets loaded successfully. Key observations:

1. **01_fund_master.csv** - `(40, 15)`: Clean, 40 distinct funds.
2. **02_nav_history.csv** - `(46000, 3)`: Large dataset containing historical NAVs.
3. **03_aum_by_fund_house.csv** - `(90, 5)`: Clean summary by fund house.
4. **04_monthly_sip_inflows.csv** - `(48, 6)`: **Anomaly Noted**: The `yoy_growth_pct` column contains `NaN` values for the earliest months, which is expected mathematically as there is no prior year data to compare against.
5. **05_category_inflows.csv** - `(144, 3)`: Standard category breakdown.
6. **06_industry_folio_count.csv** - `(21, 6)`: Summary of folios by type.
7. **07_scheme_performance.csv** - `(40, 19)`: Performance metrics aligning with the 40 funds.
8. **08_investor_transactions.csv** - `(32778, 13)`: Clean transaction logs.
9. **09_portfolio_holdings.csv** - `(322, 8)`: Distinct stock holdings mapped to AMFI codes.
10. **10_benchmark_indices.csv** - `(8050, 3)`: Time series index data.

## 6. API Data Fetching
Successfully queried `https://api.mfapi.in/mf/<code/>` and saved raw CSV files:
- **HDFC Top 100 Direct** (125497) -> `data/raw/HDFC_Top100_nav.csv` (3105 rows)
- **SBI Bluechip** (119551) -> `data/raw/SBI_Bluechip_nav.csv` (3250 rows)
- **ICICI Bluechip** (120503) -> `data/raw/ICICI_Bluechip_nav.csv` (3321 rows)
- **Nippon Large Cap** (118632) -> `data/raw/Nippon_LargeCap_nav.csv` (3312 rows)
- **Axis Bluechip** (119092) -> `data/raw/Axis_Bluechip_nav.csv` (3579 rows)
- **Kotak Bluechip** (120841) -> `data/raw/Kotak_Bluechip_nav.csv` (3315 rows)

## 7. Fund Master Exploration
- **Unique Fund Houses (10)**: SBI, HDFC, ICICI, Nippon, Kotak, Axis, Aditya Birla, UTI, Mirae Asset, DSP.
- **Unique Categories (2)**: Equity, Debt.
- **Unique Sub-Categories (12)**: Large Cap, Small Cap, Gilt, Mid Cap, Short Duration, Value, Liquid, Index/ETF, Flexi Cap, Index, Large & Mid Cap, ELSS.
- **Unique Risk Grades (5)**: Moderate, Very High, Low, High, Moderately High.
- **AMFI Scheme Code Structure**: It is an official 6-digit numerical identifier assigned by the Association of Mutual Funds in India (AMFI) to uniquely identify mutual fund schemes, their plans (e.g. Regular vs Direct), and their options (e.g. Growth vs IDCW).

## 8. AMFI Code Validation
Cross-referenced `01_fund_master.csv` with `02_nav_history.csv`.
- **Validation Status**: **PASS**
- **Summary**: All 40 unique `amfi_code` values present in the fund master table have corresponding daily NAV records in the `nav_history` dataset. No orphaned codes were detected.
