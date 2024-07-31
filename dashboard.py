import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

from ydata_profiling import ProfileReport
# from streamlit_pandas_profiling import st_profile_report
import streamlit.components.v1 as components

# --- Data Import

df = pd.read_csv("weather_cleaned.csv")
df.drop('Unnamed: 0', axis=1, inplace=True)

# Convert 'date' column to datetime
df['date'] = pd.to_datetime(df['date'])

# --- HEADLINE

st.title('''Relationship between *Temperature* and *Global Radiation* in London''')

st.write("![](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgyFh5eZI4XmaGbZ96SPRft3nPp-KdbXe1iYbVXRdknMfD9F6PaK5yVXZfLmDavxjARD6kTpuRl6xAhyphenhyphenUHobRQqNPkPjov3QHP556OLzCKwudN3_PYc2IufH0IBjLNTubQGPqD2g_8xino/s1600/WEATHER+LONDON+UK.jpg)")

st.markdown("---")

# --- DESCRIPTION
st.write("The aim of this project is to identify the relationship between mean temperature and global radiation using [Daily Historical London Weather Data from 1979 to 2021](https://www.kaggle.com/datasets/emmanuelfwerr/london-weather-data/data).")

st.write('''
We will be able to visually analyze and determine if there any change of temperature throughout the year, that indicates climate change in London?
To achieve our objective, we need to do a data profiling by clicking the button below and analyze it through data visualization.
         ''')

## --- BUTTON
with st.expander("Data Profiling"):
    if st.button("Start Profiling London Weather Data"):

        ## Generate Report
        #---- progile report using ydata profiling
        pr = ProfileReport(df)

        # Display to streamlit
        pr_html = pr.to_html()

        # HTML wrapper with scrolling enabled
        scrollable_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                }}
                #container {{
                    height: 800px; /* Adjust the height as needed */
                    overflow: auto;
                    padding: 10px;
                }}
            </style>
        </head>
        <body>
            <div id="container">
                {pr_html}
            </div>
        </body>
        </html>
        """

        components.html(pr_html, height = 800, scrolling=True)

# --- Description

with st.expander("Weather Data in London Throughout the Year"):

    df_copy = df.copy()

    # Min-Max Normalization Function
    def min_max_normalize(column):
        return (column - column.min()) / (column.max() - column.min())

    # Apply normalization to 'mean_temp' and 'global_radiation'
    df_copy['mean_temp_normalized'] = min_max_normalize(df_copy['mean_temp'])
    df_copy['global_radiation_normalized'] = min_max_normalize(df_copy['global_radiation'])

    # Streamlit widgets for filtering
    start_date = st.date_input('Start date', min_value=df_copy['date'].min().date(), max_value=df_copy['date'].max().date(), value=df_copy['date'].min().date())
    end_date = st.date_input('End date', min_value=df_copy['date'].min().date(), max_value=df_copy['date'].max().date(), value=df_copy['date'].max().date())

    # Filter the data based on the date range
    filtered_df = df_copy[(df_copy['date'].dt.date >= start_date) & (df_copy['date'].dt.date <= end_date)]

    # Group by month and calculate mean values for each group
    # Ensure the date column is set as the index for grouping
    filtered_df.set_index('date', inplace=True)
    grouped_df = filtered_df.groupby(filtered_df.index.to_period('M')).agg({
        'mean_temp_normalized': 'mean',
        'global_radiation_normalized': 'mean'
    }).reset_index()

    # Convert 'date' back to datetime for plotting
    grouped_df['date'] = grouped_df['date'].dt.to_timestamp()

    # Melt the grouped DataFrame
    df_melt = grouped_df.melt(id_vars='date', value_vars=['mean_temp_normalized', 'global_radiation_normalized'])

    # Create the line plot using Plotly Express
    fig1 = px.line(df_melt, x='date', y='value', color='variable', title='Monthly Mean of Normalized Temperature and Global Radiation')

    # Display the plot in Streamlit
    st.write(fig1)

# --- ANALYSIS 
st.write("Note that temperature is highly correlated with global temperature. Then, there was a significantly increase number of global radiation specifically on May 2020. As well as slightly increase of temperature and global radiation trend starting from 00s. Hence, by simple visually analyzing, there indicates the climate changes because upward trend of temperature & global radiation. This finding can serve as basis assumption for further investigation, which can be validated through comprehensive statistical analysis.")
