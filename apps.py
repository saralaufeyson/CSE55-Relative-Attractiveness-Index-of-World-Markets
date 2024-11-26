import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import logging
from datetime import datetime
import io
import hashlib
from typing import Optional, Tuple, Dict
import time
#2nd version
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure page settings
st.set_page_config(
    page_title="PharmaScope - Pharmaceutical Location Finder",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization
if 'data' not in st.session_state:
    st.session_state.data = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

class DataValidator:
    """Data validation class for CSV files"""
    REQUIRED_COLUMNS = {
        "Location": str,
        "GDP ($B)": float,
        "Healthcare Expenditure (%)": float,
        "Regulatory Score (1-10)": float,
        "Skilled Workforce (1-10)": float,
        "Resource Availability (1-10)": float,
        "Political Stability (1-10)": float,
        "Latitude": float,
        "Longitude": float
    }

    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, str]:
        """Validate the dataframe structure and content"""
        try:
            # Check for required columns
            missing_cols = set(DataValidator.REQUIRED_COLUMNS.keys()) - set(df.columns)
            if missing_cols:
                return False, f"Missing required columns: {missing_cols}"

            # Validate data types and ranges
            for col, dtype in DataValidator.REQUIRED_COLUMNS.items():
                if not pd.api.types.is_dtype_equal(df[col].dtype, dtype):
                    try:
                        df[col] = df[col].astype(dtype)
                    except:
                        return False, f"Column {col} contains invalid {dtype.__name__} values"

            # Validate specific ranges
            score_columns = [col for col in df.columns if "Score" in col or "Workforce" in col or "Stability" in col]
            for col in score_columns:
                if df[col].min() < 0 or df[col].max() > 10:
                    return False, f"{col} contains values outside range 0-10"

            # Validate coordinates
            if df['Latitude'].min() < -90 or df['Latitude'].max() > 90:
                return False, "Invalid latitude values"
            if df['Longitude'].min() < -180 or df['Longitude'].max() > 180:
                return False, "Invalid longitude values"

            return True, "Validation successful"
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return False, f"Validation error: {str(e)}"

