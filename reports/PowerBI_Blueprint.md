# Power BI Implementation Blueprint: Mutual Fund Dashboard

This document provides the exact, step-by-step instructions, DAX formulas, and configuration settings required to build the `bluestock_mf_dashboard.pbix` file. Follow this guide in Power BI Desktop (on Windows) to perfectly replicate the requested deliverable.

## 1. Data Connection & Modeling

### Step 1.1: Connect to Data
1. Open Power BI Desktop.
2. Go to **Home > Get Data > More...**
3. Search for **ODBC** and select it.
4. If you have a SQLite ODBC driver installed, select your DSN pointing to `bluestock_mf.db`. 
   *(Alternatively, use **Get Data > Text/CSV** and import the 6 CSVs from your `data/` folder).*
5. Load the following tables: `dim_fund`, `dim_date`, `fact_nav`, `fact_transactions`, `fact_performance`, `fact_aum`.

### Step 1.2: Create Relationships (Model View)
Go to the **Model View** (left pane, third icon) and create these relationships by dragging and dropping:
1. `dim_fund[amfi_code]` (1) ➔ `fact_nav[amfi_code]` (*)
2. `dim_fund[amfi_code]` (1) ➔ `fact_transactions[amfi_code]` (*)
3. `dim_fund[amfi_code]` (1) ➔ `fact_performance[amfi_code]` (1 to 1, or 1 to *)
4. `dim_date[date_id]` (1) ➔ `fact_nav[date]` (*)
5. `dim_date[date_id]` (1) ➔ `fact_transactions[transaction_date]` (*)
6. `dim_date[date_id]` (1) ➔ `fact_aum[date]` (*)

---

## 2. DAX Measures

Go to the **Data View**, click **New Measure**, and paste the following formulas:

**1. Total AUM (₹ L Cr)**
```dax
Total AUM = SUM(fact_performance[aum_crore]) / 100000 
// Formatted as "₹#,##0.00 L Cr"
```

**2. SIP Inflows (₹ Cr)**
```dax
SIP Inflows = 
CALCULATE(
    SUM(fact_transactions[amount_inr]),
    fact_transactions[transaction_type] = "SIP"
) / 10000000 
// Formatted as "₹#,##0K Cr"
```

**3. Total Folios (Investors)**
```dax
Total Folios = DISTINCTCOUNT(fact_transactions[investor_id])
```

**4. Total Schemes**
```dax
Total Schemes = DISTINCTCOUNT(dim_fund[amfi_code])
```

**5. Net Inflows (FY25)**
```dax
Net Inflows = 
CALCULATE(SUM(fact_transactions[amount_inr]), fact_transactions[transaction_type] IN {"SIP", "Lumpsum"}) - 
CALCULATE(SUM(fact_transactions[amount_inr]), fact_transactions[transaction_type] = "Redemption")
```

---

## 3. Page Configurations

### Page 1: Industry Overview
* **KPI Cards (Top Row):** Create 4 Card visuals. Drop the 4 DAX measures created above (`Total AUM`, `SIP Inflows`, `Total Folios`, `Total Schemes`) into each.
* **Line Chart (Industry AUM Trend 2022–2025):** 
  * X-Axis: `dim_date[year]` and `dim_date[month]`
  * Y-Axis: `SUM(fact_aum[aum_crore])`
* **Clustered Bar Chart (AUM by AMC):**
  * Y-Axis: `fact_aum[fund_house]`
  * X-Axis: `SUM(fact_aum[aum_crore])`
  * Sort by AUM descending.

### Page 2: Fund Performance
* **Slicers (Top Row):** Add three slicers for `dim_fund[fund_house]`, `dim_fund[category]`, and `dim_fund[plan]`.
* **Scatter Plot (Risk vs Return):**
  * X-Axis: `fact_performance[return_3yr_pct]`
  * Y-Axis: `fact_performance[std_dev_ann_pct]`
  * Details: `dim_fund[scheme_name]`
  * Size: `fact_performance[aum_crore]`
* **Table (Fund Scorecard):** Add `scheme_name`, `category`, `return_1yr_pct`, `return_3yr_pct`, `expense_ratio_pct`, and `morningstar_rating`. 
* **Line Chart (NAV vs Benchmark):** 
  * X-Axis: `dim_date[date_id]`
  * Y-Axis: `fact_nav[nav]` (Average)

### Page 3: Investor Analytics
* **Slicers:** `fact_transactions[state]`, `fact_transactions[age_group]`, `fact_transactions[city_tier]`.
* **Clustered Bar Chart:**
  * Y-Axis: `fact_transactions[state]`
  * X-Axis: `SUM(fact_transactions[amount_inr])`
* **Donut Chart:**
  * Legend: `fact_transactions[transaction_type]`
  * Values: `SUM(fact_transactions[amount_inr])`
* **Column Chart:**
  * X-Axis: `fact_transactions[age_group]`
  * Y-Axis: `Average SIP Amount` (Create a measure: `AVERAGE(fact_transactions[amount_inr])` filtered by SIP).
* **Line Chart (Monthly Txn Volume):**
  * X-Axis: `dim_date[year]` & `month`
  * Y-Axis: `COUNT(fact_transactions[transaction_id])`

### Page 4: SIP & Market Trends
* **Line and Stacked Column Chart (Dual-Axis):**
  * X-Axis: `dim_date[date_id]`
  * Column y-axis: `[SIP Inflows]`
  * Line y-axis: Nifty 50 Index Value (If available in your dataset, else use `AVERAGE(fact_performance[benchmark_3yr_pct])` as a proxy trend).
* **Matrix (Category Inflow Heatmap):**
  * Rows: `dim_fund[category]`
  * Columns: `dim_date[year]`
  * Values: `[Net Inflows]`
  * Format: Conditional Formatting > Background Color (Blue scale).
* **Top 5 Categories Bar Chart:**
  * Use a Top N filter on `dim_fund[category]` based on `[Net Inflows]`.

---

## 4. Interactivity & Styling

1. **Drill-through:** 
   * Create a hidden "NAV Detail" page.
   * Add `dim_fund[scheme_name]` to the "Drill-through" well on this page.
   * On Page 2's Scorecard Table, users can now Right-Click a fund > Drill through > NAV Detail.
2. **Tooltips:** Drag `dim_fund[category]` and `fact_performance[aum_crore]` into the Tooltips well of the Scatter Plot.
3. **Bluestock Theme:**
   * Go to **View > Themes > Customize current theme**.
   * Set primary colors to Bluestock branding (e.g., Deep Blue `#003366`, Light Blue `#0073e6`, Accent `#FF9900`).
   * Insert the Bluestock logo using **Insert > Image** and place it in the top left of all pages.

---

## 5. Exporting the Deliverables

1. **Save as .pbix:** File > Save As > `bluestock_mf_dashboard.pbix`.
2. **Export to PDF:** File > Export > Export to PDF (Saves all pages as `Dashboard.pdf`).
3. **PNG Screenshots:** 
   * Navigate to Page 1. Click `Windows Key + Shift + S` or use the Snipping Tool to take a screenshot. Save as `page1_overview.png`.
   * Repeat for Pages 2, 3, and 4.
