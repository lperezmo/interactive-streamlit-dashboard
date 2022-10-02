import streamlit as st
import pandas as pd
import plotly.express as px
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import numpy as np
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
import datetime

##########################################################################
# DEFINE IMPORTANT FUNCTIONS
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

def previous_week_range(date, n_weeks):
    """
    Get the start and end date of previous N weeks.
    """
    start_delta = datetime.timedelta(date.weekday(), weeks=n_weeks)
    start_of_week = datetime.datetime.now().date() - start_delta
    end_of_week = start_of_week+datetime.timedelta(days=5)
    return start_of_week, end_of_week

def get_range_for_previous_weeks(number_of_weeks=3):
    """
    Get the range of dates where week starts and ends (Mon-Sat).
    """
    calendar_ref = pd.DataFrame()
    starts = []
    ends = []
    for i in range(1,number_of_weeks+1):
        _start, _end = previous_week_range(date=datetime.datetime.now(), n_weeks=i)
        starts.append(_start)
        ends.append(_end)
    calendar_ref['STARTS'] = starts
    calendar_ref['ENDS'] = ends
    calendar_ref.sort_values(by='STARTS', inplace=True, ascending=False,ignore_index=True)
    return calendar_ref

def get_daily_hr_totals(df, dur_col_name = 'DURATION', grosspay=False, wage=17):
    """
    Get total hours per day for all dataframe.
    Returns a dataframe with daily totals in pretty format.
    """
    if grosspay is True:
        daily_hr_totals = pd.DataFrame()
        daily_hr_totals['Date'] = [f"{i:%A, %B %d, %Y}" for i in df['DATE']]
        daily_hr_totals['Daily total hours'] = [f"{i.components.hours} hrs and {i.components.minutes} min" for i in df[dur_col_name]]
        daily_hr_totals['Gross pay'] = [(i.components.hours)*wage + (i.components.minutes/60)*wage for i in df[dur_col_name]]
    else:
        daily_hr_totals = pd.DataFrame()
        daily_hr_totals['Date'] = [f"{i:%A, %B %d, %Y}" for i in df['DATE']]
        daily_hr_totals['Daily total hours'] = [f"{i.components.hours} hrs and {i.components.minutes} min" for i in df[dur_col_name]]
    return daily_hr_totals

def get_weekly_hr_totals(df, dur_col_name = 'DURATION', n_weeks=3, grosspay=False, wage=17):
    """
    Get weekly hr totals from a dataframe.
    Returns a dataframe with weekly totals in pretty format.
    """
    calref = get_range_for_previous_weeks(number_of_weeks=n_weeks)
    # n_weeks = 3
    weekly_hr_total = pd.DataFrame()
    _weekly_hrs = []
    _gross_pay =[]
    if grosspay is True:
       for i in range(n_weeks):
            if df[df['DATE']<=calref['ENDS'][i]][dur_col_name].sum().components.days == 0:
                _internalhrs = df[df['DATE']<=calref['ENDS'][i]][dur_col_name].sum().components.hours
                _internalmin = df[df['DATE']<=calref['ENDS'][i]][dur_col_name].sum().components.minutes
                # print(f"Total hours for week between {calref['STARTS'][i]:%a, %b %d} and {calref['ENDS'][i]:%a, %b %d}: \t {_weekly_hrs.components.hours} hrs and {_weekly_hrs.components.hours} min") 
                _weekly_hrs.append(f"{_internalhrs} hrs and {_internalmin} min")
            else:
                _internalhrs = df[df['DATE']<=calref['ENDS'][i]][dur_col_name].sum().components.days*24+df[df['DATE']<=calref['ENDS'][i]][dur_col_name].sum().components.hours
                _internalmin = df[df['DATE']<=calref['ENDS'][i]][dur_col_name].sum().components.minutes
                # print(f"Total hours for week between {calref['STARTS'][i]:%a, %b %d} and {calref['ENDS'][i]:%a, %b %d}: \t {_weekly_hrs.components.hours} hrs and {_weekly_hrs.components.hours} min") 
                _weekly_hrs.append(f"{_internalhrs} hrs and {_internalmin} min")
                _gross_pay.append((_internalhrs)*wage + (_internalmin/60)*wage)
    else:
        for i in range(n_weeks):
            if df[df['DATE']<=calref['ENDS'][i]][dur_col_name].sum().components.days == 0:
                _internalhrs = df[df['DATE']<=calref['ENDS'][i]][dur_col_name].sum().components.hours
                # print(f"Total hours for week between {calref['STARTS'][i]:%a, %b %d} and {calref['ENDS'][i]:%a, %b %d}: \t {_weekly_hrs.components.hours} hrs and {_weekly_hrs.components.hours} min") 
                _weekly_hrs.append(f"{_internalhrs} hrs and {df[df['DATE']<=calref['ENDS'][i]][dur_col_name].sum().components.minutes} min")
            else:
                _internalhrs = df[df['DATE']<=calref['ENDS'][i]][dur_col_name].sum().components.days*24+df[df['DATE']<=calref['ENDS'][i]][dur_col_name].sum().components.hours
                # print(f"Total hours for week between {calref['STARTS'][i]:%a, %b %d} and {calref['ENDS'][i]:%a, %b %d}: \t {_weekly_hrs.components.hours} hrs and {_weekly_hrs.components.hours} min") 
                _weekly_hrs.append(f"{_internalhrs} hrs and {df[df['DATE']<=calref['ENDS'][i]][dur_col_name].sum().components.minutes} min")

    # weekly_hr_total['Week between:'] = [f"{calref['STARTS'][i]:%a, %b %d} and {calref['ENDS'][i]:%a, %b %d}" for i in range(n_weeks)]
    weekly_hr_total['Description'] = [f"Total hours for week(s) selected" for i in range(n_weeks)]
    weekly_hr_total['Total hours'] = _weekly_hrs
    if grosspay is True:
        weekly_hr_total['Gross pay'] = _gross_pay

    if n_weeks>1:
        weekly_hr_total = weekly_hr_total.iloc[1:,0:]
    else:
        pass
    return weekly_hr_total

