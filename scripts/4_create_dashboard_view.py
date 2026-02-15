import sqlite3
import pandas as pd

print("Generating Final Executive Dashboard Dataset...")

# 1. Connect to the Database
conn = sqlite3.connect('core_banking.db')

# 2. The SQL Query (The "Join")
# We use a LEFT JOIN to include ALL clients, even those who didn't submit financials.
# In banking, "Missing Data" is often the highest risk category.
query = """
    SELECT 
        f.client_id,
        f.industry_sector,
        f.facility_amount_usd,
        f.interest_rate_margin_pct,
        f.maturity_date,
        r.revenue,
        r.ebitda,
        r.total_debt,
        r.icr,
        r.leverage_ratio,
        r.internal_rating,
        r.pd_percent,
        r.ecl_provision
    FROM facility_details f
    LEFT JOIN financial_reports r ON f.client_id = r.client_id
"""

df = pd.read_sql_query(query, conn)
conn.close()

# 3. Apply "Final Action Logic" (The Executive Summary)
# Your dashboard needs to tell the manager WHAT to do, not just show numbers.

def define_action_status(row):
    # CRITICAL: If they didn't submit financials (Data is NaN)
    if pd.isna(row['internal_rating']):
        return "Non-Compliant (Missing Financials)"
    
    # CRITICAL: If they are rated 'C' (High Risk)
    if row['internal_rating'] == 'C':
        return "Critical Watchlist"
    
    # WARNING: If Rating is 'B' but the loan is huge (>$150M) -> Concentration Risk
    if row['internal_rating'] == 'B' and row['facility_amount_usd'] > 150000000:
        return "Review Required (High Exposure)"
    
    # STANDARD: Everyone else
    return "Performing"

# Apply the logic
df['dashboard_status'] = df.apply(define_action_status, axis=1)

# 4. Save to CSV
# This file is what you will drag into Tableau/Power BI
output_filename = "final_dashboard_data.csv"
df.to_csv(output_filename, index=False)

print("-" * 30)
print(f"SUCCESS! Dashboard data saved to '{output_filename}'.")
print(f"Total Rows: {len(df)}")
print("Status Breakdown:")
print(df['dashboard_status'].value_counts())
print("-" * 30)