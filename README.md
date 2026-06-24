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

## 📅 Project Log

### Day 01: Environment Setup & Data Ingestion
- **Environment Creation:** Built the foundational folder structure (`data/raw`, `notebooks`, `sql`, `reports`, etc.).
- **Version Control:** Initialized the Git repository to track project progress.
- **Dependencies:** Created `requirements.txt` and installed all necessary Python libraries (`pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`, `sqlalchemy`, `requests`, `scipy`, `jupyter`).
- **Data Loading & Profiling:** Loaded the 10 core CSV datasets using Pandas, printing their shapes, column data types, and initial rows to understand the structure. Handled anomalies (e.g., expected `NaN`s in early YoY SIP calculations).
- **Live API Integration:** Built a robust script (`data_analysis.py`) to connect to the `mfapi.in` API. Fetched and saved raw historical NAV data for 6 benchmark funds: HDFC Top 100, SBI Bluechip, ICICI Bluechip, Nippon Large Cap, Axis Bluechip, and Kotak Bluechip.
- **Data Validation:** Parsed `01_fund_master.csv` to map out the 10 unique fund houses and AMFI code structures. Validated that all 40 tracked funds possess corresponding data within the `02_nav_history.csv` dataset, confirming 100% referential integrity.
