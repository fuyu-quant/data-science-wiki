! pip install -U pandas_profiling

import pandas as pd
import pandas_profiling as pdp

df = pd.read_csv("https://raw.githubusercontent.com/vertica/Machine-Learning-Examples/master/data/titanic_training.csv")
pdp.ProfileReport(df)
