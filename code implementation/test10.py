import streamlit as st
import wbdata
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
import pandas as pd
from geopy.geocoders import Nominatim


def render_homepage():
    homepage_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pharmascope</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montaga&display=swap');
            * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Montaga', serif; }
            body { background-color: #000; color: #fff; line-height: 1.6; }
            h1, h2 { text-align: left; font-weight: 600; background: linear-gradient(180deg, #7F1EEB, #00FFD9);
                     -webkit-background-clip: text; -webkit-text-fill-color: transparent; padding: 20px; }
            .header { text-align: center; padding: 40px; }
            .header img { width: 480px; }
            .about-container { display: flex; justify-content: space-around; padding: 40px; }
            .section { width: 45%; padding: 20px; border: 2px solid transparent; border-radius: 20px;
                       background: linear-gradient(#000, #000) padding-box, linear-gradient(90deg, #7F1EEB, #00FFD9) border-box; }
            footer { text-align: center; margin-top: 40px; padding: 20px; background: #111; }
        </style>
    </head>
    <body>
        <div class="header">
            <img src="https://i.ibb.co/9GP6hyP/Frame-4.png" alt="Logo">
            <h1>Map the Future of Pharma</h1>
            <p>Discover the perfect place to bring innovation to life.</p>
        </div>
        <div class="about-container">
            <div class="section">
                <h2>About Us</h2>
                <p>We're making pharmaceutical analytics practical—because medicines <a href="#">save lives</a>.</p>
            </div>
            <div class="section">
                <h2>What We Offer</h2>
                <p>Discover <a href="#">ideal locations</a> for your business with our customizable solutions.</p>
            </div>
        </div>
        <footer>
            &copy; 2024 Pharmascope | <a href="#">Home</a> | <a href="#">About Us</a> | <a href="#">Our Services</a>
        </footer>
    </body>
    </html>
    """
    st.markdown(homepage_html, unsafe_allow_html=True)

# Function to calculate RAI
def calculate_rai():
    st.title("Pharma RAI Calculator")
    
    # Country codes and indicators
    all_countries = [
    "AF", "AL", "DZ", "AS", "AD", "AO", "AG", "AR", "AM", "AU", "AT", "AZ",
    "BS", "BH", "BD", "BB", "BY", "BE", "BZ", "BJ", "BT", "BO", "BA", "BW",
    "BR", "BN", "BG", "BF", "BI", "CV", "KH", "CM", "CA", "CF", "TD", "CL",
    "CN", "CO", "KM", "CG", "CR", "CI", "HR", "CU", "CY", "CZ", "DK", "DJ",
    "DM", "DO", "EC", "EG", "SV", "GQ", "ER", "EE", "SZ", "ET", "FJ", "FI",
    "FR", "GA", "GM", "GE", "DE", "GH", "GR", "GD", "GT", "GN", "GW", "GY",
    "HT", "HN", "HU", "IS", "IN", "ID", "IR", "IQ", "IE", "IL", "IT", "JM",
    "JP", "JO", "KZ", "KE", "KI", "KR", "KW", "KG", "LA", "LV", "LB", "LS",
    "LR", "LY", "LI", "LT", "LU", "MG", "MW", "MY", "MV", "ML", "MT", "MH",
    "MR", "MU", "MX", "FM", "MD", "MC", "MN", "ME", "MA", "MZ", "MM", "NA",
    "NR", "NP", "NL", "NZ", "NI", "NE", "NG", "NO", "OM", "PK", "PW", "PA",
    "PG", "PY", "PE", "PH", "PL", "PT", "QA", "RO", "RU", "RW", "KN", "LC",
    "VC", "WS", "SM", "ST", "SA", "SN", "RS", "SC", "SL", "SG", "SK", "SI",
    "SB", "ZA", "ES", "LK", "SD", "SR", "SE", "CH", "SY", "TJ", "TZ", "TH",
    "TL", "TG", "TO", "TT", "TN", "TR", "TM", "TV", "UG", "UA", "AE", "GB",
    "US", "UY", "UZ", "VU", "VE", "VN", "YE", "ZM", "ZW"
]
 # Limited list for testing
    indicators = {
        'NY.GDP.MKTP.CD': 'GDP',
        'SH.XPD.CHEX.PC.CD': 'Healthcare Expenditure',
        'SL.TLF.TOTL.IN': 'Labor Force'
    }

    st.write("Fetching data from World Bank...")
    try:
        data = wbdata.get_dataframe(indicators, country=all_countries)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return

    data.reset_index(inplace=True)
    data.columns = ['Country', 'Year', 'GDP', 'Healthcare Expenditure', 'Labor Force']
    data.fillna(0, inplace=True)

    # Weights for calculation
    st.sidebar.header("Adjust Weights")
    gdp_weight = st.sidebar.slider("GDP Weight", 0, 100, 40)
    healthcare_weight = st.sidebar.slider("Healthcare Weight", 0, 100, 30)
    labor_weight = st.sidebar.slider("Labor Force Weight", 0, 100, 30)
    if st.button("run"):
        weights = [gdp_weight, healthcare_weight, labor_weight]
        normalized_weights = [w / sum(weights) for w in weights]

    # Normalize and calculate RAI
        scaler = MinMaxScaler()
        normalized_data = pd.DataFrame(
            scaler.fit_transform(data[['GDP', 'Healthcare Expenditure', 'Labor Force']]),
            columns=['GDP', 'Healthcare Expenditure', 'Labor Force']
        )
        normalized_data['RAI'] = (
            normalized_data['GDP'] * normalized_weights[0] +
            normalized_data['Healthcare Expenditure'] * normalized_weights[1] +
            normalized_data['Labor Force'] * normalized_weights[2]
        )
        data['RAI'] = normalized_data['RAI']
        st.write("RAI Calculation Complete:")
        st.write("*the data which is not available is marked as zero")
   # adata=data.groupby('Country', as_index=False).mean()
        st.dataframe(data.sort_values('RAI',ascending=False))

        st.write("aggregated data")
        numeric_columns = ['GDP', 'Healthcare Expenditure', 'Labor Force','RAI']
        aggregated_data = data.groupby('Country', as_index=False)[numeric_columns].mean()
        st.dataframe(aggregated_data)

    # Visualization
        st.subheader("Top Countries by RAI")
        fig = px.bar(data.sort_values('RAI', ascending=False), x='Country', y='RAI', title="Relative Attractiveness Index")
        st.plotly_chart(fig)

        st.subheader("Top Countries by RAI2")
        fig = px.bar(aggregated_data.sort_values('RAI', ascending=False), x='Country', y='RAI', title="Relative Attractiveness Index")
        st.plotly_chart(fig)
    # Assuming `data` is your DataFrame and RAI is already calculated
        top_12 = aggregated_data.sort_values('RAI', ascending=False).head(12)
        mapping=top_12['Country'].tolist()
        st.write(mapping)

        st.write("Top 12 Countries with Highest RAI")
        st.dataframe(top_12)

        def get_coordinates(country_name):
            geolocator = Nominatim(user_agent="pharma_rai_calculator")
            try:
                location = geolocator.geocode(country_name)
                if location:
                    return location.latitude, location.longitude
                else:
                    return 0, 0
            except Exception as e:
                print(f"Error fetching coordinates for {country_name}: {e}")
                return 0, 0
        coordinates_data = []
        for country in mapping:
            latitude, longitude = get_coordinates(country)
            coordinates_data.append([country, latitude, longitude])
            coordinates_df = pd.DataFrame(coordinates_data, columns=['Country', 'Latitude', 'Longitude'])
        print(coordinates_df)
        
        coordinates_df.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'}, inplace=True)
        st.map(coordinates_df)
        st.write(coordinates_df)
    


# Main function to control navigation
def main():
    st.set_page_config(page_title="Pharmascope", page_icon="⚕️", layout="wide")
    st.sidebar.title("Navigation")
    menu = ["Home", "Predictions"]
    choice = st.sidebar.radio("Go to", menu)

    if choice == "Home":
        render_homepage()
    elif choice == "Predictions":
        calculate_rai()


if __name__ == "__main__":
    main()

