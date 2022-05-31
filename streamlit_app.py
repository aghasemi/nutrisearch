import pandas as pd 
import duckdb, re, math, requests

import streamlit as st

import plotly.express as px 


@st.cache()
def load_data():
    df2 = pd.read_csv('generic.csv')
    
    df2['keywords'] = df2['name'].apply(lambda x:  [w.title() for w in str(x).split(', ') if len(w)>0])

    kw = set([x for l in df2['keywords'] for x in l])

    
    
    return df2, kw

symbols = ['circle', 'square', 'diamond', 'cross', 'triangle-up', 'triangle-down', 'triangle-left', 'triangle-right', 
                                  'triangle-ne', 'triangle-nw', 'triangle-sw', 'triangle-se', 'pentagon', 'hexagon', 'hexagon2', 'hexagram', 'star', 'octagon']


st.set_page_config(layout='wide')

st.title('What I Eat: Search for Common Grovery Items by Their Nutritional Value')

with st.expander(label='About', expanded=False):
    st.markdown('''
        TODO 

        If you see issues or have comments, please [contact me](https://mobile.twitter.com/a_ghasemi). 
    ''')


data, keywords = load_data()

df = data.copy()

query = st.multiselect(label='What food item(s) are you looking for?', options = keywords, default=None)

df = df[ df['keywords'].apply(lambda ks: all([k in ks for k in query]) ) ] 

carb_range = st.slider(label='Specify the desired amount of carbohydrates in 100 grams serving', min_value=0, max_value=100, value=(0,100))
df = df.query(f"carbohydrate>={carb_range[0]} and carbohydrate<={carb_range[1]}")



if len(df)<100:
    sort_column = st.selectbox('Sort by ', options= ['calories', 'carbohydrate', 'total_fat'], format_func= lambda x: dict({'calories': 'Calories', 'carbohydrate': 'Carbohydrate', 'total_fat': 'Total Fat' })[x])
    df = df.sort_values(by = sort_column)
    for i,row in df.iterrows():
        with st.expander(label=f'{row["name"]}'): 
        
            st.markdown(f'_Calories_=__{row["calories"]}__ _Fat_=__{row["total_fat"]}__ _Carbs_=__{row["carbohydrate"]}__')
else:
    st.markdown('Please specify more details')
