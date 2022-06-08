import pandas as pd
import duckdb, re, math, requests, pathlib

import streamlit as st

import plotly.express as px


@st.cache()
def load_data(country):
    df2 = pd.read_csv(f"{country}.csv")

    
    kw = pathlib.Path(f"keywords.{country}").read_text().split('\n')
    return df2, kw


symbols = [
    "circle",
    "square",
    "diamond",
    "cross",
    "triangle-up",
    "triangle-down",
    "triangle-left",
    "triangle-right",
    "triangle-ne",
    "triangle-nw",
    "triangle-sw",
    "triangle-se",
    "pentagon",
    "hexagon",
    "hexagon2",
    "hexagram",
    "star",
    "octagon",
]

CALORIES_COLUMN_NAME = 'energy-kcal_100g'
FAT_COLUMN_NAME = 'fat_100g'
CARBS_COLUMN_NAME = 'carbohydrates_100g'

SATURATED_FAT_COLUMN_NAME = 'saturated-fat_100g'
CHOLESTEROL_COLUMN_NAME = 'cholesterol_100g'
SUGARS_COLUMN_NAME = 'sugars_100g'
FIBRE_COLUMN_NAME = 'fiber_100g'

NAME_COLUMN_NAME = 'product_name'

st.set_page_config(layout="wide", page_title="NutriSearch: Search for Common Grocery Items by Their Nutritional Value")


with st.sidebar:
    with st.expander(label="About", expanded=False):
        st.markdown(
            """
             

            If you see issues or have comments, please [contact me](https://mobile.twitter.com/a_ghasemi). 
        """
        )
    country = st.selectbox('Target country', options=['UK', 'CH'], index = 1).lower()
    show_carbs = st.checkbox('Show selector for Carbs', value=True)
    show_fats = st.checkbox('Show selector for Fat', value=False)
    show_calories = st.checkbox('Show selector for Calories', value=False)

data, keywords = load_data(country)

df = data.copy()

query = st.multiselect( 
    label="What are you looking for?", options=keywords, default=None
)

df = df[df["keywords"].apply(lambda ks: len(query)==0 or any([k in str(ks) for k in query]))]

if show_carbs:
    carb_range = st.slider(
        label="Carbohydrates in 100 grams",
        min_value=0,
        max_value=100,
        value=(0, 100),
    )
    df = df.query(f"{CARBS_COLUMN_NAME}>={carb_range[0]} and {CARBS_COLUMN_NAME}<={carb_range[1]}")

if show_fats:
    fat_range = st.slider(
        label="Total fat in 100 grams",
        min_value=0,
        max_value=100,
        value=(0, 100),
    )
    df = df.query(f"{FAT_COLUMN_NAME}>={fat_range[0]} and {FAT_COLUMN_NAME}<={fat_range[1]}")

if show_calories:
    calories_range = st.slider(
        label="Calories in 100 grams",
        min_value=0,
        max_value=100,
        value=(0, 100),
    )
    df = df.query(f"{CALORIES_COLUMN_NAME}>={calories_range[0]} and {CALORIES_COLUMN_NAME}<={calories_range[1]}")


if len(df) < 100:
    sort_column = st.selectbox(
        "Sort by ",
        options=[CALORIES_COLUMN_NAME, CARBS_COLUMN_NAME, FAT_COLUMN_NAME],
        format_func=lambda x: dict(
            {
                CALORIES_COLUMN_NAME: "Calories",
                CARBS_COLUMN_NAME: "Carbohydrate",
                FAT_COLUMN_NAME: "Total Fat",
            }
        )[x],
    )
    df = df.sort_values(by=sort_column)
    for i, row in df.iterrows():
        with st.expander(label=f'{row[NAME_COLUMN_NAME]} (⚡={row[CALORIES_COLUMN_NAME]:.0f}, 🍬={row[CARBS_COLUMN_NAME]:.0f}, 🧈={row[FAT_COLUMN_NAME]:.0f})'):

            st.markdown(
                f'_Calories_=__{row[CALORIES_COLUMN_NAME]}__ _Fat_=__{row[FAT_COLUMN_NAME]}__ _Carbs_=__{row[CARBS_COLUMN_NAME]}__\n\n' 
                + f'_Saturated Fat_=__{row[SATURATED_FAT_COLUMN_NAME]}__ _Cholesterol_=__{row[CHOLESTEROL_COLUMN_NAME]}__ _Sugar_=__{row[SUGARS_COLUMN_NAME]}__ Fiber=__{row[FIBRE_COLUMN_NAME]}__\n\n'

            )
else:
    st.markdown("## Please specify more details")
