import pandas as pd
import duckdb, re, math, requests

import streamlit as st

import plotly.express as px


@st.cache()
def load_data():
    df2 = pd.read_csv("generic.csv")

    df2["keywords"] = df2["name"].apply(
        lambda x: [w.title() for w in str(x).split(", ") if len(w) > 0]
    )

    kw = set([l[0] for l in df2["keywords"]])

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


st.set_page_config(layout="wide")

st.title("NutriSearch: Search for Common Grocery Items by Their Nutritional Value")

with st.sidebar:
    with st.expander(label="About", expanded=False):
        st.markdown(
            """
            TODO 

            If you see issues or have comments, please [contact me](https://mobile.twitter.com/a_ghasemi). 
        """
        )
    show_carbs = st.checkbox('Show selector for Carbs', value=True)
    show_fats = st.checkbox('Show selector for Fat', value=False)
    show_calories = st.checkbox('Show selector for Calories', value=False)

data, keywords = load_data()

df = data.copy()

query = st.multiselect( 
    label="What food item(s) are you looking for?", options=keywords, default=None
)

df = df[df["keywords"].apply(lambda ks: len(query)==0 or any([k in ks for k in query]))]

if show_carbs:
    carb_range = st.slider(
        label="Carbohydrates in 100 grams",
        min_value=0,
        max_value=100,
        value=(0, 100),
    )
    df = df.query(f"carbohydrate>={carb_range[0]} and carbohydrate<={carb_range[1]}")

if show_fats:
    fat_range = st.slider(
        label="Total fat in 100 grams",
        min_value=0,
        max_value=100,
        value=(0, 100),
    )
    df = df.query(f"total_fat>={fat_range[0]} and total_fat<={fat_range[1]}")

if show_calories:
    calories_range = st.slider(
        label="Calories in 100 grams",
        min_value=0,
        max_value=100,
        value=(0, 100),
    )
    df = df.query(f"calories>={calories_range[0]} and calories<={calories_range[1]}")


if len(df) < 100:
    sort_column = st.selectbox(
        "Sort by ",
        options=["calories", "carbohydrate", "total_fat"],
        format_func=lambda x: dict(
            {
                "calories": "Calories",
                "carbohydrate": "Carbohydrate",
                "total_fat": "Total Fat",
            }
        )[x],
    )
    df = df.sort_values(by=sort_column)
    for i, row in df.iterrows():
        with st.expander(label=f'{row["name"]} (E={row["calories"]:.0f}, C={row["carbohydrate"]:.0f}, F={row["total_fat"]:.0f})'):

            st.markdown(
                f'_Calories_=__{row["calories"]}__ _Fat_=__{row["total_fat"]}__ _Carbs_=__{row["carbohydrate"]}__\n\n' 
                + f'_Saturated Fat_=__{row["saturated_fat"]}__ _Cholesterol_=__{row["cholesterol_mg"]}__ _Sugar_=__{row["sugars"]}__ Fiber=__{row["fiber"]}__\n\n'

            )
else:
    st.markdown("## Please specify more details")
