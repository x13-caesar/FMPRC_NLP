import pandas as pd

old = pd.read_csv('zyjh.csv', header=0)
new = pd.read_csv('new.csv', header=None)

merged = old.merge(new, how='outer')
old = merged.sort_values(by=['time']).reset_index().drop('index', axis=1,  inplace=True)
old.to_csv('old.csv')

