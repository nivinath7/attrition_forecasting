# insights_generator.py (Complete Professional Version)

import pandas as pd
from openai import OpenAI
import streamlit as st
import json

def parse_user_query(query, client):
    """
    Uses OpenAI to parse the user's query and extract entities.
    """
    if client is None: 
        return {"mode": "Overall", "horizon": 12}
        
    system_prompt = """
    You are an expert at parsing user requests for a forecasting tool.
    Extract two key pieces of information from the user's query:
    1. 'mode': The type of forecast. Must be one of ['Overall', 'By Gender', 'By Marital Status', 'By Department (Top-Down)'].
    2. 'horizon': The number of months to forecast, as an integer.
    
    Guidelines:
    - If user mentions "gender", "male", "female" -> use "By Gender"
    - If user mentions "marital", "married", "single", "unmarried" -> use "By Marital Status"  
    - If user mentions "department", "dept", "team", "division" -> use "By Department (Top-Down)"
    - If no specific category mentioned -> use "Overall"
    - If no time period mentioned -> use 12 months
    - Extract numbers for horizon: "6 months"->6, "1 year"->12, "2 years"->24, etc.
    - Common phrases: "next year"->12, "next 6 months"->6, "18 months"->18
    
    Respond ONLY with a JSON object in the format:
    {"mode": "extracted_mode", "horizon": extracted_horizon_as_int}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt}, 
                {"role": "user", "content": query}
            ],
            temperature=0,
            max_tokens=100
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Validate the result
        valid_modes = ['Overall', 'By Gender', 'By Marital Status', 'By Department (Top-Down)']
        if result.get('mode') not in valid_modes:
            result['mode'] = 'Overall'
        
        if not isinstance(result.get('horizon'), int) or result.get('horizon') < 1:
            result['horizon'] = 12
        
        return result
        
    except Exception as e:
        print(f"Error parsing query with OpenAI: {e}")
        return {"mode": "Overall", "horizon": 12}

def generate_hr_insights(historical_df, forecast_df, forecast_mode, client):
    """
    Generates strategic HR insights using OpenAI's GPT model.
    """
    if client is None:
        return "OpenAI client not authenticated. Please configure your API key to generate insights."

    try:
        # Calculate basic metrics
        total_historical = historical_df['y'].sum()
        future_part_df = forecast_df[forecast_df['ds'] > historical_df['ds'].max()].copy()
        
        if future_part_df.empty:
            return "No future forecast data available to generate insights."
        
        total_forecasted = future_part_df['yhat'].sum()
        
        # Find peak forecast period with robust error handling
        peak_forecast_month = "N/A"
        peak_forecast_value = 0
        
        if not future_part_df.empty and 'yhat' in future_part_df.columns:
            try:
                # Handle idxmax() returning Series when there are duplicate max values
                peak_indices = future_part_df['yhat'].idxmax()
                
                # Ensure we get a scalar index
                if isinstance(peak_indices, pd.Series):
                    peak_index = peak_indices.iloc[0]
                else:
                    peak_index = peak_indices
                    
                peak_date_value = future_part_df.loc[peak_index, 'ds']
                peak_forecast_value = future_part_df.loc[peak_index, 'yhat']
                
                # Robust datetime formatting
                try:
                    # Ensure we have a scalar datetime value
                    if isinstance(peak_date_value, pd.Series):
                        peak_date_scalar = peak_date_value.iloc[0]
                    else:
                        peak_date_scalar = peak_date_value
                    
                    # Convert to datetime and format
                    peak_date_dt = pd.to_datetime(peak_date_scalar)
                    peak_forecast_month = peak_date_dt.strftime('%B %Y')
                    
                except Exception as date_error:
                    print(f"Error formatting peak date: {date_error}")
                    peak_forecast_month = "N/A"
                    
            except Exception as peak_error:
                print(f"Error finding peak forecast: {peak_error}")

        # Calculate additional metrics
        historical_months = len(historical_df['ds'].unique())
        forecast_months = len(future_part_df['ds'].unique())
        historical_avg = total_historical / historical_months if historical_months > 0 else 0
        forecast_avg = total_forecasted / forecast_months if forecast_months > 0 else 0
        
        # Build data summary
        data_summary = f"""
        Historical and Forecasted Attrition Data Summary for Optum India HR ({forecast_mode} view):
        - Total historical attrition (last {historical_months} months): {total_historical:.0f} employees
        - Historical monthly average: {historical_avg:.1f} employees
        - Total forecasted attrition (next {forecast_months} months): {total_forecasted:.0f} employees  
        - Forecasted monthly average: {forecast_avg:.1f} employees
        - Trend: {'Increasing' if forecast_avg > historical_avg else 'Decreasing'} ({((forecast_avg/historical_avg-1)*100):+.1f}% change)
        - Peak attrition predicted: {peak_forecast_month} with {peak_forecast_value:.0f} employees
        """
        
        # Add category breakdown for non-overall analyses
        if forecast_mode not in ["Overall", "By Department (Top-Down)"]:
            try:
                historical_by_cat = historical_df.groupby('unique_id')['y'].sum()
                forecast_by_cat = future_part_df.groupby('unique_id')['yhat'].sum()
                data_summary += "\n\nBreakdown by Category:\n"
                for cat in historical_by_cat.index:
                    hist_val = historical_by_cat.get(cat, 0)
                    forecast_val = forecast_by_cat.get(cat, 0)
                    change_pct = ((forecast_val/hist_val - 1) * 100) if hist_val > 0 else 0
                    data_summary += f"- {cat}: Historical={hist_val:.0f}, Forecasted={forecast_val:.0f} ({change_pct:+.1f}% change)\n"
            except Exception as e:
                print(f"Error generating category breakdown: {e}")
        
    except Exception as e:
        print(f"Error creating data summary: {e}")
        return f"Could not generate insights due to data processing error: {str(e)}"

    # Generate AI insights
    prompt = f"""
    You are a strategic HR analyst for Optum, a leading healthcare technology company.
    Analyze the following workforce attrition forecast and provide actionable insights.

    **Data Summary:**
    {data_summary}

    **Instructions:**
    Based on the data summary, provide a professional executive briefing with:

    1. **Key Findings** (2-3 bullet points)
       - Most significant trends or patterns
       - Critical insights for leadership attention

    2. **Business Impact Assessment** (2-3 bullet points)  
       - Potential operational consequences
       - Financial or resource implications
       - Risk factors to consider

    3. **Strategic Recommendations** (3-4 bullet points)
       - Specific, actionable HR initiatives
       - Timeline suggestions for implementation
       - Success metrics to track

    Keep your analysis:
    - Professional and executive-level
    - Focused on business outcomes
    - Actionable with clear next steps
    - Data-driven and objective
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a strategic HR consultant providing executive-level workforce analytics insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return f"Could not generate AI insights due to API error: {str(e)}. Basic analysis shows {total_forecasted:.0f} projected departures over {forecast_months} months."

