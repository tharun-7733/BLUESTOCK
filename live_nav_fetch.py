import pandas as pd
import requests
import os
import time

def fetch_live_navs():
    """
    Fetches the latest NAV data for a list of benchmark mutual funds using mfapi.in
    """
    print("--- Fetching Live NAVs from mfapi.in ---")
    
    # Ensure raw data directory exists
    os.makedirs("data/raw", exist_ok=True)
    
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
                    file_path = f"data/raw/{name}_live_nav.csv"
                    nav_df.to_csv(file_path, index=False)
                    print(f"Saved {len(nav_df)} records to {file_path}")
                else:
                    print(f"No data available for {code}")
            else:
                print(f"Failed: API returned status code {response.status_code}")
        except Exception as e:
            print(f"Error fetching data for {code}: {e}")
        
        # Be nice to the API
        time.sleep(1)

if __name__ == "__main__":
    fetch_live_navs()
