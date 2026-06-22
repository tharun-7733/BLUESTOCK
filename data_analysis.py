import pandas as pd
import glob
import os
import requests
import json
import time

def check_csvs():
    print("--- Loading and Checking CSVs ---")
    files = glob.glob("data/raw/*.csv")
    for file in sorted(files):
        df = pd.read_csv(file)
        print(f"\nFile: {os.path.basename(file)}")
        print(f"Shape: {df.shape}")
        print("Dtypes:")
        print(df.dtypes)
        print("Head:")
        print(df.head(2))

def fetch_navs():
    print("\n--- Fetching NAVs from mfapi.in ---")
    schemes = {
        "HDFC_Top100": 125497,
        "SBI_Bluechip": 119551,
        "ICICI_Bluechip": 120503,
        "Nippon_LargeCap": 118632,
        "Axis_Bluechip": 119092,
        "Kotak_Bluechip": 120841
    }
    for name, code in schemes.items():
        url = f"https://api.mfapi.in/mf/{code}"
        print(f"Fetching {name} (Code: {code})...")
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    nav_df = pd.DataFrame(data["data"])
                    nav_df.to_csv(f"data/raw/{name}_nav.csv", index=False)
                    print(f"Saved {len(nav_df)} records to data/raw/{name}_nav.csv")
                else:
                    print(f"No data for {code}")
            else:
                print(f"Failed: {response.status_code}")
        except Exception as e:
            print(f"Error fetching {code}: {e}")
        time.sleep(1) # Be nice to the API

def explore_fund_master():
    print("\n--- Exploring Fund Master ---")
    df = pd.read_csv("data/raw/01_fund_master.csv")
    print(f"Unique Fund Houses ({df['fund_house'].nunique()}):", df['fund_house'].unique())
    print(f"Unique Categories ({df['category'].nunique()}):", df['category'].unique())
    print(f"Unique Sub-Categories ({df['sub_category'].nunique()}):", df['sub_category'].unique())
    print(f"Unique Risk Grades ({df['risk_category'].nunique()}):", df['risk_category'].unique())

def validate_codes():
    print("\n--- Validating AMFI Codes ---")
    fm = pd.read_csv("data/raw/01_fund_master.csv")
    nh = pd.read_csv("data/raw/02_nav_history.csv")
    fm_codes = set(fm['amfi_code'].unique())
    nh_codes = set(nh['amfi_code'].unique())
    
    missing_in_nh = fm_codes - nh_codes
    summary = {
        "total_funds_in_master": len(fm_codes),
        "total_funds_in_nav_history": len(nh_codes),
        "funds_missing_nav_history": list(missing_in_nh),
        "status": "PASS" if len(missing_in_nh) == 0 else "FAIL"
    }
    print("Validation Summary:", summary)
    
    with open("reports/data_quality_summary.json", "w") as f:
        json.dump(summary, f, indent=4)
    print("Saved summary to reports/data_quality_summary.json")

if __name__ == "__main__":
    check_csvs()
    fetch_navs()
    explore_fund_master()
    validate_codes()
