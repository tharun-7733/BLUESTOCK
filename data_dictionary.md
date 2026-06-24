# Data Dictionary: Mutual Fund Analysis Project

This data dictionary outlines the structure of the `bluestock_mf.db` SQLite database, detailing the tables, columns, data types, and business definitions.

## 1. dim_fund

Stores static information and master details about mutual fund schemes.
- **Source:** `01_fund_master.csv`

| Column | Data Type | Business Definition |
|---|---|---|
| `amfi_code` | INTEGER (PK) | Unique identifier assigned by AMFI for each mutual fund scheme. |
| `fund_house` | TEXT | Name of the Asset Management Company (AMC). |
| `scheme_name` | TEXT | Full name of the mutual fund scheme. |
| `category` | TEXT | Broad classification (e.g., Equity, Debt, Hybrid). |
| `sub_category` | TEXT | Specific classification within the category (e.g., Large Cap, Small Cap). |
| `plan` | TEXT | Plan type (Regular or Direct). |
| `launch_date` | DATE | Date the scheme was launched. |
| `benchmark` | TEXT | The benchmark index the fund's performance is compared against. |
| `expense_ratio_pct` | REAL | Annual percentage of AUM charged to investors for managing the fund. |
| `exit_load_pct` | REAL | Fee charged for premature withdrawals. |
| `min_sip_amount` | REAL | Minimum investment required to start an SIP. |
| `min_lumpsum_amount` | REAL | Minimum investment required for a one-time (lumpsum) investment. |
| `fund_manager` | TEXT | Name of the primary fund manager. |
| `risk_category` | TEXT | General risk assessment (e.g., Moderate, Very High). |
| `sebi_category_code` | TEXT | SEBI categorization code. |

## 2. dim_date

A standard date dimension table to support time-series analysis and reporting.
- **Source:** Generated from transaction and NAV dates.

| Column | Data Type | Business Definition |
|---|---|---|
| `date_id` | DATE (PK) | Standard date in `YYYY-MM-DD` format. |
| `year` | INTEGER | Year component of the date. |
| `month` | INTEGER | Month component (1-12). |
| `day` | INTEGER | Day component (1-31). |
| `quarter` | INTEGER | Quarter of the year (1-4). |
| `day_of_week` | INTEGER | Day of the week (0-6 where 0=Monday). |

## 3. fact_nav

Historical daily Net Asset Values (NAV) for the funds. Missing weekend/holiday dates have been forward-filled.
- **Source:** `02_nav_history.csv`

| Column | Data Type | Business Definition |
|---|---|---|
| `nav_id` | INTEGER (PK) | Unique identifier for the NAV record. |
| `amfi_code` | INTEGER (FK) | Reference to `dim_fund.amfi_code`. |
| `date` | DATE (FK) | Date of the NAV record. Reference to `dim_date.date_id`. |
| `nav` | REAL | Net Asset Value of the fund on the given date. |

## 4. fact_transactions

Records of individual investor transactions including SIPs, lumpsums, and redemptions.
- **Source:** `08_investor_transactions.csv`

| Column | Data Type | Business Definition |
|---|---|---|
| `transaction_id` | INTEGER (PK) | Unique identifier for the transaction. |
| `investor_id` | TEXT | Unique identifier for the investor. |
| `transaction_date` | DATE (FK) | Date the transaction took place. Reference to `dim_date.date_id`. |
| `amfi_code` | INTEGER (FK) | Reference to `dim_fund.amfi_code`. |
| `transaction_type` | TEXT | Type of transaction (`SIP`, `Lumpsum`, or `Redemption`). |
| `amount_inr` | REAL | Value of the transaction in Indian Rupees. |
| `state` | TEXT | Investor's state of residence. |
| `city` | TEXT | Investor's city of residence. |
| `city_tier` | TEXT | Tier classification of the city (e.g., T30, B30). |
| `age_group` | TEXT | Age bracket of the investor. |
| `gender` | TEXT | Gender of the investor. |
| `annual_income_lakh` | REAL | Annual income bracket of the investor in Lakhs. |
| `payment_mode` | TEXT | Mode of payment used (e.g., UPI, Cheque, Mandate). |
| `kyc_status` | TEXT | Investor's KYC status (`Verified`, `Pending`, `Rejected`). |

## 5. fact_performance

Performance metrics, risk ratios, and star ratings for various funds over different timeframes.
- **Source:** `07_scheme_performance.csv`

| Column | Data Type | Business Definition |
|---|---|---|
| `performance_id` | INTEGER (PK) | Unique record identifier. |
| `amfi_code` | INTEGER (FK) | Reference to `dim_fund.amfi_code`. |
| `scheme_name` | TEXT | Name of the scheme. |
| `fund_house` | TEXT | Name of the fund house/AMC. |
| `category` | TEXT | Fund category. |
| `plan` | TEXT | Plan type. |
| `return_1yr_pct` | REAL | 1-Year annualized return percentage. |
| `return_3yr_pct` | REAL | 3-Year annualized return percentage. |
| `return_5yr_pct` | REAL | 5-Year annualized return percentage. |
| `benchmark_3yr_pct` | REAL | 3-Year annualized return of the benchmark index. |
| `alpha` | REAL | Measure of the active return on an investment. |
| `beta` | REAL | Measure of the volatility/systematic risk. |
| `sharpe_ratio` | REAL | Measure of risk-adjusted return. |
| `sortino_ratio` | REAL | Measure of risk-adjusted return relative to downside volatility. |
| `std_dev_ann_pct` | REAL | Annualized standard deviation of returns. |
| `max_drawdown_pct` | REAL | Maximum observed loss from a peak to a trough. |
| `aum_crore` | REAL | Assets Under Management for the scheme in Crores. |
| `expense_ratio_pct` | REAL | Annual expense ratio. Filtered to be within 0.1% to 2.5%. |
| `morningstar_rating` | INTEGER | Morningstar star rating. |
| `risk_grade` | TEXT | Evaluated risk grade for the scheme. |

## 6. fact_aum

Aggregated Assets Under Management (AUM) statistics at the fund house level.
- **Source:** `03_aum_by_fund_house.csv`

| Column | Data Type | Business Definition |
|---|---|---|
| `aum_id` | INTEGER (PK) | Unique record identifier. |
| `date` | DATE (FK) | Date of the AUM record. Reference to `dim_date.date_id`. |
| `fund_house` | TEXT | Name of the Asset Management Company. |
| `aum_lakh_crore` | REAL | Total AUM managed by the AMC in Lakh Crores. |
| `aum_crore` | REAL | Total AUM managed by the AMC in Crores. |
| `num_schemes` | INTEGER | Number of active schemes under the AMC. |
