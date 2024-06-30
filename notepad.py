# %%
import pandas as pd

gspc = pd.read_csv("data/^GSPC.csv", index_col="Date", parse_dates=True)[["Adj Close"]]

# %%
