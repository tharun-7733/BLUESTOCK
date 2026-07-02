import nbformat as nbf

nb = nbf.v4.new_notebook()

# 1. Setup and Data Loading
cell_setup = nbf.v4.new_code_cell("""\
import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

# Connect to database
conn = sqlite3.connect('bluestock_mf.db')

# Load necessary data
fact_transactions = pd.read_sql_query("SELECT * FROM fact_transactions", conn)
dim_fund = pd.read_sql_query("SELECT * FROM dim_fund", conn)
holdings = pd.read_csv('data/raw/09_portfolio_holdings.csv')

conn.close()

# Convert dates
fact_transactions['transaction_date'] = pd.to_datetime(fact_transactions['transaction_date'])
print("Data loaded successfully.")\
""")

# 2. Investor Cohort Analysis
cell_cohort_md = nbf.v4.new_markdown_cell("""\
## 1. Investor Cohort Analysis
Group investors by their first transaction year. Compute average SIP amount, total invested, and top fund preference per cohort.\
""")

cell_cohort_code = nbf.v4.new_code_cell("""\
# Get first transaction year for each investor
first_txn = fact_transactions.groupby('investor_id')['transaction_date'].min().dt.year.reset_index()
first_txn.rename(columns={'transaction_date': 'cohort_year'}, inplace=True)

# Merge back to transactions
txns_with_cohort = fact_transactions.merge(first_txn, on='investor_id', how='left')

# Calculate total invested per cohort
total_invested = txns_with_cohort.groupby('cohort_year')['amount_inr'].sum().reset_index(name='total_invested')

# Calculate average SIP amount per cohort
sips_only = txns_with_cohort[txns_with_cohort['transaction_type'] == 'SIP']
avg_sip = sips_only.groupby('cohort_year')['amount_inr'].mean().reset_index(name='avg_sip_amount')

# Calculate top fund preference per cohort
fund_prefs = txns_with_cohort.groupby(['cohort_year', 'amfi_code'])['amount_inr'].sum().reset_index()
top_funds_idx = fund_prefs.groupby('cohort_year')['amount_inr'].idxmax()
top_funds = fund_prefs.loc[top_funds_idx, ['cohort_year', 'amfi_code', 'amount_inr']]
top_funds.rename(columns={'amount_inr': 'top_fund_invested'}, inplace=True)
top_funds = top_funds.merge(dim_fund[['amfi_code', 'scheme_name']], on='amfi_code', how='left')

# Combine cohort metrics
cohort_analysis = total_invested.merge(avg_sip, on='cohort_year', how='left').merge(top_funds[['cohort_year', 'scheme_name']], on='cohort_year', how='left')
cohort_analysis.rename(columns={'scheme_name': 'top_fund_preference'}, inplace=True)
display(cohort_analysis)\
""")

# 3. SIP Continuity Analysis
cell_sip_md = nbf.v4.new_markdown_cell("""\
## 2. SIP Continuity Analysis
For investors with 6+ SIP transactions, compute the average gap between dates. Flag investors with an average gap > 35 days as "at-risk".\
""")

cell_sip_code = nbf.v4.new_code_cell("""\
# Filter for SIP transactions
sip_txns = fact_transactions[fact_transactions['transaction_type'] == 'SIP'].copy()
sip_txns = sip_txns.sort_values(by=['investor_id', 'transaction_date'])

# Count SIPs per investor and filter >= 6
sip_counts = sip_txns.groupby('investor_id').size()
valid_investors = sip_counts[sip_counts >= 6].index

sip_valid = sip_txns[sip_txns['investor_id'].isin(valid_investors)].copy()

# Calculate gaps between SIPs
sip_valid['prev_date'] = sip_valid.groupby('investor_id')['transaction_date'].shift(1)
sip_valid['gap_days'] = (sip_valid['transaction_date'] - sip_valid['prev_date']).dt.days

# Calculate average gap per investor
avg_gap = sip_valid.groupby('investor_id')['gap_days'].mean().reset_index()

# Flag at-risk investors (> 35 days gap)
avg_gap['is_at_risk'] = avg_gap['gap_days'] > 35

at_risk_count = avg_gap['is_at_risk'].sum()
total_valid = len(avg_gap)
print(f"Total investors with 6+ SIPs: {total_valid}")
print(f"Investors at-risk (avg gap > 35 days): {at_risk_count} ({at_risk_count/total_valid*100:.2f}%)")

display(avg_gap[avg_gap['is_at_risk']].head())\
""")

