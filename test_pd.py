import pandas as pd
df = pd.DataFrame({'amfi_code': [1,1,2,2], 'date': pd.to_datetime(['2022-01-01', '2022-01-03', '2022-01-01', '2022-01-04']), 'nav': [10, 11, 20, 21]})
def fill_missing_dates(group):
    amfi_code = group.name
    min_date = group['date'].min()
    max_date = group['date'].max()
    full_dates = pd.date_range(min_date, max_date)
    group = group.set_index('date').reindex(full_dates).ffill()
    group = group.reset_index().rename(columns={'index': 'date'})
    group['amfi_code'] = amfi_code
    return group

df = df.groupby('amfi_code', group_keys=False).apply(fill_missing_dates)
print(df)
