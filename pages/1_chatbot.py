# pages/1_💬_Chatbot.py

import streamlit as st
import pandas as pd
import plotly.express as px
from data_processing import prepare_data, get_category_proportions
from forecasting_prophet import get_future_forecast, get_top_down_forecast

# --- A simple, rule-based parser. No OpenAI needed. ---
def parse_simple_query(query):
    """Parses the user query for mode and horizon without AI."""
    query_lower = query.lower()
    mode = "Overall" # Default
    
    if "gender" in query_lower:
        mode = "By Gender"
    elif "marital" in query_lower:
        mode = "By Marital Status"
    elif "department" in query_lower:
        mode = "By Department (Top-Down)"
    
    try:
        horizon = int(''.join(filter(str.isdigit, query)))
        if horizon == 0 or horizon > 24: horizon = 12
    except:
        horizon = 12
        
    return {"mode": mode, "horizon": horizon}


st.set_page_config(page_title="Attrition Forecast Chatbot", layout="wide")
st.title("🤖 Attrition Forecast Chatbot")

# Check if data has been uploaded on the main page
if 'uploaded_data' not in st.session_state or st.session_state.uploaded_data is None:
    st.warning("Please go to the main 'Dashboard' page and upload a data file first.")
    st.stop()

# --- CHATBOT UI ---
st.write("Ask a question to get a specific forecast visualization.")
st.info("Examples: 'Show the Overall forecast for 9 months' or 'What is the forecast by gender for 6 months?'")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        if "fig" in message:
            st.plotly_chart(message["fig"], use_container_width=True)
        st.markdown(message["content"])

if prompt := st.chat_input("What is your attrition question?"):
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Generating forecast based on your query..."):
            df_raw = st.session_state.uploaded_data
            parsed_query = parse_simple_query(prompt)
            
            mode = parsed_query.get("mode", "Overall")
            horizon = parsed_query.get("horizon", 12)
            
            # --- Forecast Logic ---
            if mode == "By Department (Top-Down)":
                df_overall_prepared = prepare_data(df_raw, "Overall")
                dept_proportions = get_category_proportions(df_raw, "By Department")
                forecast_df = get_top_down_forecast(df_overall_prepared, dept_proportions, horizon)
            else:
                df_prepared = prepare_data(df_raw, mode)
                forecast_df = get_future_forecast(df_prepared, horizon)
            
            # --- Create and display the plot ---
            historical_data_for_plot = prepare_data(df_raw, mode)
            future_only_df_chat = forecast_df[forecast_df['ds'] > historical_data_for_plot['ds'].max()]
            
            fig_chat = px.line(
                future_only_df_chat, x='ds', y='yhat', color='unique_id',
                title=f"Forecast for {mode} for the Next {horizon} Months",
                labels={'ds': 'Date', 'yhat': 'Projected Departures'}
            )
            
            response_text = f"Here is the requested forecast for **{mode}** for the next **{horizon} months**."
            
            st.markdown(response_text)
            st.plotly_chart(fig_chat, use_container_width=True)
            
            st.session_state.chat_messages.append({"role": "assistant", "content": response_text, "fig": fig_chat})