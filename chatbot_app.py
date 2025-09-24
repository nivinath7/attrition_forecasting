# chatbot_app.py (Complete Professional Chatbot Application)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_processing import prepare_data, get_category_proportions
from forecasting_prophet import get_future_forecast, get_top_down_forecast
from insights_generator import generate_hr_insights, parse_user_query
from ui_components import apply_professional_styling, create_header, create_metric_card, create_section_header
from openai import OpenAI
import json
from datetime import datetime

# Professional page configuration
st.set_page_config(
    page_title="Optum HR AI Chatbot", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply professional styling
apply_professional_styling()

# Professional Header
create_header("🤖 Optum HR AI Assistant", "Intelligent Workforce Analytics & Conversational Forecasting")

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.markdown(create_section_header("⚙️ AI Configuration"), unsafe_allow_html=True)
    
    # OpenAI Configuration
    with st.container():
        st.markdown("#### 🧠 AI Engine Setup")
        if 'openai_client' not in st.session_state:
            st.session_state.openai_client = None
            
        api_key = st.text_input(
            "OpenAI API Key", 
            type="password", 
            help="Enter your OpenAI API key to enable AI-powered conversational analytics"
        )
        
        if api_key and st.session_state.openai_client is None:
            try:
                st.session_state.openai_client = OpenAI(api_key=api_key)
                st.markdown('<div class="status-indicator status-success">✅ AI Engine: Connected & Ready</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown('<div class="status-indicator status-warning">❌ Connection Failed</div>', unsafe_allow_html=True)
                st.error(f"Error: {str(e)}")

    st.markdown("---")
    
    # Data Upload Section
    with st.container():
        st.markdown("#### 📊 Data Management")
        if 'uploaded_data' not in st.session_state:
            st.session_state.uploaded_data = None
            
        uploaded_file = st.file_uploader(
            "Upload Historical Data", 
            type="csv",
            help="Upload your CSV file containing historical attrition data"
        )
        
        if uploaded_file:
            try:
                st.session_state.uploaded_data = pd.read_csv(uploaded_file)
                st.markdown('<div class="status-indicator status-success">✅ Data: Successfully Loaded</div>', unsafe_allow_html=True)
                
                # Data summary
                with st.expander("📋 Data Summary"):
                    st.write(f"**Records:** {st.session_state.uploaded_data.shape[0]:,}")
                    st.write(f"**Features:** {st.session_state.uploaded_data.shape[1]}")
                    if 'ds' in st.session_state.uploaded_data.columns:
                        date_range = pd.to_datetime(st.session_state.uploaded_data['ds'])
                        st.write(f"**Period:** {date_range.min().strftime('%b %Y')} - {date_range.max().strftime('%b %Y')}")
                        
            except Exception as e:
                st.markdown('<div class="status-indicator status-warning">❌ Upload Failed</div>', unsafe_allow_html=True)
                st.error(f"Error: {str(e)}")

# System Status Check
col1, col2 = st.columns([3, 1])

with col2:
    st.markdown(create_section_header("🚦 System Status"), unsafe_allow_html=True)
    
    if st.session_state.openai_client:
        st.markdown('<div class="status-indicator status-success">🤖 AI: Online</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-indicator status-warning">🤖 AI: Offline</div>', unsafe_allow_html=True)
    
    if st.session_state.uploaded_data is not None:
        st.markdown('<div class="status-indicator status-success">📊 Data: Ready</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-indicator status-warning">📊 Data: Missing</div>', unsafe_allow_html=True)

# Main Chat Interface
with col1:
    # Check system readiness
    if st.session_state.openai_client is None:
        st.warning("Please configure your OpenAI API key in the sidebar to enable AI features.")
        st.stop()

    if st.session_state.uploaded_data is None:
        st.warning("Please upload your data file in the sidebar to begin analysis.")
        st.stop()

    df_raw = st.session_state.uploaded_data

    # Chat Interface
    st.markdown(create_section_header("💬 AI Conversation"), unsafe_allow_html=True)

    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
        # Add welcome message
        welcome_msg = """
**Welcome to Optum HR AI Assistant!**

I'm your intelligent workforce analytics companion. I can help you:

• **Generate forecasts** by demographics (gender, marital status, department)
• **Analyze trends** in your historical attrition data  
• **Provide strategic insights** for HR planning
• **Create visualizations** to support decision-making

**Try asking me questions like:**
- "Show me gender-based forecast for next 18 months"
- "What's the department attrition trend for 2 years?"
- "Overall workforce forecast for next 6 months"
        """
        st.session_state.chat_history.append({"role": "assistant", "content": welcome_msg})

    # Helper functions
    def generate_forecast(mode, horizon):
        """Generate forecast based on parsed parameters"""
        try:
            with st.spinner(f"Generating {mode} forecast for {horizon} months..."):
                if mode == "By Department (Top-Down)":
                    df_overall_prepared = prepare_data(df_raw, "Overall")
                    dept_proportions = get_category_proportions(df_raw, "By Department")
                    
                    if df_overall_prepared.empty or not dept_proportions:
                        return None, None, "Unable to prepare data for top-down forecast."
                        
                    future_forecast_df = get_top_down_forecast(df_overall_prepared, dept_proportions, horizon)
                    historical_df_for_plot = prepare_data(df_raw, "By Department")
                else:
                    df_prepared = prepare_data(df_raw, mode)
                    
                    if df_prepared.empty:
                        return None, None, f"Unable to prepare data for {mode} forecast."
                        
                    future_forecast_df = get_future_forecast(df_prepared, horizon)
                    historical_df_for_plot = df_prepared

                if future_forecast_df.empty:
                    return None, None, "Unable to generate forecast."
                    
                return future_forecast_df, historical_df_for_plot, None
        except Exception as e:
            return None, None, f"Error generating forecast: {e}"

    def create_professional_plot(historical_df, forecast_df, mode):
        """Create a professional forecast visualization"""
        historical_plot_df = historical_df.copy()
        historical_plot_df['Type'] = 'Historical'
        
        future_only_df = forecast_df[forecast_df['ds'] > historical_df['ds'].max()].copy()
        future_only_df.rename(columns={'yhat': 'y'}, inplace=True)
        future_only_df['Type'] = 'Forecast'
        
        plot_df = pd.concat([
            historical_plot_df[['ds', 'y', 'unique_id', 'Type']], 
            future_only_df[['ds', 'y', 'unique_id', 'Type']]
        ], ignore_index=True)

        # Create professional plot
        fig = go.Figure()
        
        colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
        line_styles = {'Historical': 'solid', 'Forecast': 'dash'}
        
        for i, category in enumerate(plot_df['unique_id'].unique()):
            for data_type in ['Historical', 'Forecast']:
                data = plot_df[(plot_df['unique_id'] == category) & (plot_df['Type'] == data_type)]
                if not data.empty:
                    fig.add_trace(go.Scatter(
                        x=data['ds'],
                        y=data['y'],
                        mode='lines+markers',
                        name=f"{category} - {data_type}",
                        line=dict(
                            color=colors[i % len(colors)], 
                            dash=line_styles[data_type],
                            width=3 if data_type == 'Historical' else 2
                        ),
                        marker=dict(size=6 if data_type == 'Historical' else 4),
                        hovertemplate=f"<b>{category}</b><br>" +
                                     "Date: %{x|%B %Y}<br>" +
                                     "Departures: %{y:.0f}<br>" +
                                     f"<i>{data_type}</i><extra></extra>"
                    ))
        
        fig.update_layout(
            title=dict(
                text=f'Attrition Analysis: {mode}',
                x=0.5,
                font=dict(size=20, color='#2c3e50', family='Inter')
            ),
            xaxis_title="Timeline",
            yaxis_title="Number of Departures",
            plot_bgcolor='rgba(248,249,250,0.8)',
            paper_bgcolor='white',
            font=dict(family="Inter", size=12),
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(t=80, b=50, l=50, r=50),
            height=500
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        
        return fig

    # Chat Input
    user_question = st.chat_input("Ask me about your workforce attrition forecasts...")

    # Process user question
    if user_question:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        
        # Parse the query
        parsed_params = parse_user_query(user_question, st.session_state.openai_client)
        mode = parsed_params.get("mode", "Overall")
        horizon = parsed_params.get("horizon", 12)
        
        # Generate forecast
        forecast_df, historical_df, error = generate_forecast(mode, horizon)
        
        if error:
            bot_response = f"**Analysis Error**\n\n{error}\n\nPlease check your data format and try again."
            st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
        else:
            # Generate insights
            with st.spinner("Generating strategic insights..."):
                insights = generate_hr_insights(historical_df, forecast_df, mode, st.session_state.openai_client)
            
            # Create visualization
            fig = create_professional_plot(historical_df, forecast_df, mode)
            
            # Calculate key metrics
            future_total = forecast_df[forecast_df['ds'] > historical_df['ds'].max()]['yhat'].sum()
            historical_avg = historical_df['y'].mean()
            trend = "Increasing" if future_total/horizon > historical_avg else "Decreasing"
            
            # Prepare bot response
            bot_response = f"""
### **Analysis Complete**

**Query Analysis:**
- **Forecast Type:** {mode}
- **Time Horizon:** {horizon} months
- **Processing Time:** {datetime.now().strftime('%H:%M:%S')}

**Key Metrics:**
- **Projected Departures:** {future_total:.0f} employees
- **Historical Average:** {historical_avg:.0f} departures/month
- **Forecast Trend:** {trend}

---

### **Strategic Insights**

{insights}
"""
            
            st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
            
            # Store the plot for display
            st.session_state.current_plot = fig
            st.session_state.current_forecast = forecast_df

    # Display chat history
    st.markdown("### Conversation History")
    
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(message["content"])

    # Display current plot if available
    if 'current_plot' in st.session_state:
        st.markdown("---")
        st.plotly_chart(st.session_state.current_plot, use_container_width=True)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("View Raw Data"):
                with st.expander("Detailed Forecast Data", expanded=True):
                    st.dataframe(st.session_state.current_forecast.style.highlight_max(axis=0))
        
        with col2:
            if st.button("Export Data"):
                csv = st.session_state.current_forecast.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"forecast_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
        
        with col3:
            if st.button("New Analysis"):
                del st.session_state.current_plot
                del st.session_state.current_forecast
                st.rerun()

# Sidebar: Quick Actions and Examples
with st.sidebar:
    st.markdown("---")
    
    # Quick Actions
    st.markdown("#### Quick Actions")
    
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        if 'current_plot' in st.session_state:
            del st.session_state.current_plot
        if 'current_forecast' in st.session_state:
            del st.session_state.current_forecast
        st.rerun()
    
    # Example questions
    st.markdown("#### Example Questions")
    example_questions = [
        "Overall forecast for 6 months",
        "Gender analysis for 1 year", 
        "Department trends for 18 months",
        "Marital status forecast 2 years",
        "Show historical patterns"
    ]
    
    for i, example in enumerate(example_questions):
        if st.button(f"{example}", key=f"ex_{i}", use_container_width=True):
            # Trigger the example question
            st.session_state.example_triggered = example

# Handle example questions
if 'example_triggered' in st.session_state:
    # Process the example question as if user typed it
    user_question = st.session_state.example_triggered
    del st.session_state.example_triggered
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; font-size: 0.9rem; padding: 2rem;">
    <p><strong>Optum HR AI Assistant</strong> | Intelligent Workforce Analytics</p>
    <p>Powered by OpenAI GPT • Prophet Forecasting • Advanced Analytics</p>
</div>
""", unsafe_allow_html=True)