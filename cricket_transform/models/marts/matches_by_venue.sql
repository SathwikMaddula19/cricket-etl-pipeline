SELECT
    venue,
    COUNT(*) AS match_count
FROM
    {{ ref('stg_matches') }}
WHERE
    venue IS NOT NULL AND venue != ''
GROUP BY
    venue
ORDER BY
    match_count DESC