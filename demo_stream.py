import streamlit as st
import pandas as pd
import numpy as np
import tensorflow as tf
# from sklearn.preprocessing import MinMaxScaler # Already in streamlit_app (2).py
import os
import joblib
import plotly.express as px # Already in streamlit_app (2).py

# Load feature data
DATA_PATH = 'nse_features.csv'
df = pd.read_csv(DATA_PATH)
stocks = df['Code'].unique()

# Streamlit UI
st.title("📈 NSE Stock Price Predictor") # Title from streamlit_app (2).py

selected_stock = st.selectbox("Choose a stock ticker:", sorted(stocks))

# Display the sector of the selected stock (FROM app_demo.py)
if selected_stock:
    try:
        sector = df[df['Code'] == selected_stock]['Sector'].iloc[0]
        st.write(f"**Sector:** {sector}")
    except IndexError:
        st.error("Sector information not found for the selected stock.")
    except KeyError:
        st.error("The 'Sector' column is missing from the nse_features.csv file.")

# Filter and sort data (FROM streamlit_app (2).py)
stock_data = df[df['Code'] == selected_stock].copy()
stock_data['Date'] = pd.to_datetime(stock_data['Date'], errors='coerce')
stock_data = stock_data.sort_values(by='Date')

# Layout: Tabs for Trend and Prediction (FROM streamlit_app (2).py)
tab1, tab2 = st.tabs(["📊 Recent Price Trend", "🤖 Predict Next Price"])

# Tab 1: Price Trend (FROM streamlit_app (2).py)
with tab1:
    st.subheader(f"{selected_stock} - Interactive Price Trend")
    # ... (rest of the trend tab code from streamlit_app (2).py) ...

# Tab 2: Prediction (FROM streamlit_app (2).py)
with tab2:
    st.subheader("Predict Tomorrow's Price")
    if st.button("Predict"): # Note: app_demo.py also has a predict button, ensure logic is merged cleanly if different
        try:
            # ... (rest of the prediction tab code from streamlit_app (2).py) ...
        except Exception as e:
            st.error(f"Prediction failed: {e}")