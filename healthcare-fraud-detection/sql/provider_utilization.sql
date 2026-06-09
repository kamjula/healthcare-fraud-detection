-- Provider utilization summary plus a duplicate-claim detector.

-- 1) Provider-level utilization profile (useful as model features / triage).
SELECT
    c.provider_npi,
    p.provider_specialty,
    COUNT(*)                                  AS total_claims,
    COUNT(DISTINCT c.patient_id)              AS distinct_patients,
    ROUND(AVG(c.billed_amount), 2)            AS avg_billed,
    ROUND(SUM(c.billed_amount), 2)            AS total_billed,
    ROUND(COUNT(*)::numeric
          / NULLIF(COUNT(DISTINCT c.patient_id), 0), 2) AS claims_per_patient,
    SUM(CASE WHEN c.billed_amount > 5000 THEN 1 ELSE 0 END) AS high_dollar_claims
FROM claims c
JOIN providers p ON p.provider_npi = c.provider_npi
GROUP BY c.provider_npi, p.provider_specialty
ORDER BY total_billed DESC;

-- 2) Duplicate claims: same patient + CPT + service_date billed more than once.
SELECT
    patient_id,
    cpt_code,
    service_date,
    COUNT(*)                  AS duplicate_count,
    ARRAY_AGG(claim_id)       AS claim_ids,
    SUM(billed_amount)        AS total_billed
FROM claims
GROUP BY patient_id, cpt_code, service_date
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC, total_billed DESC;