class DataProcessor:
    """Data processing and RAI calculation class"""
    
    @staticmethod
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def load_and_process_csv(uploaded_file) -> Optional[pd.DataFrame]:
        """Load and process CSV file with caching"""
        try:
            df = pd.read_csv(uploaded_file)
            is_valid, message = DataValidator.validate_dataframe(df)
            
            if not is_valid:
                st.error(message)
                return None
                
            return df
        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            st.error(f"Error loading CSV file: {str(e)}")
            return None

    @staticmethod
    def calculate_rai(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
        """Calculate RAI with normalized values"""
        try:
            df_normalized = df.copy()
            
            # Normalize numeric columns
            numeric_columns = [
                "GDP ($B)",
                "Healthcare Expenditure (%)",
                "Regulatory Score (1-10)",
                "Skilled Workforce (1-10)",
                "Resource Availability (1-10)",
                "Political Stability (1-10)"
            ]
            
            for col in numeric_columns:
                min_val = df[col].min()
                max_val = df[col].max()
                df_normalized[f'Normalized_{col}'] = (df[col] - min_val) / (max_val - min_val)
            
            # Calculate weighted RAI
            normalized_cols = [f'Normalized_{col}' for col in numeric_columns]
            weight_values = [weights[col] for col in numeric_columns]
            
            df_normalized['RAI'] = sum(
                df_normalized[col] * weight 
                for col, weight in zip(normalized_cols, weight_values)
            )
            
            return df_normalized
        except Exception as e:
            logger.error(f"Error calculating RAI: {str(e)}")
            st.error(f"Error calculating RAI: {str(e)}")
            return df

class Visualizer:
    """Visualization class for creating maps and charts"""
    
    @staticmethod
    def create_map(df: pd.DataFrame) -> folium.Map:
        """Create an interactive folium map"""
        try:
            map_center = [df["Latitude"].mean(), df["Longitude"].mean()]
            m = folium.Map(location=map_center, zoom_start=2, tiles='CartoDB positron')
            marker_cluster = MarkerCluster().add_to(m)
            
            for _, row in df.iterrows():
                # Create detailed HTML popup
                popup_html = f"""
                <div style='width: 200px'>
                    <h4>{row['Location']}</h4>
                    <b>RAI Score:</b> {row['RAI']:.2f}<br>
                    <b>GDP:</b> ${row['GDP ($B)']}B<br>
                    <b>Healthcare:</b> {row['Healthcare Expenditure (%)']}%<br>
                    <b>Regulatory Score:</b> {row['Regulatory Score (1-10)']}/10<br>
                    <b>Workforce Score:</b> {row['Skilled Workforce (1-10)']}/10<br>
                    <b>Resource Score:</b> {row['Resource Availability (1-10)']}/10<br>
                    <b>Political Stability:</b> {row['Political Stability (1-10)']}/10
                </div>
                """
                
                folium.CircleMarker(
                    location=[row["Latitude"], row["Longitude"]],
                    radius=row['RAI'] * 5,
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=row["Location"],
                    color='blue',
                    fill=True,
                    fill_opacity=0.7
                ).add_to(marker_cluster)
            
            return m
        except Exception as e:
            logger.error(f"Error creating map: {str(e)}")
            st.error(f"Error creating map visualization: {str(e)}")
            return None

    @staticmethod
    def create_charts(df: pd.DataFrame):
        """Create interactive plotly charts"""
        try:
            # RAI Score Bar Chart
            fig_rai = px.bar(
                df.sort_values("RAI", ascending=False),
                x="Location",
                y="RAI",
                title="RAI Scores by Location",
                color="RAI",
                text="RAI"
            )
            fig_rai.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            
            # Radar Chart for top location
            top_location = df.loc[df['RAI'].idxmax()]
            categories = [
                'GDP ($B)', 'Healthcare Expenditure (%)', 'Regulatory Score (1-10)',
                'Skilled Workforce (1-10)', 'Resource Availability (1-10)', 
                'Political Stability (1-10)'
            ]
            
            fig_radar = px.line_polar(
                r=[top_location[cat] for cat in categories],
                theta=categories,
                title=f"Metrics for Top Location: {top_location['Location']}"
            )
            
            return fig_rai, fig_radar
        except Exception as e:
            logger.error(f"Error creating charts: {str(e)}")
            st.error(f"Error creating chart visualizations: {str(e)}")
            return None, None

def main():
    st.markdown("<h1 style='text-align: center;'>PharmaScope</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Pharmaceutical Location Finder</h3>", unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Controls")
    
    # File upload
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV File",
        type=['csv'],
        help="Upload a CSV file with location data"
    )
    
    # Weight sliders
    st.sidebar.subheader("Adjust Factor Weights")
    weights = {
        "GDP ($B)": st.sidebar.slider("GDP Weight", 0, 100, 20) / 100,
        "Healthcare Expenditure (%)": st.sidebar.slider("Healthcare Weight", 0, 100, 20) / 100,
        "Regulatory Score (1-10)": st.sidebar.slider("Regulatory Weight", 0, 100, 20) / 100,
        "Skilled Workforce (1-10)": st.sidebar.slider("Workforce Weight", 0, 100, 20) / 100,
        "Resource Availability (1-10)": st.sidebar.slider("Resource Weight", 0, 100, 20) / 100,
        "Political Stability (1-10)": st.sidebar.slider("Stability Weight", 0, 100, 20) / 100
    }
    
    # Normalize weights
    total_weight = sum(weights.values())
    weights = {k: v/total_weight for k, v in weights.items()}
    
    if uploaded_file is not None:
        # Show loading spinner
        with st.spinner('Loading and processing data...'):
            # Process data
            df = DataProcessor.load_and_process_csv(uploaded_file)
            
            if df is not None:
                # Calculate RAI
                df_with_rai = DataProcessor.calculate_rai(df, weights)
                
                # Display last update time
                st.sidebar.info(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Create tabs for different views
                tab1, tab2, tab3 = st.tabs(["Data View", "Map View", "Analytics"])
                
                with tab1:
                    st.subheader("Location Data and RAI Scores")
                    st.dataframe(
                        df_with_rai.sort_values("RAI", ascending=False)
                        .style.background_gradient(subset=['RAI'], cmap='Blues')
                    )
                    
                    # Export button
                    csv = df_with_rai.to_csv(index=False)
                    st.download_button(
                        "Download Results",
                        csv,
                        "pharmascope_results.csv",
                        "text/csv",
                        key='download-csv'
                    )
                
                with tab2:
                    st.subheader("Geographic Distribution")
                    map_obj = Visualizer.create_map(df_with_rai)
                    if map_obj:
                        st_folium(map_obj, width=800, height=600)
                
                with tab3:
                    st.subheader("Analytics Overview")
                    fig_rai, fig_radar = Visualizer.create_charts(df_with_rai)
                    if fig_rai and fig_radar:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.plotly_chart(fig_rai, use_container_width=True)
                        with col2:
                            st.plotly_chart(fig_radar, use_container_width=True)
                        
                        # Summary statistics
                        st.subheader("Summary Statistics")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Highest RAI Score", 
                                    f"{df_with_rai['RAI'].max():.2f}",
                                    f"Top: {df_with_rai.loc[df_with_rai['RAI'].idxmax(), 'Location']}")
                        with col2:
                            st.metric("Average RAI Score",
                                    f"{df_with_rai['RAI'].mean():.2f}")
                        with col3:
                            st.metric("Number of Locations",
                                    len(df_with_rai))
    else:
        st.info("Please upload a CSV file to begin analysis")
        
        # Sample CSV template
        st.sidebar.markdown("### CSV Template")
        sample_df = pd.DataFrame({
            'Location': ['Sample City'],
            'GDP ($B)': [1000],
            'Healthcare Expenditure (%)': [8.5],
            'Regulatory Score (1-10)': [7.0],
            'Skilled Workforce (1-10)': [8.0],
            'Resource Availability (1-10)': [7.5],
            'Political Stability (1-10)': [8.0],
            'Latitude': [40.7128],
            'Longitude': [-74.0060]
        })
        
        csv = sample_df.to_csv(index=False)
        st.sidebar.download_button(
            "Download Template",
            csv,
            "pharmascope_template.csv",
            "text/csv",
            key='download-template'
        )

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("An unexpected error occurred. Please try again later.")