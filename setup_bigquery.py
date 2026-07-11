from google.cloud import bigquery

project_id = "etl-pipeline-project-502102"
dataset_id = "cricket_raw"
table_id = "matches"

# This automatically uses the credentials we just set up
client = bigquery.Client(project=project_id)

# Step 1: Create the dataset (like a "folder" for tables)
dataset_ref = f"{project_id}.{dataset_id}"
dataset = bigquery.Dataset(dataset_ref)
dataset.location = "US"

dataset = client.create_dataset(dataset, exists_ok=True)
print(f"Dataset created or already exists: {dataset_ref}")

# Step 2: Define the table schema (columns and their types)
schema = [
    bigquery.SchemaField("match_id", "STRING"),
    bigquery.SchemaField("match_name", "STRING"),
    bigquery.SchemaField("match_type", "STRING"),
    bigquery.SchemaField("status", "STRING"),
    bigquery.SchemaField("venue", "STRING"),
    bigquery.SchemaField("match_date", "STRING"),
]

table_ref = f"{project_id}.{dataset_id}.{table_id}"
table = bigquery.Table(table_ref, schema=schema)
table = client.create_table(table, exists_ok=True)
print(f"Table created or already exists: {table_ref}")

# Step 3: Insert one test row using a batch load job (works on free tier)
rows_to_insert = [
    {
        "match_id": "test123",
        "match_name": "Test Match A vs Test Match B",
        "match_type": "test",
        "status": "test status",
        "venue": "Test Venue",
        "match_date": "2026-07-11",
    }
]

job_config = bigquery.LoadJobConfig(
    schema=schema,
    write_disposition="WRITE_APPEND",  # add to table, don't overwrite
)

load_job = client.load_table_from_json(
    rows_to_insert, table_ref, job_config=job_config
)
load_job.result()  # waits for the job to finish

print("Test row inserted successfully via batch load.")