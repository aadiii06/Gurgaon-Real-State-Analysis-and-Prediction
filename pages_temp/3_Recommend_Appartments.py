import streamlit as st
import pickle
import pandas as pd
import numpy as np

st.set_page_config(page_title="Recommend Apartments")

location_df = pickle.load(open('datasets/location_distance.pkl', 'rb'))
cosine_sim1 = pickle.load(open('datasets/cosine_sim1.pkl', 'rb'))
cosine_sim2 = pickle.load(open('datasets/cosine_sim2.pkl', 'rb'))
cosine_sim3 = pickle.load(open('datasets/cosine_sim3.pkl', 'rb'))

def recommend_properties_with_scores(property_name, top_n=5):
    # Weighted combination (now it won't be overwritten)
    cosine_sim_matrix = 1*cosine_sim3 + 0.8*cosine_sim2 + 0.5*cosine_sim1
    #cosine_sim_matrix = cosine_sim3
    
    sim_scores = list(enumerate(cosine_sim_matrix[location_df.index.get_loc(property_name)]))
    
    # Sort properties by similarity
    sorted_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Select top_n most similar (excluding itself)
    top_indices = [i[0] for i in sorted_scores[1:top_n+1]]
    top_scores = [i[1] for i in sorted_scores[1:top_n+1]]
    
    # Get property names
    top_properties = location_df.index[top_indices].tolist()
    
    # Build DataFrame
    recommendations_df = pd.DataFrame({
        'PropertyName': top_properties,
        'SimilarityScore': top_scores
    })
    
    return recommendations_df

st.title("Select Location and Radius")

selected_location = st.selectbox('Location', sorted(location_df.columns.to_list()))

radius = st.number_input("Radius in KMs")

if st.button('Search'):
    result_ser = location_df[location_df[selected_location] < radius*1000][selected_location].sort_values().to_dict()
    counter = 0
    appartment = []
    distance = []
    for key, value in result_ser.items():
        if value is not None:   # make sure value exists
            counter += 1
            appartment.append(key)
            distance.append(value)
            st.text(str(counter) + ". " + str(key) + ": --> " + str(round(value/1000)) + " KMs")

    if counter == 0:
        st.text("No property in nearby location and radius")
        
st.title("Recommended Apartments")
selected_appartment = st.selectbox('Select an Apartment', sorted(location_df.index.to_list()))

if st.button('Recommend'):
    recommendation_df = recommend_properties_with_scores(selected_appartment, top_n=5)
    
    st.dataframe(recommendation_df)