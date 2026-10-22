# 🏥 Healthcare Fraud Detection — SQL & Python Claims Analytics

A **SQL + Python analytics project** that detects fraudulent patterns in healthcare claims data — modeled after real-world compliance analytics used by CMS and insurance payers to surface high-risk providers for audit review.

Healthcare fraud — including overbilling, phantom billing, and imaging overutilization — costs the U.S. healthcare system **billions of dollars annually**. This project uses statistical SQL-based analysis to flag anomalies in provider behavior and procedure volumes, with Python for deeper investigation of flagged cases.

---

## 🔍 Key Analyses

| Analysis | What It Detects |
|---|---|
| 📊 **Provider Utilization** | Ranks providers by claim/procedure volume, surfacing those significantly above peer benchmarks |
| 🖼️ **Imaging Overutilization** | Flags repeated or excessive high-cost imaging that may indicate overbilling |
| 🚩 **Fraud-Pattern Queries** | Identifies duplicate billing, improbable procedure volumes, and known fraud indicators |

### Fraud Patterns Detected
- **Overbilling** — claims exceeding typical procedure rates or peer volumes
- **Phantom billing** — procedures billed but not clinically supported
- **Duplicate charges** — same procedure billed multiple times for same patient/date
- **Imaging overuse** — excessive MRI/CT scans relative to diagnosis codes
- **Provider outliers** — volume far above the statistical norm for specialty/region
---
## 🛠 Tech Stack

```
SQL (PostgreSQL) · Python (Pandas) · Statistical Anomaly Detection · Relational Schema Design
```

| Layer | Technology |
|---|---|
| Schema & queries | PostgreSQL / SQL |
| Investigation | Python + Pandas |
| Detection method | Statistical outlier analysis + rule-based fraud flags |

---

## 📁 Project Structure

```
healthcare-fraud-detection/
├── sql/
│   ├── 01_schema.sql               # Table definitions / database schema
│   ├── 02_load_data.sql            # Load claims data into tables
│   ├── 03_fraud_queries.sql        # Core fraud-detection queries
│   ├── provider_utilization.sql    # Provider-level utilization analysis
│   ├── imaging_overutilization.sql # Detection of imaging procedure overuse
│   └── schema.sql                  # Schema reference
└── src/
    └── investigate.py              # Python script to investigate flagged records
```

---

## 🚀 How to Run

```bash
# 1. Create schema and load data
psql -d your_database -f sql/01_schema.sql
psql -d your_database -f sql/02_load_data.sql

# 2. Run fraud-detection queries
psql -d your_database -f sql/03_fraud_queries.sql

# 3. Investigate flagged records
python src/investigate.py
```

---

## 📊 Sample Results

Running the SQL queries produces ranked outputs for compliance review:

- **Provider utilization query** — ranks providers by claim and procedure volume, surfacing those whose activity is well above their peer group
- **Imaging overutilization query** — highlights repeated or excessive high-cost imaging that may indicate systematic overbilling
- **Fraud-pattern queries** — flags records matching known fraud indicators such as duplicate or improbable billing
These outputs give a **prioritized shortlist of high-risk cases** for manual review by compliance teams.
---
## 💡 Real-World Relevance

This project mirrors workflows used in production by:
- **CMS (Centers for Medicare & Medicaid Services)** fraud analytics
- **Insurance payer** provider credentialing and audit teams
- **Healthcare compliance** departments running utilization management
---
## 👩‍💻 Author

**Sravani Kamjula** | Data Scientist · Applied AI & Data Systems
[LinkedIn](https://www.linkedin.com/in/sravani-kamjula-763285176/) · [Portfolio](https://sravaniportfoli.netlify.app/)