##########################################################################
# FILTER DATAFRAME BY SELECTED CHOICES
def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Edited to add some filters by default, like
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    df = df.copy()
    _start, _end = previous_week_range(date=datetime.datetime.now(), n_weeks=1)
    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
    #     if col == 'Start Time' or col == 'End Time':
    #         pass
    #     else:
    #         if is_object_dtype(df[col]):
    #             try:
    #                 df[col] = pd.to_datetime(df[col])
    #             except Exception:
    #                 pass

    #         if is_datetime64_any_dtype(df[col]):
    #             df[col] = df[col].dt.tz_localize(None)
        if col == 'DATE':
            if is_object_dtype(df[col]):
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass

            if is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.tz_localize(None)


    modification_container = st.sidebar.container()
    str_name = str()
    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns, default='DATE')
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            custom_columns = ['First Name', 'Last Name', 'Supervisor']
            ###############################################
            # Custom selectors: (to force drop down menus and whatnot)
            if column == custom_columns[2]:
                if is_categorical_dtype(df[column]) or df[column].nunique() < 2:
                    user_cat_input = right.multiselect(
                        f"Choose supervisor:",
                        df[column].unique(),
                        default=list(df[column].unique()),
                    )
                    df = df[df[column].isin(user_cat_input)]
                    str_name = str_name+str(user_cat_input) 
                    st.write(str_name)       
                else:
                    left, right = st.columns((1, 20))
                    user_cat_input = right.multiselect(
                                f"Choose supervisor:",
                                df[column].unique(),
                                )
                    df = df[df[column].isin(user_cat_input)]
                    str_name = str_name+str(column)+str(user_cat_input) 
            if column == custom_columns[1]:
                if is_categorical_dtype(df[column]) or df[column].nunique() < 2:
                    user_cat_input = right.multiselect(
                        f"Choose last name:",
                        df[column].unique(),
                        default=list(df[column].unique()),
                    )
                    df = df[df[column].isin(user_cat_input)]
                    str_name = str_name+str(user_cat_input)        
                else:
                    left, right = st.columns((1, 20))
                    user_cat_input = right.multiselect(
                                f"Choose last name:",
                                df[column].unique(),
                                )
                    df = df[df[column].isin(user_cat_input)]
                    str_name = str_name+str(column)+str(user_cat_input)       
            if column == custom_columns[0]:
                if is_categorical_dtype(df[column]) or df[column].nunique() < 2:
                    user_cat_input = right.multiselect(
                        f"Choose first name:",
                        df[column].unique(),
                        default=list(df[column].unique()),
                    )
                    df = df[df[column].isin(user_cat_input)]
                else:
                    left, right = st.columns((1, 20))
                    user_cat_input = right.multiselect(
                                f"Choose first name:",
                                df[column].unique(),
                                )
                    df = df[df[column].isin(user_cat_input)]
                    str_name = str_name+str(column)+str(user_cat_input)       
            ################################################
            # Treat columns with < 2 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 2 and column not in custom_columns:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
                str_name = str_name+str(column)+str(user_cat_input)       

            elif is_numeric_dtype(df[column]) and column not in custom_columns:
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
                str_name = str_name+str(column)+str(user_num_input)       

            elif is_datetime64_any_dtype(df[column]) and column not in custom_columns:
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        # df[column].min(),
                        # df[column].max(),
                        _start,
                        _end
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
                # str_name = str_name+str(column)+str(user_date_input)      
            ################################################
            # Since they want only drop down lists, consider getting rid of this one altogether
            ################################################
            elif column not in custom_columns:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df, str_name
