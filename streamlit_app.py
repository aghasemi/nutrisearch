import pandas as pd 
import duckdb, re, math

import streamlit as st

def extract_number(s, num_sep=',', dec_sep='.', is_float = False):
    s =  re.sub("[\[\)].*?[\)\]]", "", str(s))
    s = s.split(' ')[0]
    s = s.replace(num_sep, '')
    s = s.replace('%', '')
    s = s.replace('\xa0', '')
    s = s.replace('\U00002013', '-') 
    s = s.replace('−', '-') 
    s = s.replace(dec_sep, '.')
    s = s.strip()
    s = float(s)
    return s if is_float else int(s) if not math.isnan(s) else 0



st.set_page_config(layout='wide')

url = st.text_input(label='Please enter page address', value = 'https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(PPP)_per_capita')

with st.expander(label = 'Modify thousands and decimal separator character'):
    num_sep = st.selectbox(label = 'Thousands separator', options=[',', '.', '\xa0'], index=0)
    dec_sep = st.selectbox(label = 'Thousands separator', options=[',', '.'], index=1)


dfs = pd.read_html(url, thousands=num_sep, decimal=dec_sep)

indices = [i for i,df in enumerate(dfs) if len(df)>10 ]

if len(indices) == 0:
    st.markdown(f'No table found in {url}')
else:

    i = st.selectbox(label='Please choose the table in the page', options=indices, index  = 0)

    T1  = dfs [i]


    T1.columns = [col if isinstance(col, str) else ' - '.join(dict.fromkeys(col)).strip() for col in T1.columns.values] # https://stackoverflow.com/questions/14507794/pandas-how-to-flatten-a-hierarchical-index-in-columns
    T1.columns = [re.sub("[\[].*?[\]]", "", c) for c in T1.columns.values]

    data_types_list = ['Text', 'Integer', 'Float']
    data_types = dict({x:i for i,x in enumerate(data_types_list)})

    with st.expander(label = 'Modify data types of columns'):
        aliases = dict({})
        md_table = []
        for i,(col, dt) in enumerate(T1.dtypes.items()):
            alias = f'C{i+1}'
            dt = str(dt)
            dt = 'Integer' if 'int' in dt else 'Float' if 'float' in dt  else 'Text'
            aliases[alias] = f'"{col}"'

            #c1, c2 =  st.columns([1,3])
            #c1.markdown(f'{i+1:3}. {alias} {col}')
            dt = st.selectbox(label = f'Please choose data type for {col}', options = data_types_list, key = col, index = data_types[dt])
            
            if dt=='Text': T1[col] = T1[col].apply(lambda s: re.sub("[\[].*?[\]]", "", str(s)).strip('*').strip())
            if dt=='Integer': T1[col] = T1[col].apply(lambda s: extract_number(str(s), num_sep=num_sep, dec_sep = dec_sep, is_float = False))
            if dt=='Float': T1[col] = T1[col].apply(lambda s: extract_number(str(s), num_sep=num_sep, dec_sep = dec_sep, is_float = True))
            
            md_table += [[alias, str(col), str(dt)]]


    st.markdown('Columns')
    md_table = pd.DataFrame(data=md_table, columns=('Column Alias', 'Column Name', 'Column Type'), index = None)
    st.table(md_table)

    query = st.text_input(label= 'Please enter SQL query', value = 'SELECT  * from T1')

    for alias,column  in aliases.items(): query = query.replace(alias, column)

    print(query)


    st.write(duckdb.query(query).to_df())