def generate_consolidated_insights(all_insights, all_forecasts, horizon, client):
    """
    Generate consolidated strategic insights across multiple analysis types.
    """
    if client is None:
        return "OpenAI client not available for consolidated analysis."
    
    try:
        # Calculate aggregate metrics
        total_analyses = len(all_insights)
        analysis_types = list(all_insights.keys())
        
        # Aggregate forecast totals
        total_projected = 0
        for mode, forecast_df in all_forecasts.items():
            future_only = forecast_df[forecast_df['ds'] > forecast_df['ds'].iloc[0]]  # Simplified future filter
            total_projected += future_only['yhat'].sum()
        
        avg_monthly_impact = total_projected / (horizon * total_analyses) if total_analyses > 0 else 0
        
        consolidated_prompt = f"""
        You are the Chief People Officer at Optum, reviewing comprehensive workforce analytics.
        
        **Executive Summary:**
        - Analysis Types Completed: {', '.join(analysis_types)}
        - Forecast Horizon: {horizon} months  
        - Combined Projected Impact: {total_projected:.0f} departures
        - Average Monthly Impact: {avg_monthly_impact:.0f} departures
        
        **Individual Analysis Insights:**
        {chr(10).join([f"• {mode}: {insight[:200]}..." for mode, insight in all_insights.items()])}
        
        **Request:**
        As CPO, provide a consolidated strategic response addressing:
        
        1. **Executive Summary** - Top 2 strategic priorities
        2. **Resource Planning** - Budget and staffing implications  
        3. **Implementation Roadmap** - 90-day action plan
        4. **Success Metrics** - KPIs to monitor progress
        
        Keep recommendations at C-level strategic focus, not tactical details.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Chief People Officer providing strategic workforce planning guidance."},
                {"role": "user", "content": consolidated_prompt}
            ],
            temperature=0.6,
            max_tokens=400
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error generating consolidated insights: {e}")
        return f"Consolidated analysis shows {total_projected:.0f} projected departures across {total_analyses} analysis types over {horizon} months."