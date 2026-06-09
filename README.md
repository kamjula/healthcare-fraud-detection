# Healthcare Fraud Detection

A data analytics project that detects potentially fraudulent patterns in healthcare claims data using **SQL** and **Python**. The project builds a relational schema, loads claims data, and runs targeted analytical queries to surface providers and procedures with suspicious utilization patterns.

## Overview

Healthcare fraud — such as overbilling, phantom billing, and overutilization of high-cost procedures — costs the system billions each year. This project uses SQL-based analytics to flag anomalies in provider behavior and procedure volumes, with a Python script to support deeper investigation of flagged cases.

## Tech Stack

- **SQL** — schema design, data loading, and fraud-detection queries
- **Python** — investigation and analysis of flagged records
- **Analytics** — provider utilization and imaging overutilization analysis
 
## Project Structure

    healthcare-fraud-detection/
    ├── sql/
    │   ├── 01_schema.sql               # Table definitions / database schema
    │   ├── 02_load_data.sql            # Load claims data into tables
    │   ├── 03_fraud_queries.sql        # Core fraud-detection queries
    │   ├── provider_utilization.sql    # Provider-level utilization analysis
    │   ├── imaging_overutilization.sql # Detection of imaging procedure overuse
    │   └── schema.sql                  # Schema reference
    └── src/
        └── investigate.py              # Script to investigate flagged records

## Key Analyses

- **Provider utilization** — identifies providers with abnormally high claim or procedure volumes relative to peers.
- **Imaging overutilization** — flags excessive or repeated high-cost imaging procedures.
- **Fraud-pattern queries** — surfaces records matching known fraud indicators (e.g., duplicate or improbable billing patterns).

## How to Run

Run the SQL files in order, then the Python script:

    psql -d your_database -f sql/01_schema.sql         # create the schema
    psql -d your_database -f sql/02_load_data.sql      # load claims data
    psql -d your_database -f sql/03_fraud_queries.sql  # run fraud-detection queries
    python src/investigate.py                          # investigate flagged records

Adjust the connection command to match your setup (e.g., MySQL, SQLite, etc.).

## Results

Running the SQL queries produces ranked lists of providers and procedures
that stand out from normal patterns:

- The provider utilization query ranks providers by claim and procedure
  volume, surfacing those whose activity is well above their peer group.
- The imaging overutilization query highlights repeated or excessive
  high-cost imaging that may indicate overbilling.
- The fraud-pattern queries flag records matching known fraud indicators
  such as duplicate or improbable billing.

These outputs give a prioritized shortlist of high-risk cases for manual review.




## Author

**Sravani Kamjula**

