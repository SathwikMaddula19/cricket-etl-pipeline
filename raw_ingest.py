import requests
from dotenv import load_dotenv
import os
from google.cloud import bigquery

# ---- Config ----
load_dotenv()
API_KEY = os.getenv("CRICAPI_KEY")
PROJECT_ID = "etl-pipeline-project-502102"
DATASET_ID = "cricket_raw"
TABLE_ID = "matches"
TABLE_REF = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

SCHEMA = [
    bigquery.SchemaField("match_id", "STRING"),
    bigquery.SchemaField("match_name", "STRING"),
    bigquery.SchemaField("match_type", "STRING"),
    bigquery.SchemaField("status", "STRING"),
    bigquery.SchemaField("venue", "STRING"),
    bigquery.SchemaField("match_date", "STRING"),
]


def extract_matches():
    """Pull current match data from CricAPI. Returns [] on failure instead of crashing."""
    url = "https://api.cricapi.com/v1/currentMatches"
    params = {"apikey": API_KEY, "offset": 0}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # catches HTTP errors like 404, 500
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network/API request failed: {e}")
        return []

    try:
        data = response.json()
    except ValueError:
        print("ERROR: API did not return valid JSON.")
        return []

    if data.get("status") != "success":
        print(f"ERROR: CricAPI returned failure status: {data.get('reason', 'unknown reason')}")
        return []

    matches = data.get("data", [])
    print(f"Extracted {len(matches)} matches from CricAPI.")
    return matches


def transform_matches(matches):
    """Reshape raw API matches into our BigQuery table format.
    Skips individual malformed matches instead of crashing the whole batch."""
    rows = []
    skipped = 0

    for match in matches:
        try:
            rows.append({
                "match_id": str(match.get("id", "")),
                "match_name": str(match.get("name", "")),
                "match_type": str(match.get("matchType", "")),
                "status": str(match.get("status", "")),
                "venue": str(match.get("venue", "")),
                "match_date": str(match.get("date", "")),
            })
        except Exception as e:
            print(f"WARNING: Skipped a malformed match record: {e}")
            skipped += 1

    print(f"Transformed {len(rows)} rows for loading. Skipped {skipped} malformed records.")
    return rows


def load_matches(rows):
    """Batch load rows into BigQuery. Returns False on failure instead of crashing."""
    if not rows:
        print("No rows to load — skipping BigQuery load.")
        return False

    try:
        client = bigquery.Client(project=PROJECT_ID)

        job_config = bigquery.LoadJobConfig(
            schema=SCHEMA,
            write_disposition="WRITE_APPEND",
        )

        load_job = client.load_table_from_json(rows, TABLE_REF, job_config=job_config)
        load_job.result()

        print(f"Loaded {len(rows)} rows into {TABLE_REF} successfully.")
        return True

    except Exception as e:
        print(f"ERROR: Failed to load rows into BigQuery: {e}")
        return False


def run_pipeline():
    """Run the full Extract -> Transform -> Load pipeline safely."""
    print("--- Pipeline run started ---")

    matches = extract_matches()
    if not matches:
        print("No matches extracted. Ending pipeline run early.")
        return

    rows = transform_matches(matches)
    if not rows:
        print("No valid rows after transform. Ending pipeline run early.")
        return

    success = load_matches(rows)

    if success:
        print("--- Pipeline run completed successfully ---")
    else:
        print("--- Pipeline run completed with errors ---")


if __name__ == "__main__":
    run_pipeline()