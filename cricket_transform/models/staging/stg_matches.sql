SELECT
    match_id,
    match_name,
    match_type,
    status,
    venue,
    match_date
FROM
    {{ source('cricket_raw', 'matches') }}
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY match_id
    ORDER BY match_id
) = 1