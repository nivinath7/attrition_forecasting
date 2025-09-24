# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from data_processing import prepare_data, get_category_proportions
from forecasting_prophet import get_future_forecast, get_top_down_forecast
import numpy as np

st.set_page_config(page_title="Forecasting Dashboard", page_icon="📈", layout="wide")
st.title("✨ Optum HR: Attrition Forecasting Dashboard")

# --- 1. DATA UPLOAD & SESSION STATE ---
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None

uploaded_file = st.sidebar.file_uploader("Upload your historical data (CSV)", type="csv")
if uploaded_file:
    st.session_state.uploaded_data = pd.read_csv(uploaded_file)

if st.session_state.uploaded_data is None:
    st.info("Please upload a CSV file using the sidebar to begin."); st.stop()
    
df_raw = st.session_state.uploaded_data

# --- 2. USER SELECTION ---
st.sidebar.subheader("Dashboard Controls")
forecast_mode = st.sidebar.radio(
    "Select the lens for your analysis:",
    ("Overall", "By Gender", "By Marital Status", "By Department (Top-Down)")
)
horizon = st.sidebar.slider("Select forecast horizon (months)", 1, 24, 12)

# --- 3. FORECAST & PLOT LOGIC ---
st.header(f"Future Attrition Forecast: {forecast_mode}")

if forecast_mode == "By Department (Top-Down)":
    st.sidebar.info("This view uses a 'Top-Down' method to provide a reliable strategic outlook.")
    df_overall_prepared = prepare_data(df_raw, "Overall")
    dept_proportions = get_category_proportions(df_raw, "By Department")
    with st.spinner('Generating top-down forecast...'):
        future_forecast_df = get_top_down_forecast(df_overall_prepared, dept_proportions, horizon)
    historical_df_for_plot = prepare_data(df_raw, "By Department")
else:
    df_prepared = prepare_data(df_raw, forecast_mode)
    with st.spinner(f'Generating {forecast_mode} forecast...'):
        future_forecast_df = get_future_forecast(df_prepared, horizon)
    historical_df_for_plot = df_prepared

st.success("Forecast generated successfully!")

# Plotting with Plotly
historical_plot_df = historical_df_for_plot.copy(); historical_plot_df['Type'] = 'Historical'
future_only_df = future_forecast_df[future_forecast_df['ds'] > historical_plot_df['ds'].max()].copy()
future_only_df.rename(columns={'yhat': 'y'}, inplace=True); future_only_df['Type'] = 'Forecast'
plot_df = pd.concat([historical_plot_df[['ds', 'y', 'unique_id', 'Type']], future_only_df[['ds', 'y', 'unique_id', 'Type']]])

st.subheader("Forecast Visualization")
fig = px.line(
    plot_df, x='ds', y='y', color='unique_id', line_dash='Type',
    labels={'ds': 'Date', 'y': 'Number of Departures', 'unique_id': 'Category'},
    title=f'Attrition Forecast vs. History ({forecast_mode})'
)
fig.update_traces(hovertemplate="<b>%{full_figure_data.name}</b><br>Date: %{x|%B %Y}<br>Departures: %{y:.0f}<extra></extra>")
st.plotly_chart(fig, use_container_width=True)

with st.expander("View Raw Forecast Data"):
    st.dataframe(future_forecast_df)