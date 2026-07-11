from prefect import flow, task
from raw_ingest import extract_matches, transform_matches, load_matches


@task(retries=2, retry_delay_seconds=10)
def extract_task():
    return extract_matches()


@task
def transform_task(matches):
    return transform_matches(matches)


@task
def load_task(rows):
    return load_matches(rows)


@flow(name="cricket-etl-pipeline")
def cricket_etl_flow():
    matches = extract_task()
    if not matches:
        print("No matches extracted. Ending flow early.")
        return

    rows = transform_task(matches)
    if not rows:
        print("No valid rows after transform. Ending flow early.")
        return

    load_task(rows)


if __name__ == "__main__":
    cricket_etl_flow()