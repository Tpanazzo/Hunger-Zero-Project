# --------------------
# Libraries
# --------------------
import pandas as pd
import plotly.express as px
import streamlit as st
import inflection

# -----------------
# Import Dataset
# -----------------
df = pd.read_csv('dataset/zomato.csv')

# --------------
# Funções
# --------------

RAW_DATA_PATH = f"dataset/zomato.csv"

COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zealand",
    162: "Philippines",
    166: "Qatar",
    184: "Singapore",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
}

COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
}

def country_name(country_id):
  return COUNTRIES[country_id]

def color_name(color_code):
  return COLORS[color_code]

def create_price_type(price_range):
  if price_range == 1:
    return "cheap"
  elif price_range == 2:
    return "normal"
  elif price_range == 3:
    return "expensive"
  else:
    return "gourmet"

def adjust_columns_order(dataframe):
    df = dataframe.copy()

    new_cols_order = [
        "restaurant_id",
        "restaurant_name",
        "country",
        "city",
        "address",
        "locality",
        "locality_verbose",
        "longitude",
        "latitude",
        "cuisines",
        "price_type",
        "average_cost_for_two",
        "currency",
        "has_table_booking",
        "has_online_delivery",
        "is_delivering_now",
        "aggregate_rating",
        "rating_color",
        "color_name",
        "rating_text",
        "votes",
    ]

    return df.loc[:, new_cols_order]

def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df

def process_data(file_path):
    df = pd.read_csv(file_path)
    df = df.dropna()
    df = rename_columns(df)
    df["price_type"] = df.loc[:, "price_range"].apply(lambda x: create_price_type(x))
    df["country"] = df.loc[:, "country_code"].apply(lambda x: country_name(x))
    df["color_name"] = df.loc[:, "rating_color"].apply(lambda x: color_name(x))
    df["cuisines"] = df.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])
    df = df.drop_duplicates()
    df = adjust_columns_order(df)
    df.to_csv("dataset/processed.csv", index=False)
    return df

df_raw = pd.read_csv(RAW_DATA_PATH)
df1 = df_raw.copy()
df1 = rename_columns(df1)
df1 = df1.dropna()
df2 = process_data(RAW_DATA_PATH)

st.set_page_config( 
    page_title="Countries", page_icon="🌎", layout="wide"
)

# =================
# Barra Lateral (Sidebar) do Streamlit
# =================

col1, col2 = st.sidebar.columns([1, 4], gap="small")
col2.markdown("# Hunger Zero!")
st.sidebar.markdown('## Filter')
country_options = st.sidebar.multiselect(
    'Choose the countries whose restaurants you want to view',
    df2.loc[:, "country"].unique().tolist(),
        default=["Brazil", "England", "Qatar", "South Africa", "Canada", "Australia"],
    )
st.sidebar.markdown("""---""")

st.sidebar.markdown("### Processed Data")

processed_data = pd.read_csv("dataset/processed.csv")

st.sidebar.download_button(
    label="Download",
    data=processed_data.to_csv(index=False, sep=";"),
    file_name="processed.csv",
    mime="text/csv",
    )

# Filtro de países:
selected_countries = df2['country'].isin(country_options)
df2 = df2.loc[selected_countries, :]

# =================
# Layout da Página Countries do Streamlit 
# =================

st.markdown("# 🌎 Country View")

with st.container():
    cols = ['country', 'restaurant_id']
    df_aux = df2.loc[:, cols].groupby('country').count().sort_values('restaurant_id', ascending=False).reset_index()
    fig = px.bar(
       df_aux, 
       x='country', 
       y='restaurant_id', text="restaurant_id", 
       title='Number of Registered Restaurants per Country',
       labels={
            "country": "Country",
            "restaurant_id": "Restaurants",
        },
       )
    st.plotly_chart(fig, use_container_width=True)
   
with st.container():   
   cols = ['country', 'city']
   df_aux = df2.loc[:, cols].groupby('country').nunique().sort_values('city', ascending=False).reset_index()
   fig = px.bar(
      df_aux,
      x='country',
      y='city', text='city',
      title='Number of Registered Cities per Country',
      labels={
        "country": "Country",
        "city": "City"
          },
        )
   st.plotly_chart(fig, use_container_width=True)
  
with st.container():   
   col1, col2 = st.columns(2)
   with col1:
      
      df_aux = df2.loc[:, ['votes', 'country']].groupby('country').mean().sort_values('votes', ascending=False).reset_index()
      fig = px.bar(
         df_aux,
         x='country',
         y='votes', 
         text='votes',
         text_auto=".2f",
         title='Average Ratings per Country',
         labels={
            "country": "Country",
            "votes": 'Votes'
         }
      )
      st.plotly_chart(fig, use_container_width=True)

   with col2:
      
      df_aux = df2.loc[:, ['average_cost_for_two', 'country']].groupby('country').mean().sort_values('average_cost_for_two', ascending=False).reset_index()
      fig = px.bar(
         df_aux,
         x='country',
         y='average_cost_for_two', text='average_cost_for_two', text_auto='.2f',
         title='Average Price of a Meal for Two People per Country',
         labels={
            "country": 'Country',
            'average_cost_for_two': 'Average Cost'
         }
      )
      st.plotly_chart(fig, use_container_width=True)
