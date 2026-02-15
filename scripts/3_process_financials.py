import pandas as pd
import sqlite3
import os
import re
import numpy as np

print("Starting Advanced Banking Analytics Pipeline...")

# --- CONFIGURATION ---
folder_path = "client_financials"
db_path = "core_banking.db"
BASE_INTEREST_RATE = 0.045  # Simulating a 4.5% SOFR/SIBOR base rate
LGD = 0.45  # Loss Given Default (Standard Basel Assumption: 45%)

# 1. LOAD CORE DATA (We need Interest Margins to calculate Expense)
conn = sqlite3.connect(db_path)
core_df = pd.read_sql("SELECT client_id, facility_amount_usd, interest_rate_margin_pct FROM facility_details", conn)
valid_clients = core_df['client_id'].tolist()

# 2. THE ROSETTA STONE (Column Mapping)
column_mapping = {
    'Revenue': ['Revenue', 'Total Revenue', 'Sales', 'Gross_Income', 'Rev'],
    'EBITDA': ['EBITDA', 'Op_Profit', 'Earnings_Before_Interest', 'Operating_Income'],
    'Total_Debt': ['Total Debt', 'Debt_Exposure', 'Liabilities_Total', 'Loan_Balance']
}

raw_data = []
files_processed = 0
errors_logged = 0

# 3. EXTRACT & CLEAN (The "Janitor" Work)
print(f"Scanning folder '{folder_path}'...")

for filename in os.listdir(folder_path):
    if filename.endswith(".xlsx"):
        client_id = filename.split('_financials')[0]
        
        if client_id not in valid_clients:
            continue
            
        try:
            file_path = os.path.join(folder_path, filename)
            df = pd.read_excel(file_path)
            
            # Standardize Columns
            for col in df.columns:
                for standard_name, aliases in column_mapping.items():
                    if col in aliases:
                        df.rename(columns={col: standard_name}, inplace=True)
            
            # Check required columns
            required_cols = ['Revenue', 'EBITDA', 'Total_Debt']
            if not all(col in df.columns for col in required_cols):
                errors_logged += 1
                continue
                
            # Clean Non-Numeric Characters
            for col in required_cols:
                df[col] = df[col].astype(str).apply(lambda x: re.sub(r'[^\d\.]', '', x))
                df[col] = pd.to_numeric(df[col], errors='coerce')

            df.dropna(subset=['EBITDA', 'Total_Debt'], inplace=True)
            
            if df.empty:
                continue

            # Store the raw cleaned numbers
            raw_data.append({
                'client_id': client_id,
                'revenue': df['Revenue'].iloc[0],
                'ebitda': df['EBITDA'].iloc[0],
                'total_debt': df['Total_Debt'].iloc[0]
            })
            
            files_processed += 1
            if files_processed % 100 == 0:
                print(f"Extracted {files_processed} files...")
                
        except Exception as e:
            errors_logged += 1

# 4. TRANSFORMATION & ADVANCED METRICS (The "Analyst" Work)
if raw_data:
    financials_df = pd.DataFrame(raw_data)
    
    # MERGE with Core Data
    merged_df = pd.merge(financials_df, core_df, on='client_id', how='left')

    # --- METRIC 1: Interest Coverage Ratio (ICR) ---
    merged_df['estimated_interest_rate'] = BASE_INTEREST_RATE + (merged_df['interest_rate_margin_pct'] / 100)
    merged_df['annual_interest_expense'] = merged_df['total_debt'] * merged_df['estimated_interest_rate']
    
    merged_df['icr'] = merged_df.apply(
        lambda row: row['ebitda'] / row['annual_interest_expense'] if row['annual_interest_expense'] > 0 else 0, axis=1
    )

    # --- METRIC 2: Leverage Ratio ---
    merged_df['leverage_ratio'] = merged_df.apply(
        lambda row: row['total_debt'] / row['ebitda'] if row['ebitda'] > 0 else 99, axis=1
    )

    # --- METRIC 3: Internal Credit Rating (Synthetic) ---
    def assign_rating(row):
        if row['leverage_ratio'] < 2.5 and row['icr'] > 3.0:
            return 'A'  # Low Risk
        elif row['leverage_ratio'] < 4.0 and row['icr'] > 1.5:
            return 'B'  # Medium Risk
        else:
            return 'C'  # High Risk (Watchlist)
            
    merged_df['internal_rating'] = merged_df.apply(assign_rating, axis=1)

    # --- METRIC 4: Probability of Default (PD) Mapping ---
    pd_mapping = {'A': 0.01, 'B': 0.05, 'C': 0.15}
    merged_df['pd_percent'] = merged_df['internal_rating'].map(pd_mapping)

    # --- METRIC 5: Expected Credit Loss (ECL) ---
    merged_df['ecl_provision'] = merged_df['facility_amount_usd'] * merged_df['pd_percent'] * LGD

    # 5. LOAD TO SQL
    # [FIX IS HERE]: Added 'pd_percent' to the list below so it saves to the DB
    final_output = merged_df[[
        'client_id', 'revenue', 'ebitda', 'total_debt', 
        'icr', 'leverage_ratio', 'internal_rating', 'pd_percent', 'ecl_provision'
    ]].copy()

    # Rounding for cleanliness
    final_output['icr'] = final_output['icr'].round(2)
    final_output['leverage_ratio'] = final_output['leverage_ratio'].round(2)
    final_output['ecl_provision'] = final_output['ecl_provision'].round(2)

    final_output.to_sql('financial_reports', conn, if_exists='replace', index=False)
    
    print("-" * 30)
    print(f"SUCCESS! Advanced Analytics Complete.")
    print(f"Processed: {len(final_output)} clients")
    print(f"Total Portfolio ECL Provision Calculated: ${final_output['ecl_provision'].sum():,.2f}")
    print("Metrics saved to 'financial_reports' in core_banking.db")

else:
    print("No data processed.")

conn.close()