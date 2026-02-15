import sqlite3
import pandas as pd
import numpy as np
import os
import random

print("Initializing Financial Data Simulation...")

# 1. Setup the folder for our messy files
folder_name = "client_financials"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# 2. Get the list of Client IDs from our Core Database (Source of Truth)
conn = sqlite3.connect('core_banking.db')
core_df = pd.read_sql_query("SELECT client_id FROM facility_details", conn)
conn.close()

# --- CONFIGURATION ---
# We will generate financials for the first 800 clients only.
# This simulates an 80% submission rate. The missing 200 are "non-compliant."
clients_to_generate = core_df['client_id'].head(800).tolist()

print(f"Generating messy Excel files for {len(clients_to_generate)} clients...")

# 3. Define the "Chaos" - Different ways clients might name their columns
col_variations = {
    'revenue': ['Revenue', 'Total Revenue', 'Sales', 'Gross_Income', 'Rev'],
    'ebitda': ['EBITDA', 'Op_Profit', 'Earnings_Before_Interest', 'Operating_Income'],
    'total_debt': ['Total Debt', 'Debt_Exposure', 'Liabilities_Total', 'Loan_Balance']
}

# 4. The Loop: Generate a unique, messy file for each client
for i, client_id in enumerate(clients_to_generate):
    
    # Randomly choose column names for this specific client
    rev_col = random.choice(col_variations['revenue'])
    ebitda_col = random.choice(col_variations['ebitda'])
    debt_col = random.choice(col_variations['total_debt'])
    
    # Generate random financial figures
    revenue = np.random.randint(10000000, 500000000) # $10M to $500M
    # Make EBITDA roughly 10-30% of revenue
    ebitda = int(revenue * np.random.uniform(0.10, 0.30))
    # Make Debt roughly 2x-5x of EBITDA (Leverage)
    total_debt = int(ebitda * np.random.uniform(2.0, 5.0))
    
    # CHAOS INJECTION 1: Randomly make some data "dirty" (Text instead of numbers)
    # 5% chance we corrupt the debt figure with "USD" prefix
    if random.random() < 0.05:
        total_debt = f"USD {total_debt}"
        
    # CHAOS INJECTION 2: Randomly insert a "None" or missing value
    # 2% chance EBITDA is missing
    if random.random() < 0.02:
        ebitda = None

    # Create a mini DataFrame for this single client
    tmp_df = pd.DataFrame([{
        rev_col: revenue,
        ebitda_col: ebitda,
        debt_col: total_debt,
        'fiscal_year': 2025
    }])
    
    # Save to Excel
    file_path = os.path.join(folder_name, f"{client_id}_financials.xlsx")
    tmp_df.to_excel(file_path, index=False)

    # Progress tracker (prints every 100 files)
    if (i + 1) % 100 == 0:
        print(f"Generated {i + 1} files...")

print(f"Success! Created {len(clients_to_generate)} messy Excel files in the 'client_financials' folder.")