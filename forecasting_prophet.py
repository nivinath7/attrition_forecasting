# forecasting.py

import pandas as pd
from prophet import Prophet

def get_future_forecast(df_prepared, horizon=12):
    """
    Generates a future forecast using a default Prophet model for each category.
    """
    all_future_forecasts = pd.DataFrame()
    for uid in df_prepared['unique_id'].unique():
        df_category = df_prepared[df_prepared['unique_id'] == uid]

        model = Prophet()
        model.fit(df_category)

        future_df = model.make_future_dataframe(periods=horizon, freq='MS')
        forecast_df = model.predict(future_df)
        forecast_df['unique_id'] = uid

        all_future_forecasts = pd.concat([all_future_forecasts, forecast_df])
        
    return all_future_forecasts

def get_top_down_forecast(overall_prepared_df, historical_proportions, horizon=12):
    """
    Generates a top-down forecast.
    """
    overall_future_df = get_future_forecast(overall_prepared_df, horizon)
    future_only_df = overall_future_df[overall_future_df['ds'] > overall_prepared_df['ds'].max()].copy()
    
    department_forecasts = []
    for category, proportion in historical_proportions.items():
        dept_df = future_only_df[['ds', 'yhat']].copy()
        dept_df['yhat'] = dept_df['yhat'] * proportion
        dept_df['unique_id'] = category
        department_forecasts.append(dept_df)
        
    final_forecast = pd.concat(department_forecasts)
    return final_forecast