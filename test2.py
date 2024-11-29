import streamlit as st
import wbdata
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PharmaRAICalculator:
    def __init__(self):
        # Configure Streamlit page
        st.set_page_config(
            page_title="Pharma Location RAI Calculator", 
            layout="wide", 
            initial_sidebar_state="expanded"
        )
        
        # Define countries with full names for better representation
        self.countries = {
            'IN': 'India', 
            'US': 'United States', 
            'CN': 'China', 
            'JP': 'Japan', 
            'DE': 'Germany'
        }
        
        # Comprehensive World Bank indicators
        self.indicators = {
            'NY.GDP.MKTP.CD': 'GDP',  # GDP (current US$)
            'SH.XPD.CHEX.PC.CD': 'Healthcare Expenditure Per Capita',  # Healthcare expenditure
            'SL.TLF.TOTL.IN': 'Total Labor Force',  # Total labor force
            'TX.VAL.TECH.CD': 'High-Tech Exports',  # High-tech exports
            'SP.POP.TOTL': 'Total Population',  # Total population
            'NY.GDP.PCAP.CD': 'GDP Per Capita'  # GDP per capita
        }
        
    def fetch_world_bank_data(self, start_year=2015, end_year=2023):
        """
        Fetch data from World Bank with comprehensive error handling
        """
        try:
            # Convert years to datetime
            start_date = datetime(start_year, 1, 1)
            end_date = datetime(end_year, 1, 1)
            
            # Fetch data for all indicators and countries
            st.info("Fetching data from World Bank API...")
            
            # Combine all indicators for fetching
            full_indicators = {k: v for k, v in self.indicators.items()}
            
            # Fetch data
            data = wbdata.get_dataframe(
                full_indicators, 
                country=list(self.countries.keys()), 
                data_date=(start_date, end_date)
            )
            
            # Reset index and rename columns
            data = data.reset_index()
            data.columns = ['Year', 'Country'] + list(self.indicators.values())
            
            # Replace country codes with full names
            data['Country'] = data['Country'].map(self.countries)
            
            st.success("Data collection complete!")
            return data
        
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            logger.error(f"Data fetch error: {e}")
            return None
    
    def normalize_data(self, data):
        """
        Normalize data using advanced techniques
        """
        try:
            # Select numeric columns for normalization
            numeric_columns = [
                'GDP', 
                'Healthcare Expenditure Per Capita', 
                'Total Labor Force',
                'High-Tech Exports',
                'Total Population',
                'GDP Per Capita'
            ]
            
            # Create a copy of the dataframe
            normalized_data = data.copy()
            
            # Use sklearn's MinMaxScaler for robust normalization
            scaler = MinMaxScaler()
            
            # Normalize selected columns
            normalized_data[numeric_columns] = scaler.fit_transform(
                normalized_data[numeric_columns]
            )
            
            return normalized_data
        
        except Exception as e:
            st.error(f"Normalization error: {e}")
            logger.error(f"Data normalization error: {e}")
            return None
    
    def calculate_rai(self, normalized_data, weights):
        """
        Calculate Relative Attractiveness Index (RAI)
        """
        try:
            # Select columns for RAI calculation
            rai_columns = [
                'GDP', 
                'Healthcare Expenditure Per Capita', 
                'Total Labor Force',
                'High-Tech Exports',
                'Total Population',
                'GDP Per Capita'
            ]
            
            # Weighted sum calculation
            normalized_data['RAI'] = sum(
                normalized_data[col] * weight 
                for col, weight in zip(rai_columns, weights)
            )
            
            # Scale RAI to 0-100 for better interpretation
            min_rai = normalized_data['RAI'].min()
            max_rai = normalized_data['RAI'].max()
            normalized_data['RAI'] = ((normalized_data['RAI'] - min_rai) / (max_rai - min_rai)) * 100
            
            return normalized_data
        
        except Exception as e:
            st.error(f"RAI calculation error: {e}")
            logger.error(f"RAI calculation error: {e}")
            return None
    
    def visualize_results(self, data):
        """
        Create comprehensive visualizations
        """
        # Tabbed interface for different views
        tab1, tab2, tab3 = st.tabs(
            ["RAI Scores", "Comparative Analysis", "Geospatial View"]
        )
        
        with tab1:
            # RAI Scores Bar Chart
            fig_rai = px.bar(
                data, 
                x='Country', 
                y='RAI', 
                color='Year',
                title='RAI Scores by Country and Year'
            )
            st.plotly_chart(fig_rai, use_container_width=True)
        
        with tab2:
            # Radar Chart for Top Country
            top_country = data.loc[data['RAI'].idxmax()]
            
            categories = [
                'GDP', 
                'Healthcare Expenditure Per Capita', 
                'Total Labor Force',
                'High-Tech Exports',
                'Total Population',
                'GDP Per Capita'
            ]
            
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=[top_country[cat] for cat in categories],
                theta=categories,
                fill='toself'
            ))
            
            fig_radar.update_layout(
                title=f'Metrics for Top Performing Country: {top_country["Country"]}'
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
        
        with tab3:
            # Geospatial Visualization
            locations = {
                'India': [20.5937, 78.9629], 
                'United States': [37.0902, -95.7129], 
                'China': [35.8617, 104.1954],
                'Japan': [36.2048, 138.2529],
                'Germany': [51.1657, 10.4515]
            }
            
            m = folium.Map(location=[20, 0], zoom_start=2)
            marker_cluster = MarkerCluster().add_to(m)
            
            for country, coords in locations.items():
                country_data = data[data['Country'] == country]
                rai_score = country_data['RAI'].values[0] if len(country_data) > 0 else 0
                
                folium.CircleMarker(
                    location=coords,
                    radius=rai_score/10,  # Size proportional to RAI
                    popup=f"{country}: RAI {rai_score:.2f}",
                    color='blue',
                    fill=True,
                    fill_opacity=0.7
                ).add_to(marker_cluster)
            
            st_folium(m, width=800, height=500)
    
    def run(self):
        """
        Main application runner
        """
        st.title("Pharmaceutical Location RAI Calculator")
        
        # Sidebar for weight adjustments
        st.sidebar.header("RAI Calculation Weights")
        
        # Dynamic weight sliders
        weights = []
        columns = [
            'GDP', 
            'Healthcare Expenditure Per Capita', 
            'Total Labor Force',
            'High-Tech Exports',
            'Total Population',
            'GDP Per Capita'
        ]
        
        for col in columns:
            weight = st.sidebar.slider(f"Weight for {col}", 0, 100, 20)
            weights.append(weight)
        
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # Fetch and process data
        data = self.fetch_world_bank_data()
        
        if data is not None:
            # Normalize data
            normalized_data = self.normalize_data(data)
            
            # Calculate RAI
            rai_data = self.calculate_rai(normalized_data, normalized_weights)
            
            if rai_data is not None:
                # Display RAI data
                st.subheader("RAI Calculation Results")
                st.dataframe(rai_data)
                
                # Visualize results
                self.visualize_results(rai_data)
                
                # Export option
                csv = rai_data.to_csv(index=False)
                st.download_button(
                    "Download RAI Results",
                    csv,
                    "pharma_rai_results.csv",
                    "text/csv",
                    key='download-csv'
                )

def main():
    calculator = PharmaRAICalculator()
    calculator.run()

if __name__ == "__main__":
    main()