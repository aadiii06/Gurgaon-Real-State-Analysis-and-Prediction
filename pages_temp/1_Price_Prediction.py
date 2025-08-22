import streamlit as st
import pickle
import pandas as pd
import numpy as np

st.set_page_config()

with open('df.pkl', 'rb') as file:
    df = pickle.load(file)
    
with open('pipeline.pkl', 'rb') as file:
    pipeline = pickle.load(file)

st.header("Enter your inputs: ")

#property type
property_type = st.selectbox("Property Type", ['flat', 'house'])

#sector
sector = st.selectbox('Sector', sorted(df['sector'].unique().tolist()))

#bedrooms
bedRooom = float(st.selectbox('Number of BedRoom', sorted(df['bedRoom'].unique().tolist())))

#bedrooms
bathRooom = float(st.selectbox('Number of BathRoom', sorted(df['bathroom'].unique().tolist())))

#balcony
balcony = st.selectbox('Number of Balcony', sorted(df['balcony'].unique().tolist()))

#property age
property_age = st.selectbox('Property Age', sorted(df['agePossession'].unique().tolist()))

#built up area
bulit_up_area = st.number_input("Built-up Area", min_value=0.0)

#servant room
servant_room = float(st.selectbox("Servant Room",[0.0, 1.0]))

#store room
store_room = float(st.selectbox("Store Room",[0.0, 1.0]))

#furnishing type
furnishing_type = st.selectbox('Furnishing Type', sorted(df['furnishing_type'].unique().tolist()))

#luxury category
luxury_category = st.selectbox('Luxury Category', sorted(df['luxury_category'].unique().tolist()))

#floor category
floor_category = st.selectbox('Floor Category', sorted(df['floor_category'].unique().tolist()))

if st.button('Predict'):
    
    # form a dataFrame
    data = [[property_type, sector, bedRooom, bathRooom, balcony, property_age, bulit_up_area, servant_room, 
             store_room, furnishing_type, luxury_category, floor_category]]
    columns = ['property_type', 'sector', 'bedRoom', 'bathroom', 'balcony',
               'agePossession', 'built_up_area', 'servant room', 'store room',
               'furnishing_type', 'luxury_category', 'floor_category']
    
    # Convert to DataFrame
    one_df = pd.DataFrame(data, columns=columns)

    #predict
    base_price = np.expm1(pipeline.predict(one_df)[0])
    low = base_price - 0.22
    high = base_price + 0.22
    
    #display
    st.text("The Price of the flat is between {} Cr and {} Cr".format(round(low, 2), round(high, 2)))