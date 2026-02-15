# 🏦 End-to-End Operations Credit Risk Engine 

> **"From Messy Data to Executive Insight: Automating the Credit Risk Lifecycle."**

---

## 📌 Executive Summary

**Role Simulation:** Operations Analyst / Risk Analyst  
**Goal:** Automate the manual credit review process for a simulated corporate loan book.

In the real world, banks struggle with fragmented data—internal loan records sit in SQL databases, while client financial statements arrive in messy, unstandardized CSV/Excel files. This project builds a **fully automated risk monitoring pipeline** that:

1. **Ingests & Standardizes** raw simulated banking data.
2. **Calculates** key risk metrics (EBITDA, Leverage, ICR).
3. **Computes** IFRS 9 Expected Credit Loss (ECL) provisions.
4. **Visualizes** portfolio health in an interactive **Power BI Command Center**.

---

## 📂 Repository Structure

This project is structured to mimic a production-grade ETL pipeline:

```text
├── 📁 client_financials/       # [Source B] 800+ simulated external client financial statements (Unstructured CSVs)
├── 📁 data/
│   ├── raw/                    # [Source A] core_banking.db (Simulated internal loan book)
│   └── processed/              # Final Analytical Dataset (Cleaned & Merged for Power BI)
├── 📁 dashboard/               # Executive Risk Dashboard (.pbix) & Snapshots
├── 📁 scripts/                 # The Python ETL & Calculation Engine (Steps 1-4)
└── README.md                   # System Documentation
```

---

## ⚙️ The Engineering Pipeline

The system follows a strict 4-step operational workflow, automated via Python scripts in the `scripts/` folder.

### Phase 1: Simulation (Creating the Chaos)

**Objective:** Simulate the "messy reality" of banking operations.

**Action:** Generated a SQL database (`core_banking.db`) representing the internal loan book and 800 distinct client CSV files representing external financial submissions.

**Challenge Solved:** Deliberately introduced data quality issues (e.g., inconsistent column names like `Rev`, `Total_Rev`, `Revenue`) to test the robustness of the ETL pipeline.

---

### Phase 2: ETL & Data Cleaning

**Objective:** Ingest and standardize disparate data sources.

**Action:**

- **SQL Extraction:** Queried the internal loan book to get Exposure at Default (EAD).
- **Fuzzy Matching:** Implemented Python logic to map inconsistent CSV headers to a standard schema (`Revenue`, `EBITDA`, `Total Debt`).
- **Merging:** Joined Internal Data (Loans) with External Data (Financials) on `Client_ID`.

---

### Phase 3: The Risk Engine (The Logic Layer)

**Objective:** Apply Basel III / IFRS 9 logic to assess creditworthiness.

**Action:** Calculated the following risk metrics for every client:

#### A. Financial Health Ratios

**Interest Coverage Ratio (ICR):**

$$
\text{ICR} = \frac{\text{EBITDA}}{\text{Interest Expense}}
$$

Measures the client's ability to pay interest.

**Leverage Ratio:**

$$
\text{Leverage} = \frac{\text{Total Debt}}{\text{EBITDA}}
$$

Measures the client's debt load relative to earnings.

---

#### B. Risk Grading & Probability of Default (PD)

Clients are segmented into internal rating buckets based on their ratios:

| Rating              | Criteria                            | PD (Probability of Default) |
|---------------------|-------------------------------------|----------------------------|
| Grade A (Safe)      | Leverage < 2.5x AND ICR > 3.0x     | 1.0%                       |
| Grade B (Warning)   | Leverage < 4.0x AND ICR > 1.5x     | 5.0%                       |
| Grade C (Critical)  | Failed above criteria               | 15.0%                      |

---

#### C. IFRS 9 Expected Credit Loss (ECL)

Calculated the capital provision required using the Foundation IRB formula:

$$
\text{ECL} = \text{EAD} \times \text{PD} \times \text{LGD}
$$

- **EAD (Exposure at Default):** Facility Amount from SQL DB.
- **PD:** Derived from the Risk Grade above.
- **LGD (Loss Given Default):** Fixed at 45% (Basel Standard for Senior Unsecured Debt).

---

### Phase 4: Executive Reporting

**Objective:** Visualize the data for stakeholders and management.

**Action:** Validated data types and exported the final dataset to `final_dashboard_data.csv` for Power BI ingestion.

---

## 📊 Dashboard Visuals

The final output is the **Credit Risk Command Center**.

<img width="1732" height="963" alt="image" src="https://github.com/user-attachments/assets/ec9c7079-cd63-4c87-a30d-f5077a659d7b" />

### Key Insights Delivered:

- **Total Portfolio Exposure:** Aggregated view of the loan book.
- **The "Red" Number:** Real-time ECL Provision calculation.
- **Concentration Risk:** Visual breakdown of risk by Industry Sector.
- **Actionable "Hit List":** Automatic flagging of clients with Critical Watchlist status.

---

## 📈 Technical Highlights

- **Data Volume:** 800+ client files, $3.5B+ simulated exposure
- **Automation:** End-to-end Python pipeline with zero manual intervention
- **Compliance:** IFRS 9 and Basel III aligned calculations
- **Scalability:** Modular design supports additional risk metrics

Author:
Javier Tay Yu Xiang
NTU Year 3 Economics & Data Science
Aspiring Operations Analyst 