##########################################################################
# Get data and prepare plots
# TITLE AND IMAGES
st.sidebar.image('https://s3.dualstack.us-east-2.amazonaws.com/pythondotorg-assets/media/files/python-logo-only.svg', width=None)
st.title("Sample hour checking application for employees")
st.caption('Written & designed by Luis Perez Morales')

###########################################################################
# READ OR IMPORT DATA HERE
# Main data
calref = get_range_for_previous_weeks(number_of_weeks=3)
df = pd.DataFrame()
df['START'] = ['2022-09-17 06:49:50',
               '2022-09-19 06:49:50', 
               '2022-09-20 06:53:17',
              '2022-09-21 06:33:17',
              '2022-09-22 06:44:17',
              '2022-09-23 06:40:17']
df['START'] = pd.to_datetime(df['START'])
df['END'] = ['2022-09-17 17:05:14', 
            '2022-09-19 17:05:14', 
             '2022-09-20 16:53:17',
             '2022-09-21 16:59:11',
             '2022-09-22 17:33:10',
             '2022-09-23 16:32:38']
df['END'] = pd.to_datetime(df['END'])
df['DURATION'] = df['END'] - df['START']
df['DATE'] = [df['START'][i].date() for i in df.index]
filtered_df = filter_dataframe(df)

###########################################################################
# SHOW INTERACTIVE TABLE AND OPTIONS
st.subheader("See your hours below:")
gd = GridOptionsBuilder.from_dataframe(df)
gridoptions = gd.build()
grid_table = AgGrid(filtered_df,
                    height=200,
                    gridOptions=gridoptions,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    # theme="material"
                    )

# Save as CSV for own records
csv = convert_df(filtered_df)
st.download_button(label='Download data for your own records',
                    data = csv,
                    file_name = "current_changes.csv",
                    mime='text/csv')

###########################################################################
# TOTAL HOURS & OPTIONAL GROSS PAY
st.subheader('Click here to input your current hourly wage and see your gross pay along with total hours')
wage_hr = st.text_input('OPTIONAL: Write down your hourly wage if you want gross wage calculated for you:')
n_weeks = st.text_input('Number of weeks to calculate data for:', '1')

if wage_hr:
    n_weeks = int(n_weeks)
    wage_hr = float(wage_hr)
    weekly_hrs = get_weekly_hr_totals(filtered_df, grosspay=True, wage=wage_hr, n_weeks=n_weeks)    
    daily_hrs = get_daily_hr_totals(filtered_df, grosspay=True, wage=wage_hr)
else:
    n_weeks = int(n_weeks)
    weekly_hrs = get_weekly_hr_totals(filtered_df, n_weeks=n_weeks)
    daily_hrs = get_daily_hr_totals(filtered_df)

st.subheader("Total hours per week:")
st.dataframe(weekly_hrs, use_container_width=True)
st.subheader("Total hours per day:")
st.dataframe(daily_hrs, use_container_width=True)

###########################################################################
