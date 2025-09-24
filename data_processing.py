# data_processing.py

import pandas as pd

def prepare_data(df, mode):
    """
    Prepares data for various forecast modes by creating a continuous monthly timeline.
    """
    date_col = 'ds'
    value_col = 'attrition_count'
    pct_female_col = 'pct_female'
    pct_married_col = 'pct_married'
    department_col = 'top_department'
    
    df[date_col] = pd.to_datetime(df[date_col])
    
    full_date_range = pd.date_range(
        start=df[date_col].min(),
        end=df[date_col].max(),
        freq='MS'
    )
    
    if mode == "Overall":
        df_prep = df.set_index(date_col).resample('MS')[value_col].sum().reindex(full_date_range, fill_value=0).reset_index()
        df_prep.rename(columns={'index': 'ds', value_col: 'y'}, inplace=True)
        df_prep['unique_id'] = 'Overall Attrition'
        
    elif mode == "By Gender":
        monthly_sums = df.set_index(date_col).resample('MS')[value_col].sum().reindex(full_date_range, fill_value=0)
        monthly_pcts = df.set_index(date_col).resample('MS')[pct_female_col].mean().reindex(full_date_range)
        df_gender = pd.merge(monthly_sums, monthly_pcts, left_index=True, right_index=True).reset_index().rename(columns={'index': date_col})
        df_gender.interpolate(method='linear', inplace=True); df_gender.fillna(0, inplace=True)
        
        df_gender['female_count'] = df_gender[value_col] * df_gender[pct_female_col]
        df_gender['male_count'] = df_gender[value_col] * (1 - df_gender[pct_female_col])
        df_female = df_gender[[date_col, 'female_count']].rename(columns={date_col: 'ds', 'female_count': 'y'}); df_female['unique_id'] = 'Female'
        df_male = df_gender[[date_col, 'male_count']].rename(columns={date_col: 'ds', 'male_count': 'y'}); df_male['unique_id'] = 'Male'
        df_prep = pd.concat([df_female, df_male])
        
    elif mode == "By Marital Status":
        monthly_sums = df.set_index(date_col).resample('MS')[value_col].sum().reindex(full_date_range, fill_value=0)
        monthly_pcts = df.set_index(date_col).resample('MS')[pct_married_col].mean().reindex(full_date_range)
        df_marital = pd.merge(monthly_sums, monthly_pcts, left_index=True, right_index=True).reset_index().rename(columns={'index': date_col})
        df_marital.interpolate(method='linear', inplace=True); df_marital.fillna(0, inplace=True)

        df_marital['married_count'] = df_marital[value_col] * df_marital[pct_married_col]
        df_marital['unmarried_count'] = df_marital[value_col] * (1 - df_marital[pct_married_col])
        df_married = df_marital[[date_col, 'married_count']].rename(columns={date_col: 'ds', 'married_count': 'y'}); df_married['unique_id'] = 'Married'
        df_unmarried = df_marital[[date_col, 'unmarried_count']].rename(columns={date_col: 'ds', 'unmarried_count': 'y'}); df_unmarried['unique_id'] = 'Unmarried'
        df_prep = pd.concat([df_married, df_unmarried])

    elif mode == "By Department" or mode == "By Department (Top-Down)":
        all_categories = df[department_col].unique()
        master_index = pd.MultiIndex.from_product([all_categories, full_date_range], names=[department_col, date_col])
        df_monthly = df.groupby(department_col).resample('MS', on=date_col)[value_col].sum()
        df_prep = df_monthly.reindex(master_index, fill_value=0).reset_index()
        df_prep.rename(columns={date_col: 'ds', value_col: 'y', department_col: 'unique_id'}, inplace=True)
    
    else:
        # Default case to prevent errors
        df_prep = pd.DataFrame(columns=['ds', 'y', 'unique_id'])

    df_prep['y'] = df_prep['y'].round().astype(int)
    df_prep.sort_values(['unique_id', 'ds'], inplace=True)
    return df_prep

def get_category_proportions(df, mode):
    """Calculates historical proportions for top-down forecasting."""
    value_col = 'attrition_count'
    if mode == "By Department":
        category_col = 'top_department'
    else: return None
    
    category_totals = df.groupby(category_col)[value_col].sum()
    category_proportions = category_totals / df[value_col].sum()
    return category_proportions