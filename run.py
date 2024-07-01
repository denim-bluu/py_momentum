import click
from cli.backtest import run_backtest
from cli.process_data import process_data
from cli.download_data import download_data


@click.group()
def cli():
    pass


cli.add_command(run_backtest, name="backtest")
cli.add_command(process_data, name="process")
cli.add_command(download_data, name="download")

if __name__ == "__main__":
    cli()
