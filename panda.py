import pandas as pd

import config

calls_df, = pd.read_html(config.URL1, header=0)

print(calls_df)