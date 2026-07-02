import sqlite3
import pandas as pd
import argparse

def get_recommendations(risk_appetite):
    risk_mapping = {
        'Low': ['Low'],
        'Moderate': ['Moderate', 'Moderately High'],
        'High': ['High', 'Very High']
    }
    
    if risk_appetite not in risk_mapping:
        print(f"Error: Invalid risk appetite '{risk_appetite}'. Choose from Low, Moderate, High.")
        return
        
    target_grades = risk_mapping[risk_appetite]
    
    conn = sqlite3.connect('bluestock_mf.db')
    query = """
    SELECT 
        df.scheme_name, 
        df.category, 
        df.sub_category, 
        fp.risk_grade, 
        fp.sharpe_ratio, 
        fp.return_3yr_pct
    FROM dim_fund df
    JOIN fact_performance fp ON df.amfi_code = fp.amfi_code
    WHERE fp.risk_grade IN ({})
    ORDER BY fp.sharpe_ratio DESC
    LIMIT 3
    """.format(','.join(['?']*len(target_grades)))
    
    recommendations = pd.read_sql_query(query, conn, params=target_grades)
    conn.close()
    
    if recommendations.empty:
        print("No funds found for this risk appetite.")
        return
        
    print(f"\n--- Top 3 Recommended Funds for {risk_appetite} Risk Appetite ---\n")
    print(recommendations.to_markdown(index=False))
    print("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simple Fund Recommender based on Risk Appetite')
    parser.add_argument('--risk', type=str, choices=['Low', 'Moderate', 'High'], required=True,
                        help='Risk appetite (Low / Moderate / High)')
    
    args = parser.parse_args()
    get_recommendations(args.risk)
