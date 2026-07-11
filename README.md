# Cricket ETL Pipeline

An automated data pipeline that extracts live cricket match data from a public API, loads it into a cloud data warehouse, transforms it into clean analytics-ready tables, and runs on an automated schedule.

## Architecture

```
CricAPI  →  Python (Extract/Transform/Load)  →  BigQuery (raw)  →  dbt (staging → marts)
                          ↑
                     Prefect (scheduling, retries, monitoring)
```

## What it does

1. **Extract**: Pulls live match data (teams, venues, match status, scores) from the [CricAPI](https://www.cricapi.com/) public API
2. **Load**: Batch-loads raw JSON records into a Google BigQuery dataset (`cricket_raw.matches`)
3. **Transform**: Uses [dbt](https://www.getdbt.com/) to:
   - Deduplicate raw records into a clean staging table (`stg_matches`)
   - Aggregate cleaned data into an analytics-ready mart (`matches_by_venue`)
4. **Orchestrate**: Uses [Prefect](https://www.prefect.io/) to schedule the pipeline to run automatically, with built-in retry logic for network failures

## Tech stack

- **Language**: Python 3.12
- **Cloud data warehouse**: Google BigQuery
- **Transformation**: dbt (data build tool)
- **Orchestration**: Prefect
- **Data source**: CricAPI (REST API)
- **Version control**: Git / GitHub

## Key engineering decisions

- **Batch loading over streaming inserts**: BigQuery's streaming insert API requires a paid billing tier. The pipeline uses `load_table_from_json()` batch jobs instead — free-tier compatible and the standard approach for scheduled batch pipelines.
- **Deduplication via dbt, not application code**: Rather than handling duplicate detection in Python, raw data is loaded as-is and deduplication logic lives in a dbt SQL model (`QUALIFY ROW_NUMBER()`), keeping the raw layer immutable and the transformation logic version-controlled and testable.
- **Graceful failure handling**: Every stage (extract, transform, load) catches and logs errors independently rather than crashing the whole run, so a single bad API response or malformed record doesn't take down the entire pipeline.
- **Retry logic at the orchestration layer**: Prefect automatically retries the extract step on failure (e.g., API timeout) rather than requiring manual re-runs.

## Project structure

```
cricket-etl-pipeline/
├── raw_ingest.py           # Core Extract → Transform → Load functions
├── prefect_flow.py         # Prefect flow wrapping the pipeline with retries
├── deploy_flow.py          # Prefect deployment/scheduling entry point
├── setup_bigquery.py       # One-time BigQuery dataset/table setup
├── test_api.py             # Standalone API connectivity check
├── cricket_transform/      # dbt project
│   └── models/
│       ├── staging/
│       │   ├── stg_matches.sql
│       │   └── sources.yml
│       └── marts/
│           └── matches_by_venue.sql
└── .env                    # API credentials (not committed)
```

## Running it locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set up your .env file with CRICAPI_KEY=your_key_here

# One-time BigQuery setup
python setup_bigquery.py

# Run the pipeline once
python raw_ingest.py

# Run dbt transformations
cd cricket_transform
dbt run

# Start the scheduled orchestration
cd ..
python deploy_flow.py
```

## Future improvements

- Add dbt tests for data quality checks (null checks, uniqueness constraints)
- Expand to historical match data and player-level statistics
- Add a lightweight BI dashboard on top of the mart tables
