import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Load the data
def load_data():
    try:
        df = pd.read_csv('nse_features.csv')
        # Try multiple date formats
        try:
            df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
        except:
            try:
                df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
            except:
                df['Date'] = pd.to_datetime(df['Date'])  # Let pandas infer format
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()  # Return empty dataframe if error occurs


df = load_data()

# Set page config
st.set_page_config(page_title="NSE Stock Analysis", layout="wide")

# Sidebar filters
st.sidebar.title("Filters")
selected_sector = st.sidebar.selectbox("Select Sector", ['All'] + sorted(df['Sector'].unique().tolist()))
selected_stock = st.sidebar.selectbox("Select Stock", ['All'] + sorted(df['Name'].unique().tolist()))
date_range = st.sidebar.date_input("Date Range", 
                                  [df['Date'].min(), df['Date'].max()],
                                  min_value=df['Date'].min(),
                                  max_value=df['Date'].max())

# Apply filters
if selected_sector != 'All':
    df = df[df['Sector'] == selected_sector]
if selected_stock != 'All':
    df = df[df['Name'] == selected_stock]
if len(date_range) == 2:
    df = df[(df['Date'] >= pd.to_datetime(date_range[0])) & 
            (df['Date'] <= pd.to_datetime(date_range[1]))]

# Dashboard title
st.title("Nairobi Securities Exchange (NSE) Stock Analysis Dashboard")

# Key metrics
st.header("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Stocks", df['Name'].nunique())
col2.metric("Total Sectors", df['Sector'].nunique())
col3.metric("Average Daily Volume", f"{df['Volume'].mean():,.0f}")
col4.metric("Average Price Change", f"{df['Change%'].mean():.2f}%")

# Stock price trends
st.header("Stock Price Trends")
tab1, tab2, tab3 = st.tabs(["Daily Prices", "Moving Averages", "RSI Analysis"])

with tab1:
    fig = px.line(df, x='Date', y='Day Price', color='Name', 
                  title='Daily Stock Prices')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = go.Figure()
    for stock in df['Name'].unique():
        stock_df = df[df['Name'] == stock]
        fig.add_trace(go.Scatter(
            x=stock_df['Date'], 
            y=stock_df['SMA_10'], 
            name=f'{stock} - SMA 10', 
            line=dict(dash='dot')
        ))
        fig.add_trace(go.Scatter(
            x=stock_df['Date'], 
            y=stock_df['SMA_50'], 
            name=f'{stock} - SMA 50', 
            line=dict(dash='dash')
        ))
        fig.add_trace(go.Scatter(
            x=stock_df['Date'], 
            y=stock_df['Day Price'], 
            name=f'{stock} - Price', 
            line=dict(width=2)
        ))
    fig.update_layout(title='Moving Averages Analysis')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    fig = px.line(df, x='Date', y='RSI', color='Name', 
                  title='Relative Strength Index (RSI)',
                  labels={'RSI': 'RSI (14-period)'})
    fig.add_hline(y=70, line_dash="dash", line_color="red", 
                  annotation_text="Overbought (70)", annotation_position="bottom right")
    fig.add_hline(y=30, line_dash="dash", line_color="green", 
                  annotation_text="Oversold (30)", annotation_position="top right")
    st.plotly_chart(fig, use_container_width=True)

# Sector analysis
st.header("Sector Analysis")
sector_df = df.groupby('Sector').agg({
    'Day Price': 'mean',
    'Volume': 'sum',
    'Change%': 'mean',
    'Name': 'nunique'
}).reset_index().rename(columns={'Name': 'Stock Count'})

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(sector_df, x='Sector', y='Stock Count', 
                 title='Number of Stocks by Sector')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(sector_df, x='Sector', y='Volume', 
                 title='Total Trading Volume by Sector')
    st.plotly_chart(fig, use_container_width=True)

# Top performers
st.header("Top Performers")
tab1, tab2, tab3 = st.tabs(["Gainers", "Losers", "Most Active"])

with tab1:
    gainers = df.groupby('Name')['Change%'].mean().sort_values(ascending=False).head(10)
    fig = px.bar(gainers, x=gainers.index, y=gainers.values,
                 title='Top 10 Stocks by Average Daily Gain (%)',
                 labels={'y': 'Average Daily Change (%)', 'index': 'Stock'})
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    losers = df.groupby('Name')['Change%'].mean().sort_values().head(10)
    fig = px.bar(losers, x=losers.index, y=losers.values,
                 title='Top 10 Stocks by Average Daily Loss (%)',
                 labels={'y': 'Average Daily Change (%)', 'index': 'Stock'})
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    active = df.groupby('Name')['Volume'].sum().sort_values(ascending=False).head(10)
    fig = px.bar(active, x=active.index, y=active.values,
                 title='Top 10 Most Actively Traded Stocks',
                 labels={'y': 'Total Volume', 'index': 'Stock'})
    st.plotly_chart(fig, use_container_width=True)

# Stock details table
st.header("Stock Details")
st.dataframe(df[['Date', 'Name', 'Sector', 'Day Price', 'Change%', 'Volume', 
                'SMA_10', 'SMA_50', 'RSI']].sort_values('Date', ascending=False),
             use_container_width=True)

# Download button
st.download_button(
    label="Download Filtered Data as CSV",
    data=df.to_csv(index=False).encode('utf-8'),
    file_name='filtered_stock_data.csv',
    mime='text/csv'
)