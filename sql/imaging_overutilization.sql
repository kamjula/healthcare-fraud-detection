-- Imaging overutilization: providers billing an unusually high number of
-- imaging studies (radiology CPT range 70010–79999) per distinct patient.
-- Mirrors the imaging_overutilization rule in the Python engine.

WITH provider_imaging AS (
    SELECT
        c.provider_npi,
        p.provider_specialty,
        COUNT(*) FILTER (WHERE c.cpt_code BETWEEN 70010 AND 79999) AS imaging_claims,
        COUNT(DISTINCT c.patient_id)                                AS distinct_patients,
        SUM(c.billed_amount) FILTER (WHERE c.cpt_code BETWEEN 70010 AND 79999) AS imaging_billed
    FROM claims c
    JOIN providers p ON p.provider_npi = c.provider_npi
    GROUP BY c.provider_npi, p.provider_specialty
)
SELECT
    provider_npi,
    provider_specialty,
    imaging_claims,
    distinct_patients,
    ROUND(imaging_claims::numeric / NULLIF(distinct_patients, 0), 2) AS imaging_per_patient,
    imaging_billed
FROM provider_imaging
WHERE imaging_claims::numeric / NULLIF(distinct_patients, 0) > 3   -- threshold
ORDER BY imaging_per_patient DESC;
