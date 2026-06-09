-- ============================================================
-- 01_schema.sql  |  Healthcare Fraud Detection — table schema
-- Dialect: PostgreSQL (ANSI-friendly; adjust types for others)
-- ============================================================

CREATE TABLE IF NOT EXISTS providers (
    provider_id        VARCHAR(16) PRIMARY KEY,
    npi                BIGINT       NOT NULL,
    provider_specialty VARCHAR(64),
    region             VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS claims (
    claim_id        VARCHAR(20) PRIMARY KEY,
    provider_id     VARCHAR(16) NOT NULL REFERENCES providers(provider_id),
    patient_id      VARCHAR(20) NOT NULL,
    cpt_code        INTEGER     NOT NULL,
    icd10_code      VARCHAR(10),
    claim_date      DATE        NOT NULL,
    units           INTEGER     NOT NULL DEFAULT 1,
    billed_amount   NUMERIC(12,2) NOT NULL CHECK (billed_amount >= 0),
    paid_amount     NUMERIC(12,2) NOT NULL CHECK (paid_amount  >= 0)
);

-- Scoring output written back by the pipeline (optional).
CREATE TABLE IF NOT EXISTS claim_scores (
    claim_id          VARCHAR(20) PRIMARY KEY REFERENCES claims(claim_id),
    ml_probability    NUMERIC(6,4),
    rule_score        NUMERIC(6,4),
    final_risk_score  NUMERIC(6,4),
    flagged           BOOLEAN,
    rule_reasons      TEXT,
    scored_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_claims_provider ON claims(provider_id);
CREATE INDEX IF NOT EXISTS idx_claims_cpt      ON claims(cpt_code);
CREATE INDEX IF NOT EXISTS idx_claims_date     ON claims(claim_date);
