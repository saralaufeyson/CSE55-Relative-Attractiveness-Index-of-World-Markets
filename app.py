import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# Sample data for locations
locations = {
    "Location": ["Location A", "Location B", "Location C", "Location D", "Location E"],
    "GDP ($B)": [2500, 1800, 3000, 1500, 4000],
    "Healthcare Expenditure (%)": [9.5, 7.2, 10.0, 6.8, 12.0],
    "Regulatory Score (1-10)": [8.5, 6.0, 9.0, 5.0, 9.5],
    "Skilled Workforce (1-10)": [9.0, 8.5, 8.5, 7.0, 9.5],
    "Resource Availability (1-10)": [7.5, 8.0, 9.5, 6.5, 8.0],
    "Political Stability (1-10)": [8.0, 7.0, 9.0, 6.5, 9.5],
    "Latitude": [40.7128, 34.0522, 51.5074, 48.8566, 35.6895],
    "Longitude": [-74.0060, -118.2437, -0.1278, 2.3522, 139.6917]
}
df = pd.DataFrame(locations)

# Streamlit page configuration
st.set_page_config(page_title="PharmaScope - Pharmaceutical Location Finder", layout="wide")

background_image_url = "https://i.postimg.cc/brVpRM4J/Whats-App-Image-2024-11-14-at-12-59-36-PM.jpg"

# CSS Styling
st.markdown(f"""
    <style>
    /* Remove Streamlit's default padding */
    .css-1v3fvcr {{
        padding: 0 !important;
        margin: 0 !important;
    }}
    
    /* Background Image */
    .stApp {{
        background-image: url("{background_image_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* Center main content and control width */
    .main-content {{
        padding: 0px; /* Remove padding to avoid box effect */
        margin: 0 auto;  /* Centers the content */
        max-width: 1200px;
        color: #333;
    }}
    
    /* Custom alignment for headers and tables */
    .title {{
        color: #0d6efd;
        font-weight: bold;
        font-size: 2.5em;
    }}
    
    .stDataFrame {{
        padding-left: 20px !important;  /* Consistent alignment for tables */
    }}
    </style>
""", unsafe_allow_html=True)

# Main Content Wrapper
st.markdown("<div class='main-content'>", unsafe_allow_html=True)

# Sidebar and main page sections
st.sidebar.title("Navigation")
pages = ["Home", "RAI Calculation", "Visualizations"]
choice = st.sidebar.radio("Go to", pages)

# Sidebar sliders for factor weights
st.sidebar.subheader("Adjust Factor Weights")
gdp_weight = st.sidebar.slider("Weight for GDP ($B)", 0, 100, 20)
healthcare_weight = st.sidebar.slider("Weight for Healthcare Expenditure (%)", 0, 100, 20)
regulatory_weight = st.sidebar.slider("Weight for Regulatory Score", 0, 100, 20)
workforce_weight = st.sidebar.slider("Weight for Skilled Workforce", 0, 100, 20)
resource_weight = st.sidebar.slider("Weight for Resource Availability", 0, 100, 20)
political_weight = st.sidebar.slider("Weight for Political Stability", 0, 100, 20)

# Normalize weights and calculate RAI
total_weight = sum([gdp_weight, healthcare_weight, regulatory_weight, workforce_weight, resource_weight, political_weight])
normalized_weights = [
    gdp_weight / total_weight,
    healthcare_weight / total_weight,
    regulatory_weight / total_weight,
    workforce_weight / total_weight,
    resource_weight / total_weight,
    political_weight / total_weight
]

df["RAI"] = (
    normalized_weights[0] * df["GDP ($B)"] +
    normalized_weights[1] * df["Healthcare Expenditure (%)"] +
    normalized_weights[2] * df["Regulatory Score (1-10)"] +
    normalized_weights[3] * df["Skilled Workforce (1-10)"] +
    normalized_weights[4] * df["Resource Availability (1-10)"] +
    normalized_weights[5] * df["Political Stability (1-10)"]
)

# Page sections
if choice == "Home":
    st.markdown("<h1 class='title'>PharmaScope</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='subtitle'>Pharmaceutical Location Finder</h2>", unsafe_allow_html=True)
    st.markdown("""<p>Welcome to PharmaScope, your tool for identifying optimal locations for establishing or expanding pharmaceutical operations.</p>""", unsafe_allow_html=True)

elif choice == "RAI Calculation":
    st.markdown("<h1 class='title'>Calculate RAI for Locations</h1>", unsafe_allow_html=True)
    st.markdown("<p><strong>Updated RAI Scores:</strong></p>", unsafe_allow_html=True)
    st.dataframe(df.sort_values("RAI", ascending=False))

elif choice == "Visualizations":
    st.markdown("<h1 class='title'>Visualize Locations</h1>", unsafe_allow_html=True)

    # Bar chart of RAI scores
    fig = px.bar(df.sort_values("RAI", ascending=False), x="Location", y="RAI", text="RAI", color="RAI", title="RAI Scores")
    st.plotly_chart(fig, use_container_width=True)

    # Map visualization with markers
    map_center = [df["Latitude"].mean(), df["Longitude"].mean()]
    m = folium.Map(location=map_center, zoom_start=2)
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df.iterrows():
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=f"{row['Location']}: RAI Score = {row['RAI']:.2f}",
            tooltip=row["Location"]
        ).add_to(marker_cluster)

    st_folium(m, width=800, height=400)

# Close main content div
st.markdown("</div>", unsafe_allow_html=True)
