# ui_components.py (Complete Professional UI Components)

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

def apply_professional_styling():
    """Apply professional CSS styling to the Streamlit app"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        .main {
            font-family: 'Inter', sans-serif;
        }
        
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2.5rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            text-align: center;
            color: white;
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
        }
        
        .header-title {
            font-family: 'Inter', sans-serif;
            font-size: 3rem;
            font-weight: 800;
            margin: 0;
            text-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        .header-subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 1.4rem;
            font-weight: 400;
            margin: 1rem 0 0 0;
            opacity: 0.95;
        }
        
        .professional-card {
            background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%);
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            border: 1px solid rgba(102, 126, 234, 0.1);
            margin: 1.5rem 0;
            transition: all 0.4s ease;
        }
        
        .professional-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }
        
        .metric-container {
            background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.08);
            border: 1px solid rgba(102, 126, 234, 0.1);
            margin: 1rem 0;
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .metric-container:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.12);
        }
        
        .metric-title {
            font-family: 'Inter', sans-serif;
            font-size: 1rem;
            font-weight: 500;
            color: #64748b;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .metric-value {
            font-family: 'Inter', sans-serif;
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0;
        }
        
        .section-header {
            font-family: 'Inter', sans-serif;
            font-size: 1.6rem;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 3px solid #667eea;
        }
        
        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem 1.25rem;
            border-radius: 25px;
            font-size: 0.9rem;
            font-weight: 600;
            margin: 0.5rem;
        }
        
        .status-success {
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
        }
        
        .status-warning {
            background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
            color: white;
        }
        
        .status-info {
            background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
            color: white;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 0.8rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        
        .chart-container {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            border: 1px solid rgba(102, 126, 234, 0.1);
            margin: 2rem 0;
        }
        
        .forecast-summary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 20px;
            margin: 2rem 0;
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-top: 1rem;
        }
        
        .summary-item {
            text-align: center;
            padding: 1.5rem;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
    </style>
    """, unsafe_allow_html=True)

def create_header(title, subtitle):
    """Create a professional header section"""
    st.markdown(f"""
    <div class="main-header">
        <h1 class="header-title">{title}</h1>
        <p class="header-subtitle">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def create_metric_card(title, value, delta=None, delta_color="gray"):
    """Create a professional metric card"""
    delta_html = ""
    if delta:
        delta_html = f'<div style="color: {delta_color}; font-size: 0.9rem; margin-top: 0.5rem;">{delta}</div>'
    
    return f"""
    <div class="metric-container">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """

def create_status_indicator(text, status_type="info"):
    """Create a status indicator"""
    return f'<div class="status-indicator status-{status_type}">{text}</div>'

def create_section_header(text):
    """Create a professional section header"""
    return f'<div class="section-header">{text}</div>'

def create_professional_chart(data, chart_type="line", title="", height=500, color_column=None):
    """Create a professional looking chart"""
    
    colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
    
    if chart_type == "line":
        if color_column and color_column in data.columns:
            fig = px.line(data, x=data.columns[0], y=data.columns[1], 
                         color=color_column, title=title, height=height,
                         color_discrete_sequence=colors)
        else:
            fig = px.line(data, x=data.columns[0], y=data.columns[1], 
                         title=title, height=height)
    elif chart_type == "bar":
        fig = px.bar(data, x=data.columns[0], y=data.columns[1], 
                    title=title, height=height, color_discrete_sequence=colors)
    else:
        fig = go.Figure()
    
    # Apply professional styling
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=20, color='#1a202c', family='Inter')
        ),
        plot_bgcolor='rgba(248,249,250,0.3)',
        paper_bgcolor='white',
        font=dict(family="Inter", size=12),
        margin=dict(t=80, b=60, l=60, r=60)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    
    return fig

def display_forecast_summary(forecasted_total, horizon, historical_avg, trend):
    """Display a forecast summary section"""
    avg_monthly_forecast = forecasted_total / horizon if horizon > 0 else 0
    
    st.markdown(f"""
    <div class="forecast-summary">
        <h2 style="margin-bottom: 2rem; text-align: center;">🎯 Forecast Summary</h2>
        <div class="summary-grid">
            <div class="summary-item">
                <h3 style="margin: 0; font-size: 2.2rem;">{forecasted_total:.0f}</h3>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Projected Departures</p>
            </div>
            <div class="summary-item">
                <h3 style="margin: 0; font-size: 2.2rem;">{avg_monthly_forecast:.0f}</h3>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Avg Monthly</p>
            </div>
            <div class="summary-item">
                <h3 style="margin: 0; font-size: 2.2rem;">{horizon}</h3>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Months Ahead</p>
            </div>
            <div class="summary-item">
                <h3 style="margin: 0; font-size: 2.2rem;">{trend}</h3>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Trend</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)