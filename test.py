import wbdata
import pandas as pd
import streamlit as st
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler

# Streamlit page configuration
st.set_page_config(page_title="Pharma RAI Calculator", layout="wide")

# 1. Data Collection from World Bank using wbdata
st.sidebar.title("Data Collection and RAI Calculation")

# Define the countries (example: India, USA, China)
countries = ['IN', 'US', 'CN']

# Define the indicators (GDP, Healthcare Expenditure, Labor Force)
indicators = {
    'NY.GDP.MKTP.CD': 'GDP',  # GDP (current US$)
    'SH.XPD.CHEX.PC.CD': 'Healthcare Expenditure',  # Per capita healthcare expenditure
    'SL.TLF.TOTL.IN': 'Labor Force'  # Total labor force
}

# Define the date range for data collection
start_date = datetime(2015, 1, 1)
end_date = datetime(2023, 1, 1)

# Fetch the data from World Bank API
st.write("Fetching data from World Bank...")
data = wbdata.get_dataframe(indicators, country=countries)
#data = wbdata.get_dataframe(indicators, country=['IN', 'US', 'CN'])
# Reset index and format the data
data = data.reset_index()
data.columns = ['Year', 'Country', 'GDP', 'Healthcare Expenditure', 'Labor Force']
st.write("Data collection complete")
st.write(data.head())

# 2. User Input for Weights to Calculate RAI
st.sidebar.header("Adjust Weights for RAI Calculation")

# User can adjust the weights for the factors
gdp_weight = st.sidebar.slider("Weight for GDP", 0, 100, 40)
healthcare_weight = st.sidebar.slider("Weight for Healthcare Expenditure", 0, 100, 30)
labor_weight = st.sidebar.slider("Weight for Labor Force", 0, 100, 30)

# Normalize the weights so they sum to 100
weights = [gdp_weight, healthcare_weight, labor_weight]
total_weight = sum(weights)
normalized_weights = [w / total_weight for w in weights]

st.sidebar.write(f"Normalized Weights: GDP: {normalized_weights[0]}, Healthcare: {normalized_weights[1]}, Labor: {normalized_weights[2]}")

# 3. Data Normalization (Min-Max Scaling) for RAI Calculation
scaler = MinMaxScaler()
normalized_data = pd.DataFrame(scaler.fit_transform(data[['GDP', 'Healthcare Expenditure', 'Labor Force']]), 
                               columns=['GDP', 'Healthcare Expenditure', 'Labor Force'], 
                               index=data.index)

# 4. RAI Calculation (Weighted Sum of Normalized Data)
normalized_data['RAI'] = (normalized_data['GDP'] * normalized_weights[0] +
                          normalized_data['Healthcare Expenditure'] * normalized_weights[1] +
                          normalized_data['Labor Force'] * normalized_weights[2])

# Merge the RAI with the original data
data['RAI'] = normalized_data['RAI']

# Display the RAI Data
st.write("Calculated RAI for each country and year:")
st.dataframe(data[['Year', 'Country', 'GDP', 'Healthcare Expenditure', 'Labor Force', 'RAI']])

# 5. Visualize Results with Streamlit

# Bar Chart of RAI Scores
st.subheader("RAI Scores by Country and Year")
fig = px.bar(data, x='Country', y='RAI', color='Year', title="RAI Scores by Country")
st.plotly_chart(fig, use_container_width=True)

# 6. Map Visualization with Folium
st.subheader("Geospatial Visualization of RAI Scores")
m = folium.Map(location=[20, 80], zoom_start=2)
marker_cluster = MarkerCluster().add_to(m)

# Define the locations of the countries and RAI scores
locations = {'India': [20.5937, 78.9629], 'USA': [37.0902, -95.7129], 'China': [35.8617, 104.1954]}
for country, coords in locations.items():
    country_data = data[data['Country'] == country]
    rai_score = country_data['RAI'].values[0]
    folium.Marker(
        location=coords,
        popup=f"{country}: RAI {rai_score:.2f}",
        tooltip=f"{country} - RAI"
    ).add_to(marker_cluster)

st_folium(m, width=800, height=500)

# 7. Conclusion
st.write("""
### Conclusion:
This tool provides a data-driven approach for pharmaceutical companies to evaluate optimal locations based on key economic factors such as GDP, healthcare expenditure, and labor force. By adjusting the weights for these factors, users can dynamically compute the **Relative Attractiveness Index (RAI)** and make informed decisions about market expansion.
""")
