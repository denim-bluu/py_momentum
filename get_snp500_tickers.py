import click
import pandas as pd


def get_snp500_tickers():
    click.echo("Downloading S&P 500 tickers...")
    # Download S&P 500 tickers from Wikipedia
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    sp500_tickers = tables[0]["Symbol"].tolist()
    click.echo(f"Downloaded {len(sp500_tickers)} tickers.")

    # store to txt
    with open("snp500_tickers.txt", "w") as f:
        for ticker in sp500_tickers:
            f.write(f"{ticker}\n")
    return sp500_tickers


if __name__ == "__main__":
    get_snp500_tickers()
