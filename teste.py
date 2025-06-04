import pandas as pd

df = pd.read_excel('fluxo_de_caixa.xlsx', skiprows=0)
print(df.columns)
