from dagster import repository, define_asset_job, AssetSelection, ScheduleDefinition

from .ops import (
    scrape_telegram_data_op,
    load_raw_to_postgres_op,
    run_dbt_transformations_op,
    run_yolo_enrichment_op,
    start_fastapi_op # This op would typically be for development/testing, not production orchestration
)

@repository
def telegram_data_pipeline_repo():
    """
    Defines the Dagster repository containing jobs and schedules for the Telegram data pipeline.
    """
    # Define a job that orchestrates the entire ELT and enrichment process
    telegram_elt_job = define_asset_job(
        name="telegram_elt_and_enrichment_job",
        selection=AssetSelection.all(), # Selects all assets defined in ops (conceptual)
        description="Orchestrates the end-to-end Telegram data pipeline."
    )

    # Define the ops and their dependencies
    # In a real Dagster project, you'd define these as assets or ops with explicit dependencies
    # For simplicity, here's a conceptual job definition:
    @define_asset_job(name="full_data_pipeline")
    def full_data_pipeline_job():
        # Define the execution order of your ops
        # This is a simplified representation; in a real Dagster graph,
        # you'd use `>>` or `<<` operators to define dependencies.
        # For example: scrape_telegram_data_op() >> load_raw_to_postgres_op()
        scrape_telegram_data_op()
        load_raw_to_postgres_op()
        run_dbt_transformations_op()
        run_yolo_enrichment_op()
        # start_fastapi_op() # FastAPI is usually a long-running service, not an op in a batch job

    # Define a schedule for the full pipeline
    daily_pipeline_schedule = ScheduleDefinition(
        job=full_data_pipeline_job,
        cron_schedule="0 0 * * *",  # Run daily at midnight UTC
        name="daily_telegram_pipeline_schedule",
        description="Runs the full Telegram data pipeline daily."
    )

    return [
        full_data_pipeline_job,
        daily_pipeline_schedule
    ]
