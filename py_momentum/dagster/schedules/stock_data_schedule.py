from dagster import ScheduleDefinition, define_asset_job

stock_data_job = define_asset_job(
    "stock_data_job", selection=["stock_data", "processed_stock_data"]
)

stock_data_schedule = ScheduleDefinition(
    job=stock_data_job,
    cron_schedule="0 18 * * 1-5",  # Run at 6 PM on weekdays
)
