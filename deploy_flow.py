from prefect import serve
from prefect_flow import cricket_etl_flow

if __name__ == "__main__":
    cricket_etl_flow.serve(
        name="cricket-etl-hourly",
        interval=3600,  # run every 3600 seconds = 1 hour
    )