# Data Quality & Setup Summary

## 1. Project Structure
The following directories were successfully created:
- `data/raw/` (contains the 10 source datasets and the 6 fetched API datasets)
- `data/processed/`
- `notebooks/`
- `sql/`
- `dashboard/`
- `reports/`

## 2. Git & Dependencies
- `git` repository initialized.
- `requirements.txt` generated with all 9 requested packages.
- Dependencies successfully installed via pip.

*(Note: To push to GitHub, you will need to manually configure your remote repository using `git remote add origin <URL>` and `git push -u origin master`, as I do not have access to your GitHub credentials.)*

## 3. Dataset Exploration & Anomalies
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

## 4. API Data Fetching
Successfully queried `https://api.mfapi.in/mf/<code/>` and saved raw CSV files:
- **HDFC Top 100 Direct** (125497) -> `data/raw/HDFC_Top100_nav.csv` (3105 rows)
- **SBI Bluechip** (119551) -> `data/raw/SBI_Bluechip_nav.csv` (3250 rows)
- **ICICI Bluechip** (120503) -> `data/raw/ICICI_Bluechip_nav.csv` (3321 rows)
- **Nippon Large Cap** (118632) -> `data/raw/Nippon_LargeCap_nav.csv` (3312 rows)
- **Axis Bluechip** (119092) -> `data/raw/Axis_Bluechip_nav.csv` (3579 rows)
- **Kotak Bluechip** (120841) -> `data/raw/Kotak_Bluechip_nav.csv` (3315 rows)

## 5. Fund Master Exploration
- **Unique Fund Houses (10)**: SBI, HDFC, ICICI, Nippon, Kotak, Axis, Aditya Birla, UTI, Mirae Asset, DSP.
- **Unique Categories (2)**: Equity, Debt.
- **Unique Sub-Categories (12)**: Large Cap, Small Cap, Gilt, Mid Cap, Short Duration, Value, Liquid, Index/ETF, Flexi Cap, Index, Large & Mid Cap, ELSS.
- **Unique Risk Grades (5)**: Moderate, Very High, Low, High, Moderately High.
- **AMFI Scheme Code Structure**: It is an official 6-digit numerical identifier assigned by the Association of Mutual Funds in India (AMFI) to uniquely identify mutual fund schemes, their plans (e.g. Regular vs Direct), and their options (e.g. Growth vs IDCW).

## 6. AMFI Code Validation
Cross-referenced `01_fund_master.csv` with `02_nav_history.csv`.
- **Validation Status**: **PASS**
- **Summary**: All 40 unique `amfi_code` values present in the fund master table have corresponding daily NAV records in the `nav_history` dataset. No orphaned codes were detected.
