import streamlit as st
import pandas as pd
import numpy as np
import datetime

# DEFINE IMPORTANT FUNCTIONS
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

def get_daily_hr_totals(df, dur_col_name = 'DURATION'):
    """
    Get total hours per day for all dataframe.
    Returns a dataframe with daily totals in pretty format.
    """
    daily_hr_totals = pd.DataFrame()
    daily_hr_totals['Date'] = [f"{i:%A, %B %d, %Y}" for i in df['DATE']]
    daily_hr_totals['Daily total hours'] = [f"{i.components.hours} hrs and {i.components.hours} min" for i in df[dur_col_name]]
    return daily_hr_totals

def get_weekly_hr_totals(df, dur_col_name = 'DURATION'):
    """
    Get weekly hr totals from a dataframe.
    Returns a dataframe with weekly totals in pretty format.
    """
    n_weeks = 3
    weekly_hr_total = pd.DataFrame()
    _weekly_hrs = []
    for i in range(n_weeks):
        if df[df['DATE']<=calref['ENDS'][i]][dur_col_name].sum().components.days == 0:
            _internalhrs = df[df['DATE']<=calref['ENDS'][i]][dur_col_name].sum().components.hours
            # print(f"Total hours for week between {calref['STARTS'][i]:%a, %b %d} and {calref['ENDS'][i]:%a, %b %d}: \t {_weekly_hrs.components.hours} hrs and {_weekly_hrs.components.hours} min") 
            _weekly_hrs.append(f"{_internalhrs} hrs and {df[df['DATE']<=calref['ENDS'][i]][dur_col_name].sum().components.minutes} min")
        else:
            _internalhrs = df[df['DATE']<=calref['ENDS'][i]][dur_col_name].sum().components.days*24+df[df['DATE']<=calref['ENDS'][i]][dur_col_name].sum().components.hours
            # print(f"Total hours for week between {calref['STARTS'][i]:%a, %b %d} and {calref['ENDS'][i]:%a, %b %d}: \t {_weekly_hrs.components.hours} hrs and {_weekly_hrs.components.hours} min") 
            _weekly_hrs.append(f"{_internalhrs} hrs and {df[df['DATE']<=calref['ENDS'][i]][dur_col_name].sum().components.hours} min")

    weekly_hr_total['Week between:'] = [f"{calref['STARTS'][i]:%a, %b %d} and {calref['ENDS'][i]:%a, %b %d}" for i in range(n_weeks)]
    weekly_hr_total['Total hours'] = _weekly_hrs
    return weekly_hr_total

# START REF CALENDAR
calref = get_range_for_previous_weeks(number_of_weeks=3)

# MAIN DATA
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

daily_hrs = get_daily_hr_totals(df)
weekly_hrs = get_weekly_hr_totals(df)

st.header("Dashboard")
st.dataframe(daily_hrs)
st.dataframe(weekly_hrs)