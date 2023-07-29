#api doc: https://rapidapi.com/alphavantage/api/alpha-vantage/

import pandas as pd
import requests
import plotly.graph_objects as go
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import folium
import seaborn as sns
from streamlit_folium import folium_static

st.set_page_config(
    page_title = "HCI - Streamlit",
    layout = "wide",
    menu_items = {
        'Get Help' : 'https://docs.streamlit.io',
        'Report a bug' : 'https://google.com',
        'About' : 'WebApp to display Forex Statistics'
    }
)
st.title("Currency Performance Analyzer")
# function = "INTRADAY"
# timeInterval = "5min"
# toCurr = "USD"
# fromCurr = "EUR"

if 'data' not in st.session_state:
    st.session_state.data = None
if 'mapData' not in st.session_state:
    st.session_state.mapData = None
if 'mapInfo' not in st.session_state:
    st.session_state.mapInfo = None

col1, col2, col3, col4, col5 = st.columns([1,1,.2,.2,1])
with col1:
    function = st.selectbox("Time Range",
                        options = ["IntraDay", "Weekly", "Daily", "Monthly"]
                        )
with col2:
    if function == "IntraDay":
        timeInterval = st.selectbox("Time Interval",
                            options = ["1min", "5min", "30min", "60min"]
                            )
    else:
        timeInterval = st.selectbox("Time Interval",disabled = True,
                            options = ["1min", "5min", "30min", "60min"]
                            )
with col3:
    toCurr = st.radio("To:",
                        options = ["USD", "EUR", "JPY"]
                        )
with col4:
    fromCurr = st.radio("From:",
                        options = ["EUR", "USD", "JPY"]
                        )
with col5:
    toggle = st.checkbox("Supplemental Data",value=True)

