import streamlit as st
import yfinance as yf
import pandas as pd
from retrying import retry

# Function to fetch and process intraday data with retry mechanism
@retry(stop_max_attempt_number=3, wait_fixed=2000)  # Retry up to 3 times with a 2-second wait between retries
def get_intraday_data(ticker, period='30d', interval='15m'):
    try:
        data = yf.download(ticker, period=period, interval=interval)
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

    if data.empty:
        st.warning(f"No data returned for {ticker}.")
        return None

    # Ensure the datetime index is properly formatted
    if 'Datetime' in data.columns:
        data['Datetime'] = pd.to_datetime(data['Datetime'])
    else:
        st.error(f"Invalid data format for {ticker}. No 'Datetime' column found.")
        return None

    data['Date'] = data['Datetime'].dt.date
    data['Time'] = data['Datetime'].dt.time

    # Pivot the table to get closing prices for each 15-minute interval
    pivot_df = data.pivot(index='Date', columns='Time', values='Close')

    return pivot_df

# Streamlit app
st.title('Intraday Price Data')

# Input fields for ticker, duration, and interval
ticker = st.text_input('Enter the ticker symbol (e.g., AAPL, MSFT, GOOGL, 7010.SR):', 'AAPL')
duration = st.selectbox('Select the duration:', ['7d', '14d', '30d', '60d', '90d'], index=2)
interval = st.selectbox('Select the interval:', ['1m', '5m', '15m', '30m', '60m'], index=2)

# Button to fetch data
if st.button('Fetch Data'):
    df = get_intraday_data(ticker, period=duration, interval=interval)
    
    if df is not None:
        st.subheader(f'{ticker} - {interval} Interval Closing Prices for the Last {duration}')
        st.dataframe(df)
    else:
        st.write(f'No data available for {ticker}')

# To run the Streamlit app, save this script as `app.py` and execute the following command in your terminal:
# streamlit run app.py

