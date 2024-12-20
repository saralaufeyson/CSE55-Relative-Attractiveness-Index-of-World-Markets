# Pharmascope

## Overview
Pharmascope is a web application built with Streamlit that helps pharmaceutical companies identify ideal locations for their business operations. The application calculates a Relative Attractiveness Index (RAI) using World Bank data to evaluate different countries based on multiple economic and healthcare indicators.

## Features
- Interactive homepage with modern UI design
- RAI Calculator with customizable weights for different factors:
  - GDP
  - Healthcare Expenditure
  - Labor Force
- Data visualization including:
  - Bar charts for RAI comparison
  - Interactive map showing top 12 countries
  - Detailed data tables with raw and aggregated data

## Dependencies
```
streamlit
wbdata
pandas
plotly.express
scikit-learn
datetime
geopy
```

## Installation
1. Clone the repository
2. Install the required dependencies:
```bash
pip install streamlit wbdata pandas plotly scikit-learn geopy
```
3. Run the application:
```bash
streamlit run test10.py
```

## Usage

### Navigation
The application has two main sections:
1. **Home**: Landing page with information about the service
2. **Predictions**: RAI calculation and visualization tools

### RAI Calculator
1. Use the sidebar sliders to adjust weights for:
   - GDP (default: 40%)
   - Healthcare Expenditure (default: 30%)
   - Labor Force (default: 30%)
2. Click "run" to calculate RAI
3. View results in multiple formats:
   - Sorted data table
   - Aggregated country data
   - Bar charts
   - Interactive map of top 12 countries

## Data Sources
- World Bank Indicators:
  - GDP (NY.GDP.MKTP.CD)
  - Healthcare Expenditure (SH.XPD.CHEX.PC.CD)
  - Labor Force (SL.TLF.TOTL.IN)

## Technical Details
- Uses MinMaxScaler for data normalization
- Implements Nominatim geocoding for mapping
- Handles missing data by setting null values to zero
- Provides both raw and aggregated views of the data

## Notes
- The application processes data for over 200 countries
- Missing data is marked as zero in the calculations
- Geographic coordinates are fetched using the Nominatim geocoding service
- The RAI is calculated using normalized values and user-defined weights

## UI Components
- Custom HTML/CSS for the homepage
- Gradient-styled headings
- Responsive design
- Dark theme with purple and cyan accent colors

## License
© 2024 Pharmascope - All Rights Reserved
