-- ============================================================
-- 03_fraud_queries.sql  |  Analytical fraud-detection queries
-- These mirror the Python rule logic in pure SQL for analysts/BI.
-- ============================================================

-- ------------------------------------------------------------
-- 1. Imaging overutilization: providers whose imaging share of
--    claims (CPT 70000-79999) is well above peers.
-- ------------------------------------------------------------
WITH provider_imaging AS (
    SELECT
        provider_id,
        provider_specialty,
        COUNT(*)                                              AS total_claims,
        SUM(CASE WHEN cpt_code BETWEEN 70000 AND 79999
                 THEN 1 ELSE 0 END)                           AS imaging_claims,
        ROUND(AVG(CASE WHEN cpt_code BETWEEN 70000 AND 79999
                 THEN 1.0 ELSE 0.0 END), 3)                   AS imaging_ratio
    FROM claims c
    JOIN providers p USING (provider_id)
    GROUP BY provider_id, provider_specialty
)
SELECT *
FROM provider_imaging
WHERE total_claims >= 20
  AND imaging_ratio >= 0.45
ORDER BY imaging_ratio DESC;

-- ------------------------------------------------------------
-- 2. High billed amount vs the median for the same CPT code.
-- ------------------------------------------------------------
WITH cpt_median AS (
    SELECT cpt_code,
           PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY billed_amount)
               AS median_billed
    FROM claims
    GROUP BY cpt_code
)
SELECT c.claim_id, c.provider_id, c.cpt_code,
       c.billed_amount, m.median_billed,
       ROUND(c.billed_amount / NULLIF(m.median_billed, 0), 2) AS ratio
FROM claims c
JOIN cpt_median m USING (cpt_code)
WHERE c.billed_amount >= 4 * m.median_billed
ORDER BY ratio DESC
LIMIT 100;

-- ------------------------------------------------------------
-- 3. Possible duplicate billing: same provider, patient, CPT, date.
-- ------------------------------------------------------------
SELECT provider_id, patient_id, cpt_code, claim_date,
       COUNT(*) AS occurrences,
       STRING_AGG(claim_id, ', ') AS claim_ids
FROM claims
GROUP BY provider_id, patient_id, cpt_code, claim_date
HAVING COUNT(*) > 1
ORDER BY occurrences DESC;

-- ------------------------------------------------------------
-- 4. Excessive units on a single claim.
-- ------------------------------------------------------------
SELECT claim_id, provider_id, cpt_code, units, billed_amount
FROM claims
WHERE units > 12
ORDER BY units DESC;

-- ------------------------------------------------------------
-- 5. Inflated billed-vs-paid pattern by provider.
-- ------------------------------------------------------------
SELECT provider_id,
       COUNT(*)                                          AS total_claims,
       ROUND(AVG(billed_amount / NULLIF(paid_amount, 0)), 2)
                                                         AS avg_billed_to_paid
FROM claims
GROUP BY provider_id
HAVING COUNT(*) >= 20
   AND AVG(billed_amount / NULLIF(paid_amount, 0)) >= 3.0
ORDER BY avg_billed_to_paid DESC;

-- ------------------------------------------------------------
-- 6. Top flagged claims (requires claim_scores populated).
-- ------------------------------------------------------------
SELECT s.claim_id, s.provider_id_placeholder AS provider_id,
       s.final_risk_score, s.ml_probability, s.rule_score, s.rule_reasons
FROM (
    SELECT cs.*, c.provider_id AS provider_id_placeholder
    FROM claim_scores cs
    JOIN claims c USING (claim_id)
) s
WHERE s.flagged = TRUE
ORDER BY s.final_risk_score DESC
LIMIT 50;
