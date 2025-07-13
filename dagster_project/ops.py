import os
from dagster import op, Out, In, Nothing
import subprocess

# Define paths relative to the Docker container's /app directory
SCRIPTS_DIR = "/app/scripts"
DBT_PROJECT_DIR = "/app/dbt_project"
FASTAPI_APP_DIR = "/app/fastapi_app"

@op(out=Out(Nothing))
def scrape_telegram_data_op():
    """
    Dagster op to execute the Telegram data scraping script.
    """
    print("Executing Telegram data scraping...")
    try:
        # Ensure the script is executable or run with python
        result = subprocess.run(
            ["python", os.path.join(SCRIPTS_DIR, "telegram_scraper.py")],
            check=True,
            capture_output=True,
            text=True
        )
        print("Telegram scraping output:\n", result.stdout)
        if result.stderr:
            print("Telegram scraping errors:\n", result.stderr)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Telegram scraping failed: {e.stderr}")
    print("Telegram data scraping completed.")

@op(out=Out(Nothing), ins={"start": In(Nothing)})
def load_raw_to_postgres_op():
    """
    Dagster op to load raw JSON data from data lake to PostgreSQL.
    """
    print("Executing raw data loading to PostgreSQL...")
    try:
        result = subprocess.run(
            ["python", os.path.join(SCRIPTS_DIR, "load_raw_to_postgres.py")],
            check=True,
            capture_output=True,
            text=True
        )
        print("Raw data loading output:\n", result.stdout)
        if result.stderr:
            print("Raw data loading errors:\n", result.stderr)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Raw data loading failed: {e.stderr}")
    print("Raw data loading to PostgreSQL completed.")

@op(out=Out(Nothing), ins={"start": In(Nothing)})
def run_dbt_transformations_op():
    """
    Dagster op to run dbt transformations.
    """
    print("Executing dbt transformations...")
    try:
        # Ensure dbt is installed and configured in the container
        result = subprocess.run(
            ["dbt", "build", "--project-dir", DBT_PROJECT_DIR], # 'dbt build' runs models, tests, snapshots, seeds
            check=True,
            capture_output=True,
            text=True
        )
        print("dbt transformations output:\n", result.stdout)
        if result.stderr:
            print("dbt transformations errors:\n", result.stderr)
    except subprocess.CalledProcessError as e:
        raise Exception(f"dbt transformations failed: {e.stderr}")
    print("dbt transformations completed.")

@op(out=Out(Nothing), ins={"start": In(Nothing)})
def run_yolo_enrichment_op():
    """
    Dagster op to run YOLOv8 object detection for data enrichment.
    """
    print("Executing YOLOv8 enrichment...")
    try:
        result = subprocess.run(
            ["python", os.path.join(SCRIPTS_DIR, "yolo_enrichment.py")],
            check=True,
            capture_output=True,
            text=True
        )
        print("YOLO enrichment output:\n", result.stdout)
        if result.stderr:
            print("YOLO enrichment errors:\n", result.stderr)
    except subprocess.CalledProcessError as e:
        raise Exception(f"YOLO enrichment failed: {e.stderr}")
    print("YOLOv8 enrichment completed.")

@op(out=Out(Nothing), ins={"start": In(Nothing)})
def start_fastapi_op():
    """
    Dagster op to start the FastAPI application.
    Note: This is typically for development/testing. In production, FastAPI runs as a separate service.
    """
    print("Starting FastAPI application...")
    try:
        # This will block, so it's not ideal for a typical Dagster op in a production pipeline
        # unless it's a long-running service op.
        # For demonstration, we'll just print the command.
        print(f"To run FastAPI, execute: uvicorn {FASTAPI_APP_DIR.replace('/app/', '')}.main:app --host 0.0.0.0 --port 8000")
        # Example of how you might run it in a blocking way (not recommended for typical ops):
        # subprocess.run(
        #     ["uvicorn", f"{FASTAPI_APP_DIR.replace('/app/', '')}.main:app", "--host", "0.0.0.0", "--port", "8000"],
        #     check=True
        # )
    except Exception as e:
        raise Exception(f"Failed to start FastAPI: {e}")
    print("FastAPI application started (or command printed).")
