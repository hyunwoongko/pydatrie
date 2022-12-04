import pandas as pd

df = pd.read_csv("data.csv")
df = df[['a', 'b', 'c', 'd', 'e']]
df.to_csv("data.csv", index=False)
