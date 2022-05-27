import pandas as pd 
import duckdb, re, math, requests

import streamlit as st

import plotly.express as px 


@st.cache()
def load_data():
    df2 = pd.read_csv('https://www.dropbox.com/s/x1bpr7phh32mwwu/nutrition.csv?dl=1')
    df2  = df2[['name', 'calories', 'total_fat', 'saturated_fat', 'cholesterol', 'carbohydrate', 'fiber', 'sugars']]
    df2 = df2.fillna(value=0)
    df2 = df2.rename(columns = {'cholesterol':'cholesterol_mg'}, errors='raise')
    for col in [ 'calories', 'total_fat', 'saturated_fat', 'cholesterol_mg', 'carbohydrate', 'fiber', 'sugars']:
        df2[col] = df2[col].apply(lambda s: re.sub("[^0-9\.]", "", str(s)))
        df2[col] = df2[col].apply(lambda s: 0 if len(s)==0 else float(s))
    return df2

symbols = ['circle', 'square', 'diamond', 'cross', 'triangle-up', 'triangle-down', 'triangle-left', 'triangle-right', 
                                  'triangle-ne', 'triangle-nw', 'triangle-sw', 'triangle-se', 'pentagon', 'hexagon', 'hexagon2', 'hexagram', 'star', 'octagon']


st.set_page_config(layout='centered')

with st.expander(label='About', expanded=False):
    st.markdown('''
        TODO 

        If you see issues or have comments, please [contact me](https://mobile.twitter.com/a_ghasemi). 
    ''')


df = load_data()

query = st.text_input(label='What food items are you looking for?')

df = df [ df['name'].str.lower().str.contains(query.lower())]

carb_range = st.slider(label='Specify the desired amount of carbohydrates in 100 grams serving', min_value=0, max_value=100, value=(0,100))
df = df.query(f"carbohydrate>={carb_range[0]} and carbohydrate<={carb_range[1]}")


if len(df)<100:
    for i,row in df.iterrows():
        with st.expander(label=f'{row["name"]}'):
        
            st.markdown(f'_Calories_=__{row["calories"]}__ _Fat_=__{row["total_fat"]}__ _Carbs_=__{row["carbohydrate"]}__')
else:
    st.markdown('Please specify more details')
