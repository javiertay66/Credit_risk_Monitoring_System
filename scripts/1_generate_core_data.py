import sqlite3
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

print("Initializing Core Banking System Simulation...")

# --- CONFIGURATION ---
# We are simulating a specialized lending desk portfolio.
# 1,000 is a realistic portfolio size for a single operational team to monitor.
num_clients = 1000 

# Generating IDs like 'CORP_00001'
client_ids = [f"CORP_{str(i).zfill(5)}" for i in range(1, num_clients + 1)]

# Expanded sectors reflecting a global portfolio
industries = [
    "Manufacturing", "Commercial Real Estate", "Technology", 
    "Healthcare", "Retail", "Energy", "Financials", 
    "Aviation", "Logistics", "Telecommunications"
]

np.random.seed(42) 

# Corporate facilities are usually larger. Let's simulate loans between $5M and $250M
facility_amounts = np.random.randint(5000000, 250000000, size=num_clients) 
interest_margins = np.round(np.random.uniform(1.0, 6.5, size=num_clients), 2) 

start_date = datetime(2026, 1, 1)
end_date = datetime(2032, 12, 31)
days_between = (end_date - start_date).days

# Optimize the date generation for the dataset
random_days = np.random.randint(0, days_between, size=num_clients)
maturity_dates = [(start_date + timedelta(days=int(days))).strftime('%Y-%m-%d') for days in random_days]

# Build the structured table
df = pd.DataFrame({
    'client_id': client_ids,
    'industry_sector': np.random.choice(industries, size=num_clients),
    'facility_amount_usd': facility_amounts,
    'interest_rate_margin_pct': interest_margins,
    'maturity_date': maturity_dates
})

# Connect to SQLite and write the data
conn = sqlite3.connect('core_banking.db')
df.to_sql('facility_details', conn, index=False, if_exists='replace')
conn.close()

print(f"Success! Generated {num_clients} loan records and saved to 'core_banking.db'.")