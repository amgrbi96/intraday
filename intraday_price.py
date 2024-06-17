import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

# Function to fetch and process intraday data
def get_intraday_data(ticker, period='30d', interval='15m'):
    st.write(f"Fetching data for {ticker}, Period: {period}, Interval: {interval}")
    # Download historical data
    try:
        data = yf.download(ticker, period=period, interval=interval)
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

    # Ensure we have data
    if data.empty:
        st.error(f"No data found for {ticker}")
        return None

    # Reset index to move the datetime index into a column
    data.reset_index(inplace=True)

    # Check if 'Datetime' column exists and is properly formatted
    if 'Datetime' in data.columns:
        data['Datetime'] = pd.to_datetime(data['Datetime'])
    elif 'date' in data.columns:  # Sometimes it can be lowercase 'date'
        data['Datetime'] = pd.to_datetime(data['date'])
    else:
        st.error(f"No 'Datetime' column found in data for {ticker}")
        return None

    # Extract the date and time from the datetime index
    data['Date'] = data['Datetime'].dt.date
    data['Time'] = data['Datetime'].dt.time

    # Pivot the table to get closing prices for each 15-minute interval
    pivot_df = data.pivot(index='Date', columns='Time', values='Close')

    return pivot_df

# Streamlit app
st.title('Intraday Price Data v2')

# Input fields for ticker, duration, and interval
ticker = st.text_input('Enter the ticker symbol (e.g., AAPL, MSFT, GOOGL):', 'AAPL')
duration = st.selectbox('Select the duration:', ['7d', '14d', '30d', '60d', '90d'], index=2)
interval = st.selectbox('Select the interval:', ['1m', '5m', '15m', '30m', '60m'], index=2)

# Button to fetch data
if st.button('Fetch Data'):
    # Fetch and process the data
    df = get_intraday_data(ticker, period=duration, interval=interval)
    
    # Display the data in a table
    if df is not None:
        st.subheader(f'{ticker} - {interval} Interval Closing Prices for the Last {duration}')
        st.dataframe(df)
    else:
        st.write(f'No data available for {ticker}')

    # Log the data fetched
    st.write("Data Fetch Attempt Completed")
