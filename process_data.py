import pandas as pd
import numpy as np
import os
import shutil
import sqlite3
from sqlalchemy import create_engine

raw_dir = 'data/raw'
proc_dir = 'data/processed'
os.makedirs(proc_dir, exist_ok=True)

print("Starting data processing...")

# 1. Copy all 10 numbered files to processed (will overwrite the cleaned ones)
csv_files = [f for f in os.listdir(raw_dir) if f.endswith('.csv') and f[:2].isdigit()]
for f in csv_files:
    shutil.copy(os.path.join(raw_dir, f), os.path.join(proc_dir, f))

# 2. Clean 02_nav_history.csv
print("Cleaning nav_history...")
nav_path = os.path.join(proc_dir, '02_nav_history.csv')
nav_df = pd.read_csv(nav_path)
nav_df['date'] = pd.to_datetime(nav_df['date'])
nav_df = nav_df.drop_duplicates()
nav_df = nav_df[nav_df['nav'] > 0]

def fill_missing_dates(group):
    amfi_code = group.name
    min_date = group['date'].min()
    max_date = group['date'].max()
    full_dates = pd.date_range(min_date, max_date)
    group = group.set_index('date').reindex(full_dates).ffill()
    group = group.reset_index().rename(columns={'index': 'date'})
    group['amfi_code'] = amfi_code
    return group

nav_df = nav_df.sort_values(['amfi_code', 'date'])
nav_df = nav_df.groupby('amfi_code', group_keys=False).apply(fill_missing_dates)
nav_df = nav_df.sort_values(['amfi_code', 'date'])
nav_df['date'] = nav_df['date'].dt.strftime('%Y-%m-%d')
nav_df.to_csv(nav_path, index=False)

# 3. Clean 08_investor_transactions.csv
print("Cleaning investor_transactions...")
txn_path = os.path.join(proc_dir, '08_investor_transactions.csv')
txn_df = pd.read_csv(txn_path)
txn_df['transaction_type'] = txn_df['transaction_type'].str.strip().str.title()
txn_df['transaction_type'] = txn_df['transaction_type'].replace({'Sip': 'SIP'})
valid_types = ['SIP', 'Lumpsum', 'Redemption']
txn_df = txn_df[txn_df['transaction_type'].isin(valid_types)]
txn_df = txn_df[txn_df['amount_inr'] > 0]
txn_df['transaction_date'] = pd.to_datetime(txn_df['transaction_date'], errors='coerce')
txn_df = txn_df.dropna(subset=['transaction_date'])
txn_df['transaction_date'] = txn_df['transaction_date'].dt.strftime('%Y-%m-%d')
txn_df['kyc_status'] = txn_df['kyc_status'].str.strip().str.title()
# Assume Verified, Pending are valid
txn_df = txn_df[txn_df['kyc_status'].isin(['Verified', 'Pending', 'Rejected'])]
txn_df.to_csv(txn_path, index=False)

# 4. Clean 07_scheme_performance.csv
print("Cleaning scheme_performance...")
perf_path = os.path.join(proc_dir, '07_scheme_performance.csv')
perf_df = pd.read_csv(perf_path)
ret_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct']
for col in ret_cols:
    perf_df[col] = pd.to_numeric(perf_df[col], errors='coerce')

# Flag anomalies > 100% or < -100% 
# (The task says 'flag anomalies', we will just add a flag column)
perf_df['is_anomaly'] = False
for col in ret_cols:
    perf_df.loc[(perf_df[col] > 100) | (perf_df[col] < -100), 'is_anomaly'] = True

perf_df['expense_ratio_pct'] = pd.to_numeric(perf_df['expense_ratio_pct'], errors='coerce')
perf_df = perf_df[(perf_df['expense_ratio_pct'] >= 0.1) & (perf_df['expense_ratio_pct'] <= 2.5)]
perf_df.to_csv(perf_path, index=False)

# 5. Load to SQLite
print("Loading to SQLite...")
db_path = 'bluestock_mf.db'
if os.path.exists(db_path):
    os.remove(db_path)

# Initialize schema
conn = sqlite3.connect(db_path)
with open('sql/schema.sql', 'r') as f:
    conn.executescript(f.read())
conn.close()

engine = create_engine(f'sqlite:///{db_path}')

# Load dim_fund
fund_df = pd.read_csv(os.path.join(proc_dir, '01_fund_master.csv'))
conn_sql = sqlite3.connect(db_path)
fund_df.to_sql('dim_fund', con=conn_sql, if_exists='append', index=False)

# Load fact_nav
# We don't want nav_id to be auto-inserted by pandas, we let sqlite auto-increment
nav_df.to_sql('fact_nav', con=conn_sql, if_exists='append', index=False)

# Load fact_transactions
txn_df.to_sql('fact_transactions', con=conn_sql, if_exists='append', index=False)

# Load fact_performance
# fact_performance doesn't have is_anomaly in our schema, so we drop it before loading or add it to schema
# Since schema doesn't have it, we drop it here.
perf_df.drop(columns=['is_anomaly'], errors='ignore').to_sql('fact_performance', con=conn_sql, if_exists='append', index=False)

# Load fact_aum
aum_df = pd.read_csv(os.path.join(proc_dir, '03_aum_by_fund_house.csv'))
aum_df['date'] = pd.to_datetime(aum_df['date']).dt.strftime('%Y-%m-%d')
aum_df.to_sql('fact_aum', con=conn_sql, if_exists='append', index=False)

# Generate dim_date
dates = pd.concat([nav_df['date'], txn_df['transaction_date'], aum_df['date']]).dropna().unique()
dim_date_df = pd.DataFrame({'date_id': dates})
dim_date_df['date_id'] = pd.to_datetime(dim_date_df['date_id'])
dim_date_df['year'] = dim_date_df['date_id'].dt.year
dim_date_df['month'] = dim_date_df['date_id'].dt.month
dim_date_df['day'] = dim_date_df['date_id'].dt.day
dim_date_df['quarter'] = dim_date_df['date_id'].dt.quarter
dim_date_df['day_of_week'] = dim_date_df['date_id'].dt.dayofweek
dim_date_df['date_id'] = dim_date_df['date_id'].dt.strftime('%Y-%m-%d')
dim_date_df.to_sql('dim_date', con=conn_sql, if_exists='append', index=False)
conn_sql.close()

print("Data processing and DB loading complete.")
