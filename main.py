##########################################################################
# IMPORT PACKAGES AND DEPENDENCIES
import os
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
# from st_aggrid.shared import ColumnsAutoSizeMode
# from st_aggrid.shared import GridUpdateMode, DataReturnMode, JsCode, walk_gridOptions, ColumnsAutoSizeMode, AgGridTheme
import datetime
# Use the full page instead of a narrow central column
st.set_page_config(page_title='Example App by LPM', page_icon='https://raw.githubusercontent.com/pyinstaller/pyinstaller/develop/PyInstaller/bootloader/images/icon-windowed.ico', layout="wide")
##########################################################################
# DEFINE IMPORTANT FUNCTIONS
@st.experimental_memo
def get_data_from_sql(days_past_due=0):
    # Main data
    # calref = get_range_for_previous_weeks(number_of_weeks=3)
    df = pd.DataFrame()
    df['NAMES'] = ['BOB',
                    'BOB',
                    'ALICE',
                    'BOB',
                    'ALICE',
                    'ALICE']
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
    df['DATE'] = [df['START'][i].date() for i in df.index]
    # filtered_df = df.copy()
    df['DURATION'] = df['END'] - df['START']
    return df
# @st.cache
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
    if grosspay==True:
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
    if grosspay==True:
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
    weekly_hr_total['Description'] = [f"Total hours for {n_weeks} weeks selected" for i in range(n_weeks)]
    weekly_hr_total['Total hours'] = _weekly_hrs
    if grosspay ==True:
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
        if col == 'Date':
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
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns, default=["DATE"])
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            custom_columns = ['DATE', 'Last Name', 'Supervisor']
            ###############################################
            # Custom selectors: (to force drop down menus and whatnot)
            if column == custom_columns[2]:
                if is_categorical_dtype(df[column]) or df[column].nunique() < 3:
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
                if is_categorical_dtype(df[column]) or df[column].nunique() < 3:
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
                if is_categorical_dtype(df[column]) or df[column].nunique() < 3:
                    user_cat_input = right.multiselect(
                        f"Choose first name:",
                        df[column].unique(),
                        default=list(df[column].unique()),
                    )
                    df = df[df[column].isin(user_cat_input)]
                else:
                    user_date_input = right.date_input(
                        f"Values for {column}",
                        value=(
                            df[column].min(),
                            df[column].max(),
#                             _start,
#                             _end
                        ),
                    )
                    if len(user_date_input) == 2:
                        user_date_input = tuple(map(pd.to_datetime, user_date_input))
                        start_date, end_date = user_date_input
                        df = df.loc[df[column].between(start_date, end_date)]       
            ################################################
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 3 and column not in custom_columns:
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
                        df[column].min(),
                        df[column].max(),
#                         _start,
#                         _end
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
st.sidebar.image('https://www.python.org/static/community_logos/python-logo-generic.svg')
st.title("Sample hour checking program for employees")
st.caption('Written & designed by Luis Perez Morales')
###########################################################################
# GET DATA
df = get_data_from_sql()
filtered_df, str_name = filter_dataframe(df)
##########################################################################
# SHOW TABLE AND OPTIONS
st.subheader("See your hours below:")
cols_to_be_shown = ['START', 'END', 'DATE']
st.dataframe(filtered_df.loc[:, cols_to_be_shown], use_container_width=True)
# gd = GridOptionsBuilder.from_dataframe(filtered_df.loc[:, cols_to_be_shown])
# gridoptions = gd.build()
# grid_table = AgGrid(filtered_df.loc[:, cols_to_be_shown],
#                     height=200,
#                     ColumnsAutoSizeMode = ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
#                     gridOptions=gridoptions,
#                     update_mode=GridUpdateMode.SELECTION_CHANGED,
#                     use_container_width = True,
#                     # theme="material"
#                     )

# Save as CSV for own records
csv = convert_df(filtered_df.loc[:, cols_to_be_shown])
st.download_button(label='Download data for your own records',
                    data = csv,
                    file_name = "current_changes.csv",
                    mime='text/csv')
    # st.success("Changes saved to csv")

###########################################################################
# GANTT TIMELINE GRAPH
st.subheader("Timeline of your work, choose the different options to color and annotate graph:")
# to do later
# discrete_map_resource = dict colors by column

# get figure
color_options = st.selectbox("Color Gantt Chart by:", ['DATE'],index=0)
text_options = st.selectbox("Text description on bars:", [None, 'DATE', 'DURATION', 'NAMES'],index=0)

# @st.experimental_memo
def get_gantt_chart(color_options, text_options):
    fig = px.timeline(filtered_df, x_start='START',x_end='END',y='NAMES', color=color_options,text=text_options)
    fig.update_yaxes(autorange='reversed')
    return fig

# Get data for graph, get figure, and show figure
fig = get_gantt_chart(color_options, text_options)
st.plotly_chart(fig, use_container_width=False)  #Display the plotly chart in Streamlit

###########################################################################
# TOTAL HOURS & EVEN GROSS PAY
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
# CREDITS AT THE END OF SIDEBAR
st.sidebar.markdown('# Credits')
st.sidebar.markdown("### Written & Designed by Luis Perez Morales.")
# st.sidebar.markdown("Changes made on 9/23/22: \n*Optimized when SQL query is made, making program x20 times faster. \n*Fixed launchers.")
###########################################################################
