-- Healthcare fraud detection — warehouse schema
-- Target: PostgreSQL (adjust types for other engines as needed).

CREATE TABLE IF NOT EXISTS providers (
    provider_npi        VARCHAR(10) PRIMARY KEY,
    provider_name       VARCHAR(255),
    provider_specialty  VARCHAR(100),
    state               CHAR(2),
    enrolled_date       DATE
);

CREATE TABLE IF NOT EXISTS claims (
    claim_id        VARCHAR(32) PRIMARY KEY,
    provider_npi    VARCHAR(10) NOT NULL REFERENCES providers (provider_npi),
    patient_id      VARCHAR(32) NOT NULL,
    cpt_code        INTEGER     NOT NULL,
    icd10_code      VARCHAR(10),
    billed_amount   NUMERIC(12, 2) NOT NULL CHECK (billed_amount >= 0),
    paid_amount     NUMERIC(12, 2) NOT NULL CHECK (paid_amount >= 0),
    units           INTEGER     NOT NULL CHECK (units > 0),
    service_date    DATE        NOT NULL,
    place_of_service VARCHAR(10),
    created_at      TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

-- Investigation outcomes feed back into model training.
CREATE TABLE IF NOT EXISTS investigations (
    investigation_id SERIAL PRIMARY KEY,
    claim_id        VARCHAR(32) NOT NULL REFERENCES claims (claim_id),
    fraud_score     NUMERIC(5, 4),
    outcome         VARCHAR(20),   -- 'confirmed_fraud' | 'cleared' | 'pending'
    reviewed_by     VARCHAR(64),
    reviewed_at     TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_claims_provider ON claims (provider_npi);
CREATE INDEX IF NOT EXISTS idx_claims_patient  ON claims (patient_id);
CREATE INDEX IF NOT EXISTS idx_claims_cpt      ON claims (cpt_code);
CREATE INDEX IF NOT EXISTS idx_claims_service_date ON claims (service_date);