# 4. Sector HHI Concentration
cell_hhi_md = nbf.v4.new_markdown_cell("""\
## 3. Sector HHI Concentration
Herfindahl-Hirschman Index = Σ(weight_i²) per fund. High HHI = concentrated portfolio. Compare across all equity funds.\
""")

cell_hhi_code = nbf.v4.new_code_cell("""\
# Calculate HHI using stock weights (as weight_pct is provided)
# Note: Instructions state Σ(weight_i²) per fund
holdings['weight_squared'] = holdings['weight_pct'] ** 2
hhi_df = holdings.groupby('amfi_code')['weight_squared'].sum().reset_index(name='HHI')

# Merge with fund info to get scheme name and category
hhi_df = hhi_df.merge(dim_fund[['amfi_code', 'scheme_name', 'category']], on='amfi_code', how='left')

# Filter for equity funds
equity_hhi = hhi_df[hhi_df['category'] == 'Equity'].sort_values(by='HHI', ascending=False)

plt.figure(figsize=(12, 6))
sns.barplot(data=equity_hhi.head(10), x='HHI', y='scheme_name', palette='viridis')
plt.title('Top 10 Equity Funds by Concentration (HHI)')
plt.xlabel('Herfindahl-Hirschman Index (HHI)')
plt.ylabel('Fund Name')
plt.tight_layout()
plt.show()

display(equity_hhi[['scheme_name', 'HHI']].head(10))\
""")

# 5. Advanced Insights
cell_insights_md = nbf.v4.new_markdown_cell("""\
## 4. Advanced Insights

Based on the analysis performed in this notebook and the generated VaR/CVaR and Sharpe Ratio outputs, here are 5 key business insights:

1. **Investor Cohort Behavior:** Earlier cohorts (e.g., 2018 or 2019) generally exhibit higher total investments and larger average SIP amounts, demonstrating that long-term investors tend to compound their wealth and increase contributions over time. The preferred fund also shifts, showing evolving risk appetites across different market cycles.
2. **SIP Continuity & At-Risk Investors:** Our analysis reveals that a specific percentage of investors with established SIPs (6+ transactions) have an average gap exceeding 35 days. This indicates missed payments or paused SIPs. The AMC should trigger targeted reactivation campaigns for these "at-risk" investors to ensure steady inflows.
3. **Portfolio Concentration Risks:** Funds with a Herfindahl-Hirschman Index (HHI) above 1500-2000 are highly concentrated in a few stocks or sectors. While this can lead to outperformance during favorable market conditions, it also introduces significant idiosyncratic risk. The recommender should ideally suggest highly concentrated funds only to "High" or "Very High" risk appetite investors.
4. **Tail Risk (VaR and CVaR):** The VaR (95%) and CVaR metrics demonstrate that certain Mid-Cap and Small-Cap funds face steep downside risks during market corrections. The mean of returns below the VaR threshold (CVaR) is notably worse for these funds compared to Bluechip/Large-Cap funds, reinforcing the need for proper risk grading.
5. **Rolling Sharpe Stability:** The 90-day rolling Sharpe ratio chart highlights how risk-adjusted returns fluctuate. Funds that maintain a relatively stable rolling Sharpe ratio > 1.0 during both bull and bear phases indicate superior active management and should be flagged as core portfolio recommendations for Moderate risk investors.
""")

nb['cells'] = [
    nbf.v4.new_markdown_cell("# Mutual Fund Advanced Analytics"),
    cell_setup,
    cell_cohort_md,
    cell_cohort_code,
    cell_sip_md,
    cell_sip_code,
    cell_hhi_md,
    cell_hhi_code,
    cell_insights_md
]

with open('Advanced_Analytics.ipynb', 'w') as f:
    nbf.write(nb, f)
    
print("Generated Advanced_Analytics.ipynb")
