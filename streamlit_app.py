import pandas as pd
import numpy as np
import duckdb, re, math, requests, pathlib

import streamlit as st

import plotly.express as px


@st.cache()
def load_data(country):
    df2 = pd.read_pickle(f"facts.{country}.pkl")  # .dropna(subset=["keywords"])
    # df2["keywords"] = df2["keywords"].str.split("|")

    kw = pathlib.Path(f"keywords.{country}").read_text().split("\n")
    return df2, kw


CALORIES_COLUMN_NAME = "energy"
FAT_COLUMN_NAME = "fat"
CARBS_COLUMN_NAME = "carbs"

SATURATED_FAT_COLUMN_NAME = "saturated_fat"
SUGARS_COLUMN_NAME = "sugars"
FIBRE_COLUMN_NAME = "fiber"

NAME_COLUMN_NAME = "name"
URL_COLUMN_NAME = "url"
IMAGE_COLUMN_NAME = "image"

stores = {"coop": "Coop (CH)"}

st.set_page_config(
    layout="centered",
    page_title="NutriSearch: Search for Common Grocery Items by Their Nutritional Value",
)


with st.sidebar:
    with st.expander(label="About", expanded=False):
        st.markdown(
            """
             

            If you see issues or have comments, please [contact me](https://mobile.twitter.com/a_ghasemi). 
        """
        )
    country = st.selectbox(
        "Grocery store",
        options=list(stores.keys()),
        format_func=lambda x: stores[x],
        index=0,
    ).lower()
    show_carbs = st.checkbox("Show selector for Carbs", value=True)
    show_fats = st.checkbox("Show selector for Fat", value=False)
    show_calories = st.checkbox("Show selector for Calories", value=False)

data, keywords = load_data(country)

df = data.copy()

query = st.multiselect(
    label="What are you looking for?", options=keywords, default=None
)

df = df[
    df["keywords"].apply(lambda ks: len(query) == 0 or any([k in ks for k in query]))
]

if show_carbs:
    carb_range = st.slider(
        label="Carbohydrates in 100 grams",
        min_value=0,
        max_value=100,
        value=(0, 100),
    )
    df = df.query(
        f"{CARBS_COLUMN_NAME}>={carb_range[0]} and {CARBS_COLUMN_NAME}<={carb_range[1]}"
    )

if show_fats:
    fat_range = st.slider(
        label="Total fat in 100 grams",
        min_value=0,
        max_value=100,
        value=(0, 100),
    )
    df = df.query(
        f"{FAT_COLUMN_NAME}>={fat_range[0]} and {FAT_COLUMN_NAME}<={fat_range[1]}"
    )

if show_calories:
    calories_range = st.slider(
        label="Calories in 100 grams",
        min_value=0,
        max_value=1000,
        value=(0, 1000),
    )
    df = df.query(
        f"`{CALORIES_COLUMN_NAME}`>={calories_range[0]} and `{CALORIES_COLUMN_NAME}`<={calories_range[1]}"
    )


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
        index=1,
    )
    df = df.sort_values(by=sort_column)
    st.markdown(f"### {len(df)} item(s) found")

    for i, row in df.iterrows():
        with st.expander(
            label=f"{row[NAME_COLUMN_NAME]} (⚡={row[CALORIES_COLUMN_NAME]:.0f}, 🍬={row[CARBS_COLUMN_NAME]:.0f}, 🧈={row[FAT_COLUMN_NAME]:.0f})"
        ):
            im_url = row[IMAGE_COLUMN_NAME]
            # im_nutr_url = row['image_nutrition_small_url']
            # im_ingr_url = row['image_ingredients_small_url']

            sat_fat = (
                row[SATURATED_FAT_COLUMN_NAME]
                if not np.isnan(row[SATURATED_FAT_COLUMN_NAME])
                else "?"
            )
            sugar = (
                row[SUGARS_COLUMN_NAME]
                if not np.isnan(row[SUGARS_COLUMN_NAME])
                else "?"
            )
            fiber = (
                row[FIBRE_COLUMN_NAME] if not np.isnan(row[FIBRE_COLUMN_NAME]) else "?"
            )

            st.markdown(
                f"_Calories_=__{row[CALORIES_COLUMN_NAME]}__ _Fat_=__{row[FAT_COLUMN_NAME]}__ _Carbs_=__{row[CARBS_COLUMN_NAME]}__\n\n"
                + f"_Saturated Fat_=__{sat_fat}__ _Sugar_=__{sugar}__ Fiber=__{fiber}__\n\n"
            )
            if im_url is not None:
                st.markdown(
                    f'<p align="center"> <img src="{im_url}"  width="60%" /> </p>',
                    unsafe_allow_html=True,
                )

            st.markdown(f"__[Visit in the store website]({row[URL_COLUMN_NAME]})__")


else:
    st.markdown(f"### Too many ({len(df)}) items found. Please specify more details")
