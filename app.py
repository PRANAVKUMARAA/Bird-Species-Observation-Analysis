import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    forest_data = pd.read_excel('Bird_Monitoring_Data_FOREST.xlsx')
    grassland_data = pd.read_excel('Bird_Monitoring_Data_GRASSLAND.xlsx')
    return forest_data, grassland_data

forest_data, grassland_data = load_data()

forest_data["Location_Type"] = "Forest"
grassland_data["Location_Type"] = "Grassland"
merged_data = pd.concat([forest_data, grassland_data], ignore_index=True)

st.sidebar.title("Filters")
location_type = st.sidebar.selectbox("Select Habitat Type", ["Both", "Forest", "Grassland"])
years = merged_data["Year"].unique()

years.sort()

min_year, max_year = min(years), max(years)

if min_year == max_year:
    st.sidebar.write(f"Year Range: {min_year} (Only one year available)")
    year_range = (min_year, max_year)
else:
    year_range = st.sidebar.slider(
        "Select Year Range",
        min_value=int(min_year),
        max_value=int(max_year),
        value=(int(min_year), int(max_year))
    )


filtered_data = merged_data[
    (merged_data["Year"] >= year_range[0]) &
    (merged_data["Year"] <= year_range[1])
]

if location_type != "Both":
    filtered_data = filtered_data[filtered_data["Location_Type"] == location_type]


st.title("Bird Species Observation Dashboard")

st.subheader("Dataset Overview")
st.dataframe(filtered_data)

st.subheader("Species Observation Count")
species_counts = (
    filtered_data.groupby("Common_Name")
    .size()
    .reset_index(name="Count")
    .sort_values(by="Count", ascending=False)
    .head(10)
)

species_fig = px.bar(
    species_counts,
    x="Common_Name",
    y="Count",
    title="Top 10 Observed Bird Species",
    labels={"Common_Name": "Bird Species", "Count": "Observation Count"}
)
st.plotly_chart(species_fig)

st.subheader("Environmental Factors Analysis")

if "Temperature" in filtered_data.columns and "Humidity" in filtered_data.columns:

    filtered_data["Initial_Three_Min_Cnt"] = filtered_data["Initial_Three_Min_Cnt"].astype(int)

    env_fig = px.scatter(
        filtered_data,
        x="Temperature",
        y="Humidity",
        color="Location_Type",
        size="Initial_Three_Min_Cnt",
        hover_name="Common_Name",
        title="Temperature vs Humidity and Bird Count",
        labels={
            "Temperature": "Temperature (°C)",
            "Humidity": "Humidity (%)",
            "Initial_Three_Min_Cnt": "Bird Count"
        },
    )
    st.plotly_chart(env_fig)


st.subheader("Observation Trend Over Time")
time_series = (
    filtered_data.groupby(["Year", "Location_Type"])
    .size()
    .reset_index(name="Count")
)

time_series_fig = px.line(
    time_series,
    x="Year",
    y="Count",
    color="Location_Type",
    title="Bird Observations Over Time",
    labels={"Year": "Year", "Count": "Observation Count"}
)
st.plotly_chart(time_series_fig)
