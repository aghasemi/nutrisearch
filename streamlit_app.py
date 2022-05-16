import pandas as pd 
import duckdb, re, math, requests

import streamlit as st

import plotly.express as px 
from lxml.html.clean import Cleaner


def clean_html(raw_html):
    cleaner = Cleaner(remove_tags=["sup", "b"])
    return cleaner.clean_html(raw_html).decode("utf-8")

def extract_number(s, num_sep=',', dec_sep='.', is_float = False):
    s =  re.sub("[\[\)].*?[\)\]]", "", str(s))
    s = s.split(' ')[0]
    s = s.replace(num_sep, '')
    s = s.replace('%', '')
    s = s.replace('\xa0', '')
    s = s.replace('\U00002013', '-') 
    s = s.replace('−', '-')
    s = s.replace('-', '-')
    s = s.replace(dec_sep, '.')
    s = s.strip()
    s = 0.0 if s=='-' else float(s)
    return s if is_float else int(s) if not math.isnan(s) else 0

def get_types(df, allow_change = True):
    aliases = dict({})
    types_table = []
    for i,(col, dt) in enumerate(df.dtypes.items()):
        alias = f'{{C{i+1}}}'
        dt = str(dt)
        dt = 'Integer' if 'int' in dt else 'Float' if 'float' in dt  else 'Text'
        aliases[alias] = f'"{col}"'

        #c1, c2 =  st.columns([1,3])
        #c1.markdown(f'{i+1:3}. {alias} {col}')
        dt = st.selectbox(label = f'Please choose data type for {col}', options = data_types_list, key = col, index = data_types.get(dt, 0)) \
            if allow_change else dt
        
        if dt=='Text': df[col] = df[col].apply(lambda s: re.sub("[\[].*?[\]]", "", str(s)).strip('*').strip())
        if dt=='Integer': df[col] = df[col].apply(lambda s: extract_number(str(s), num_sep=num_sep, dec_sep = dec_sep, is_float = False))
        if dt=='Float': df[col] = df[col].apply(lambda s: extract_number(str(s), num_sep=num_sep, dec_sep = dec_sep, is_float = True))
        if dt=='Date': df[col] = pd.to_datetime(df[col].apply(lambda s: re.sub("[\[].*?[\]]", "", str(s)).strip('*').strip()), errors='coerce')

        types_table += [[alias, str(col), str(dt)]]

    return aliases, types_table

symbols = ['circle', 'square', 'diamond', 'cross', 'triangle-up', 'triangle-down', 'triangle-left', 'triangle-right', 
                                  'triangle-ne', 'triangle-nw', 'triangle-sw', 'triangle-se', 'pentagon', 'hexagon', 'hexagon2', 'hexagram', 'star', 'octagon']


st.set_page_config(layout='wide')

url = st.text_input(label='Please enter page address', value = 'https://en.wikipedia.org/wiki/List_of_cities_by_GDP')

with st.expander(label = 'Modify thousands and decimal separator character'):
    num_sep = st.selectbox(label = 'Thousands separator', options=[',', '.', '\xa0'], index=1 if '://de.' in url else 0)
    dec_sep = st.selectbox(label = 'Decimal separator', options=[',', '.'], index=0 if '://de.' in url else 1)


raw_html = requests.get(url).text


dfs = pd.read_html(url, thousands=num_sep, decimal=dec_sep)

indices = []

for i,df in enumerate(dfs):
    if len(df)<10: continue
    df.columns = [col if isinstance(col, str) else ' - '.join(dict.fromkeys(col)).strip() if isinstance(col, tuple) else str(col) for col in df.columns.values] # https://stackoverflow.com/questions/14507794/pandas-how-to-flatten-a-hierarchical-index-in-columns
    df.columns = [re.sub("[\[].*?[\]]", "", c) for c in df.columns.values]
    indices.append(i)


if len(indices) == 0:
    st.markdown(f'No table found in {url}')
else:

    tables = [f'{i} ({len(dfs[i])} rows. Columns: <{", ".join(dfs[i].columns.values)}>)' for i in indices]
    i = st.selectbox(label='Please choose the table in the page', options=tables, index = 0)
    i = int(i.split(' ')[0])
    T1  = dfs [i]


    

    data_types_list = ['Text', 'Integer', 'Float', 'Date']
    data_types = dict({x:i for i,x in enumerate(data_types_list)})

    with st.expander(label = 'Modify data types of columns'):
        aliases, types_table = get_types(T1)


    st.markdown('Columns')
    types_table_df = pd.DataFrame(data=types_table, columns=('Column Alias', 'Column Name', 'Column Type'), index = None)
    st.table(types_table_df)

    query = st.text_input(label= 'Please enter SQL query', value = 'SELECT  * from T1')

    for alias,column  in aliases.items(): query = query.replace(alias, column)

    print(query)
    try:
        result = duckdb.query(query).to_df()
        st.dataframe(result, width = 20 * len(''.join(result.columns.values)), height= 10 * len(result))
        _, types_table = get_types(result, allow_change = False)
        with st.expander(label='Plot the table', expanded=False):
        
            numerical_columns = [row[1] for row in types_table if row[2] in {'Float', 'Integer'}]
            text_columns = [''] + [row[1] for row in types_table if row[2] in {'Text'}]
            all_columns = [row[1] for row in types_table ]


            if len(numerical_columns)>1:

                x_column = st.selectbox('Please choose the column for the X axis', options=numerical_columns, index=0, key = 0)
                y_column = st.selectbox('Please choose the columen for the Y axis', options=numerical_columns, index=1, key = 1)

                #size_column = st.selectbox('Please choose the columen for the blob size', options=[''] + numerical_columns, index=0)
                #color_column = st.selectbox('Please choose the columen for the blob color', options=[''] + numerical_columns, index=0)


                title_column = st.selectbox('Please choose the column for the blob title', options=text_columns, index=0, key = 2)
                

                fig = px.scatter(result, x=x_column, y=y_column, size=None, symbol= None, color= None ,log_y= False, log_x= False, height = 800, 
                                symbol_sequence= symbols, 
                                hover_name=None if len(title_column)==0 else title_column, hover_data ={x:True for x in  all_columns}
                                ) #,hover_data={'Model Family': True, 'Parameters': True, 'ImageNet Top1 Error': True, 'Inference Time': True, 'Feature Vector Size': True, 'Input Size': True, 'Log(Inference Time)': False, 'Input Size (Categorised)': False}
                #fig.layout.legend.x = 1.1
                #fig.layout.coloraxis.colorbar.y = .55
                fig.update_layout({'legend_orientation':'h'})

                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.markdown(f'SQL Error: {e}')

