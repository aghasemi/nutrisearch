import pandas as pd 
import duckdb, re

import streamlit as st


st.set_page_config(layout='wide')

url = st.text_input(label='Please enter page address', value = 'https://en.wikipedia.org/wiki/List_of_largest_cities')

dfs = pd.read_html(url)

indices = [i for i,df in enumerate(dfs) if len(df)>10 ]
i = st.selectbox(label='Please choose the table in the page', options=indices, index  = 0)

df  = dfs [i]


df.columns = [col if isinstance(col, str) else ' - '.join(dict.fromkeys(col)).strip() for col in df.columns.values] # https://stackoverflow.com/questions/14507794/pandas-how-to-flatten-a-hierarchical-index-in-columns
 df.columns = [re.sub("[\[].*?[\]]", "", c) for c in df.columns.values]

print(df.columns)

aliases = dict({})
md_table = []
for i,(col, dt) in enumerate(df.dtypes.items()):
    alias = f'C{i+1}'
    dt = str(dt)
    dt = 'Text' if dt=='object' else 'Number' if 'float' in dt else dt
    md_table += [[alias, str(col), str(dt)]]
    aliases[alias] = f'"{col}"'

st.markdown('Columns')
md_table = pd.DataFrame(data=md_table, columns=('Column Alias', 'Column Name', 'Column Type'), index = None)
st.table(md_table)

query = st.text_input(label= 'Please enter SQL query', value = 'SELECT  * from df')

for alias,column  in aliases.items(): query = query.replace(alias, column)

print(query)


st.write(duckdb.query(query).to_df())
