import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    print("Connecting to DB...")
    conn = sqlite3.connect('bluestock_mf.db')
    
    dim_fund = pd.read_sql_query("SELECT * FROM dim_fund", conn)
    fact_nav = pd.read_sql_query("SELECT * FROM fact_nav", conn)
    
    conn.close()
    
    fact_nav['date'] = pd.to_datetime(fact_nav['date'])
    fact_nav = fact_nav.sort_values(by=['amfi_code', 'date'])
    
    # Calculate daily return for each fund
    fact_nav['daily_return'] = fact_nav.groupby('amfi_code')['nav'].pct_change()
    
    # TASK 1: Historical VaR (95%) and CVaR
    print("Computing VaR and CVaR...")
    var_cvar_data = []
    
    for amfi, group in fact_nav.groupby('amfi_code'):
        returns = group['daily_return'].dropna()
        if len(returns) == 0:
            continue
            
        var_95 = np.percentile(returns, 5)
        cvar = returns[returns <= var_95].mean()
        
        fund_name = dim_fund[dim_fund['amfi_code'] == amfi]['scheme_name'].iloc[0] if len(dim_fund[dim_fund['amfi_code'] == amfi]) > 0 else "Unknown"
        
        var_cvar_data.append({
            'amfi_code': amfi,
            'scheme_name': fund_name,
            'VaR_95': var_95,
            'CVaR': cvar
        })
        
    var_cvar_df = pd.DataFrame(var_cvar_data)
    var_cvar_df.to_csv('var_cvar_report.csv', index=False)
    print("Saved var_cvar_report.csv")
    
    # TASK 2: Rolling 90-day Sharpe Ratio
    print("Computing Rolling 90-day Sharpe for 5 key funds...")
    # Select 5 key equity funds
    equity_funds = dim_fund[dim_fund['category'] == 'Equity'].head(5)
    key_amfi_codes = equity_funds['amfi_code'].tolist()
    
    plt.figure(figsize=(14, 7))
    sns.set_theme(style="whitegrid")
    
    for amfi in key_amfi_codes:
        group = fact_nav[fact_nav['amfi_code'] == amfi].copy()
        group = group.set_index('date')
        
        # Calculate rolling mean and std
        rolling_mean = group['daily_return'].rolling(window=90).mean()
        rolling_std = group['daily_return'].rolling(window=90).std()
        
        # Calculate annualized rolling Sharpe
        rolling_sharpe = (rolling_mean / rolling_std) * np.sqrt(252)
        
        fund_name = dim_fund[dim_fund['amfi_code'] == amfi]['scheme_name'].iloc[0]
        plt.plot(group.index, rolling_sharpe, label=fund_name, alpha=0.8)
        
    plt.title('Rolling 90-Day Sharpe Ratio for 5 Key Equity Funds')
    plt.xlabel('Date')
    plt.ylabel('Annualized Sharpe Ratio')
    plt.legend()
    plt.tight_layout()
    plt.savefig('rolling_sharpe_chart.png', dpi=300)
    print("Saved rolling_sharpe_chart.png")

if __name__ == "__main__":
    main()
