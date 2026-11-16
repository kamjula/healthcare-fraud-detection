-- ============================================================
-- 02_load_data.sql  |  Load the synthetic claims CSV
-- Run after generating data: python -m src.data.generate_synthetic
-- ============================================================

-- Stage the raw CSV (PostgreSQL COPY; adjust path as needed).
-- The CSV has both provider and claim fields denormalized, so we
-- load it into a staging table and split into the normalized tables.

CREATE TEMP TABLE staging_claims (
    claim_id           VARCHAR(20),
    provider_id        VARCHAR(16),
    npi                BIGINT,
    provider_specialty VARCHAR(64),
    patient_id         VARCHAR(20),
    cpt_code           INTEGER,
    icd10_code         VARCHAR(10),
    claim_date         DATE,
    units              INTEGER,
    billed_amount      NUMERIC(12,2),
    paid_amount        NUMERIC(12,2),
    is_fraud           INTEGER
);

\copy staging_claims FROM 'data/sample_claims.csv' WITH (FORMAT csv, HEADER true);

INSERT INTO providers (provider_id, npi, provider_specialty)
SELECT DISTINCT provider_id, npi, provider_specialty
FROM staging_claims
ON CONFLICT (provider_id) DO NOTHING;

INSERT INTO claims (claim_id, provider_id, patient_id, cpt_code,
                    icd10_code, claim_date, units, billed_amount, paid_amount)
SELECT claim_id, provider_id, patient_id, cpt_code,
       icd10_code, claim_date, units, billed_amount, paid_amount
FROM staging_claims
ON CONFLICT (claim_id) DO NOTHING;