time_series = st.session_state.data
if st.session_state.data == None:
    #API Retrieval Data
    url = "https://alpha-vantage.p.rapidapi.com/query"
    if function == "IntraDay":
        querystring = {"function":"FX_"+function,"interval":timeInterval,"to_symbol":toCurr,"from_symbol":fromCurr,"datatype":"json","outputsize":"compact"}
        timeSeries = timeInterval
    else:
        querystring = {"function":"FX_"+function,"to_symbol":toCurr,"from_symbol":fromCurr,"datatype":"json","outputsize":"compact"}
        timeSeries = function
    headers = {
        "X-RapidAPI-Key": "42ceb880c3msh05de72c30c08239p119463jsnf3d7e6d9512e",
        "X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring).json()
    st.session_state.data = response["Time Series FX (" + timeSeries +")"]
    time_series = st.session_state.data

if st.button("Retrieve"):
    if fromCurr == toCurr:
        st.error("Error: Currencies cannot be the same")
    #API Retrieval Data
    else:
        url = "https://alpha-vantage.p.rapidapi.com/query"
        if function == "IntraDay":
            querystring = {"function":"FX_"+function,"interval":timeInterval,"to_symbol":toCurr,"from_symbol":fromCurr,"datatype":"json","outputsize":"compact"}
            timeSeries = timeInterval
        else:
            querystring = {"function":"FX_"+function,"to_symbol":toCurr,"from_symbol":fromCurr,"datatype":"json","outputsize":"compact"}
            timeSeries = function
        headers = {
            "X-RapidAPI-Key": "42ceb880c3msh05de72c30c08239p119463jsnf3d7e6d9512e",
            "X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring).json()
        st.session_state.data = response["Time Series FX (" + timeSeries +")"]
        time_series = st.session_state.data

"___"
st.subheader("Candlesticks")
# Create a list of dictionaries for each time point
time_points = []
for time, values in time_series.items():
    time_point = {
        "Time": pd.to_datetime(time),
        "Open": float(values["1. open"]),
        "High": float(values["2. high"]),
        "Low": float(values["3. low"]),
        "Close": float(values["4. close"]),
    }
    time_points.append(time_point)

# Create a DataFrame from the list of dictionaries
df = pd.DataFrame(time_points)

# Create the candlestick graph using Plotly
fig = go.Figure(data=[go.Candlestick(x=df['Time'],
                                    open=df['Open'],
                                    high=df['High'],
                                    low=df['Low'],
                                    close=df['Close'])])

# Set axis titles
fig.update_layout(
    xaxis_title="Time",
    yaxis_title="Price ("+toCurr+")"
)
#Enlarge graph
fig.update_layout(height=600, width=1600)
# Display the graph
st.plotly_chart(fig) 

if toggle == True:
    st.divider()
    st.subheader("Supplemental Data")
    col1, col2, col3 = st.columns([1,.5,1])
    with col1:
        #raw Data displayed
        parameters = st.multiselect(
                "View One or More Parameters from Complete DataSet",
                ["Open", "High", "Low", "Close" ]
            )
        st.dataframe(df[["Time"] + parameters])

    with col2:
        st.dataframe(df.describe(include=[np.number]))

    with col3:
        # Assuming you want to create the boxplot for all the numeric columns in the DataFrame
        numeric_columns = df.select_dtypes(include=[np.number]).columns

        # Create a figure and axes
        fig, ax = plt.subplots()

        # Plot the boxplot using seaborn
        sns.boxplot(data=df[numeric_columns], ax=ax)

        # Show the plot in Streamlit
        st.pyplot(fig)

"---"
st.subheader("Currency Map")
# Define the currency codes
currency_codes = [
    "USD",
    "EUR",
    "JPY",
    "GBP",
    "AUD",
    "CAD",
    "CHF",
    "CNY",
    "SEK",
    "NZD",
    "MXN",
    "SGD",
    "HKD",
    "NOK",
    "KRW"
]

# Create a DataFrame with the location coordinates and country names
world = pd.DataFrame(
    [
        [37.0902, -95.7129, "United States"],
        [47.5162, 14.5501, "Eurozone"],
        [36.2048, 138.2529, "Japan"],
        [55.3781, -3.4360, "United Kingdom"],
        [-25.2744, 133.7751, "Australia"],
        [56.1304, -106.3468, "Canada"],
        [46.8182, 8.2275, "Switzerland"],
        [35.8617, 104.1954, "China"],
        [60.1282, 18.6435, "Sweden"],
        [-40.9006, 174.8860, "New Zealand"],
        [23.6345, -102.5528, "Mexico"],
        [1.3521, 103.8198, "Singapore"],
        [22.3193, 114.1694, "Hong Kong"],
        [60.4720, 8.4689, "Norway"],
        [35.9078, 127.7669, "South Korea"]
    ],
    columns=['lat', 'lon', 'country']
)

# Define the currency symbols for each country
currency_symbols = {
    "United States": "$",
    "Eurozone": "€",
    "Japan": "¥",
    "United Kingdom": "£",
    "Australia": "$",
    "Canada": "$",
    "Switzerland": "Fr",
    "China": "¥",
    "Sweden": "kr",
    "New Zealand": "$",
    "Mexico": "$",
    "Singapore": "$",
    "Hong Kong": "$",
    "Norway": "kr",
    "South Korea": "₩"
}

# Create a list to store the prices for each country
prices = []
choice = st.text_input('Input Currency to be Mapped:', value = "USD")
if choice not in currency_codes:
    st.info('Available Currency codes are: USD, EUR, JPY, GBP, AUD, CAD, CHF, CNY, SEK, NZD, MXN, SGD, HKD, NOK, KRW', icon="ℹ️")
if choice != st.session_state.mapData:
    for currency, symbol in zip(currency_codes, currency_symbols.values()):
        url = "https://currency-converter-by-api-ninjas.p.rapidapi.com/v1/convertcurrency"
        querystring = {"have": choice, "want": currency, "amount": "1"}
        headers = {
            "X-RapidAPI-Key": "42ceb880c3msh05de72c30c08239p119463jsnf3d7e6d9512e",
            "X-RapidAPI-Host": "currency-converter-by-api-ninjas.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring).json()
        new_amount = response.get('new_amount')
        if new_amount is not None:
            price = symbol + str(new_amount)
            prices.append(price)
    st.session_state.mapInfo = prices
    st.session_state.mapData = choice
elif choice == st.session_state.mapData:
    prices = st.session_state.mapInfo

if choice in currency_codes:
    map = st.select_slider(
        'Map Style',
        options=['CartoDB Positron', 'Stamen Watercolor', 'CartoDB dark_matter', 'OpenStreetMap', 'Stamen Toner', 'Stamen Terrain'])
    # Create a Folium Map object centered at the location
    m = folium.Map(location=[0, 0], zoom_start=2, tiles=map)

    # Add a marker for each coordinate with a custom icon and currency symbol as a popup and caption
    for i, row in world.iterrows():
        currency_symbol = currency_symbols.get(row['country'], "")
        price = prices[i]
        caption = f"{row['country']} ({price})"
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=currency_symbol,
            tooltip=caption,  # Set caption as tooltip
            icon=folium.Icon(color='red', icon='star')
        ).add_to(m)

    # Display the map in Streamlit
    folium_static(m, width=1600)