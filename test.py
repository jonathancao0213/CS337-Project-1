import numpy as np
import pandas as pd 

df = pd.read_json('../gg2013.json')
df = df['text']
print(df.head())

# filter by key