import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import plotly.express as px
import json
import ast
import pickle
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Plotting Demo")

st.title("Analytics")

new_df = pd.read_csv('datasets/data_viz1.csv')
feature_text = pickle.load(open('datasets/feature_text.pkl', 'rb'))

group_df = (
    new_df
    .groupby('sector')[['price', 'price_per_sqft', 'built_up_area', 'south_lat', 'north_lat', 'west_lon', 'east_lon']]
    .mean()
    .reset_index()
)

# If you want to keep geojson (e.g., first occurrence per sector)
geojson_df = new_df.groupby('sector')['geojson'].first().reset_index()
group_df = group_df.merge(geojson_df, on='sector', how='left')


def safe_json_parser(val):
    if isinstance(val, dict):
        return val
    try:
        return json.loads(val)
    except:
        return ast.literal_eval(val)

group_df['geojson'] = group_df['geojson'].apply(safe_json_parser)

# --- Merge all geojsons into one FeatureCollection ---
feature_collection = {
    "type": "FeatureCollection",
    "features": []
}
for _, row in group_df.iterrows():
    gj = row['geojson']

    # If it's not already a Feature, wrap it
    if gj.get("type") != "Feature":
        gj = {
            "type": "Feature",
            "geometry": gj,
            "properties": {"sector": row['sector']}
        }
    else:
        # Ensure sector property exists
        gj["properties"]["sector"] = row['sector']

    feature_collection["features"].append(gj)

# --- Normalize sector values in BOTH places ---
group_df['sector'] = group_df['sector'].astype(str).str.strip().str.lower()
for f in feature_collection['features']:
    f['properties']['sector'] = str(f['properties']['sector']).strip().lower()

# --- Debug: Show unmatched sectors (if any) ---
df_sectors = set(group_df['sector'])
geojson_sectors = {f['properties']['sector'] for f in feature_collection['features']}
# --- Choropleth ---
fig = px.choropleth_mapbox(
    group_df,
    geojson=feature_collection,
    locations='sector',
    color='price_per_sqft',  # Change to 'price' or 'built_up_area' as needed
    featureidkey="properties.sector",
    mapbox_style="carto-positron",
    center={"lat": 28.45, "lon": 77.03},
    zoom=10,
    color_continuous_scale="Viridis",
    opacity=0.6,
    title="Average Price per Sqft by Sector",
    height = 700,
    width = 1200,
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<h4 style='text-align: left;'>Features WordCloud</h4>", unsafe_allow_html=True)
wordcloud = WordCloud(
    width=800, height=800,
    background_color='white',
    stopwords=set(['s']),
    min_font_size=10
).generate(feature_text)

# Create a figure and axis
fig, ax = plt.subplots(figsize=(8, 8))
ax.imshow(wordcloud, interpolation='bilinear')
ax.axis('off')
plt.tight_layout(pad=0)

# Pass the figure to Streamlit
st.pyplot(fig)

st.markdown("<h4 style='text-align: left;'>Area vs Price</h4>", unsafe_allow_html=True)
property_type = st.selectbox("Select Property Type", ['flat', 'house'])
if(property_type == 'house'):
    fig1 = px.scatter(new_df[new_df['property_type']=='house'], x = 'built_up_area', y = 'price', color = 'bedRoom')
    st.plotly_chart(fig1, use_container_width=True)
else:
    fig1 = px.scatter(new_df[new_df['property_type']=='flat'], x = 'built_up_area', y = 'price', color = 'bedRoom')
    st.plotly_chart(fig1, use_container_width=True)

st.markdown("<h4 style='text-align: left;'>Bhk Pie Chart</h4>", unsafe_allow_html=True)
sector_options = new_df['sector'].unique().tolist()
sector_options.insert(0, 'All Sectors')
selected_sector = st.selectbox("Select Sector", sector_options)
if selected_sector == 'All Sectors':
    fig2 = px.pie(new_df, names = 'bedRoom')
    st.plotly_chart(fig2, use_container_width=True)
else:
    fig2 = px.pie(new_df[new_df['sector'] == selected_sector], names = 'bedRoom')
    st.plotly_chart(fig2, use_container_width=True)
    
st.markdown("<h4 style='text-align: left;'>Side by Side Bhk Price Comparison</h4>", unsafe_allow_html=True)
temp_df = new_df[new_df['bedRoom'] <= 4]
fig3 = px.box(temp_df, x = 'bedRoom', y = 'price', title = 'Bhk Price Range')
st.plotly_chart(fig3, use_container_width=True)
    
st.markdown("<h4 style='text-align: left;'>Side by Side Distplot for Property Type</h4>", unsafe_allow_html=True)    
fig4, ax = plt.subplots()
sns.histplot(
    data=new_df,
    x="price",
    kde=True,
    hue="property_type",
    element="step",  # Outlines instead of filled bars
    common_norm=False,  # Prevents normalizing across categories
    ax=ax
)

st.pyplot(fig4, use_container_width=True)