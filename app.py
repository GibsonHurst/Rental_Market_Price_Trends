#!/usr/bin/env python
# coding: utf-8

# In[783]:


import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go


# In[784]:


metro = pd.read_csv("https://raw.githubusercontent.com/GibsonHurst/Rental_Market_Price_Trends/main/ZORI_all_homes_metro.csv")
cpi = pd.read_csv("https://raw.githubusercontent.com/GibsonHurst/Rent_Market_Price_Trends/main/CUSR0000SA0L2.csv")
income = pd.read_csv("https://raw.githubusercontent.com/GibsonHurst/Rent_Market_Price_Trends/main/lapi1123msa.csv")


# In[786]:


metro_prices = metro.copy() #duplicate date
metro_prices = metro_prices[metro_prices['SizeRank']<30] #pick top 30 cities
drop_list = ['RegionID', 'SizeRank', 'RegionType', 'StateName'] #drop not needed columns


# In[787]:


metro_recent = metro_prices[['MetroRegionName', '12/31/22', 'SizeRank']]


# In[788]:


metro_prices.drop(columns=drop_list, inplace=True) #drop not needed columns
metro_prices = metro_prices.transpose() #transpose the df


# In[789]:


new_columns = metro_prices.iloc[0] #store first row that has column names
metro_prices = metro_prices[1:] #remove current column labels
metro_prices.columns = new_columns #assign new column labels that used to be in the first row
metro_prices = metro_prices.reset_index() #move date from index to its own column
metro_prices.rename(columns={'index':'Date'}, inplace=True) #rename it to date


# In[790]:


metro_prices['Date'] = pd.to_datetime(metro_prices['Date'], format='%m/%d/%y') #dtype to datetime
usa_prices = metro_prices[['Date','United States']] #split of USA data for annual inflation calculation 
metro_prices = metro_prices[metro_prices['Date'] > '2019-12-31'] #filter since covid-19 hit
metro_prices.set_index('Date', inplace=True) #move date back to index temporaroly


# In[791]:


metro_changes = metro_prices.apply(lambda x: (x/x.iloc[0])-1, axis=0) #caclulate change since inital date
metro_changes = metro_changes.reset_index() #move date back to its own column


# In[792]:


cpi['DATE'] = pd.to_datetime(cpi['DATE'], format='%m/%d/%y')


# In[ ]:


usa_prices['Annual USA Rent Inflation'] = usa_prices['United States'].pct_change(periods=12)
usa_prices = usa_prices[usa_prices['Date'] > '2019-12-31']


# In[794]:


inflation_comp = pd.merge(cpi, usa_prices, left_on='DATE', right_on='Date', how='left')


# In[795]:


rent_vs_income = pd.merge(metro_recent, income, left_on='MetroRegionName', right_on='Location', how='left')


# In[796]:


rent_vs_income['Rent-to-Income Ratio'] = (rent_vs_income['12/31/22']*12)/rent_vs_income['2022 PCPI']


# In[797]:


rent_vs_income['SizeRank'] = 30 - rent_vs_income['SizeRank'] 


# In[799]:


import streamlit as st
import plotly.graph_objects as go
import pandas as pd

regions_to_plot = ['New York, NY', 'Los Angeles, CA',
                   'Chicago, IL', 'Dallas, TX', 'Houston, TX', 'Washington, DC',
                   'Philadelphia, PA', 'Miami, FL', 'Atlanta, GA', 'Boston, MA',
                   'Phoenix, AZ', 'San Francisco, CA', 'Riverside, CA', 'Detroit, MI',
                   'Seattle, WA', 'Minneapolis, MN', 'San Diego, CA', 'Tampa, FL',
                   'Denver, CO', 'Baltimore, MD', 'St. Louis, MO', 'Orlando, FL',
                   'Charlotte, NC', 'San Antonio, TX', 'Portland, OR', 'Sacramento, CA',
                   'Pittsburgh, PA', 'Cincinnati, OH', 'Austin, TX']

st.title('National Rental Market Trends Since The Pandemic')

st.header('Cumulative Rent Increase in Selected Metropolitan Area Compared to National Average')

selected_region = st.selectbox('Select a metro area to compare:', regions_to_plot)

fig = go.Figure()

fig.add_trace(
    go.Scatter(x=metro_changes['Date'],
               y=metro_changes['United States'],
               mode='lines',
               name='United States',
               line=dict(color='gray'))
)

fig.add_trace(
    go.Scatter(x=metro_changes['Date'],
               y=metro_changes[selected_region],
               mode='lines',
               name=selected_region,
               line=dict(color='red'))
)

fig.update_layout(
    #title=f'Rent Price Change Since 2020 in {selected_region} Compared To USA',
    yaxis_title='Percentage Change',
    yaxis=dict(tickformat=".0%"),
    plot_bgcolor='white',
    width=800,  
    height=600, 
    legend=dict(
        orientation="h",  # Horizontal orientation
        yanchor="top",
        y=1.04,  
        xanchor="left",
        x=-0.05 
    ),
    annotations=[
        dict(
            text="Source: Zillow Observed Rent Index | By: Gibson Hurst",
            showarrow=False,
            xref="paper",
            yref="paper",
            x=-0.05,
            y=-0.05,  
            yanchor='top',
            xanchor='left',
            font=dict(size=12, color="gray")
        )
    ],
    margin=dict(l=90, r=0, t=70, b=70) 
)

st.plotly_chart(fig, use_container_width=True)


# In[800]:


st.header('Annual Rent Inflation Compared to Annual Inflation (Shleter Excluded)')

fig2 = go.Figure()

fig2.add_trace(
    go.Scatter(
        x=inflation_comp['DATE'],
        y=inflation_comp['Annual Inflation (Shelter Excluded)'],
        mode='lines',
        name='Annual Inflation (Shelter Excluded)',
        line=dict(color='blue')
    )
)

fig2.add_trace(
    go.Scatter(
        x=inflation_comp['DATE'],
        y=inflation_comp['Annual USA Rent Inflation'],
        mode='lines',
        name='Annual USA Rent Inflation',
        line=dict(color='red')  
    )
)

fig2.update_layout(
    #title='National Annual Rent Inflation Compared to Annual Inflation (Shleter Excluded)',
    yaxis_title='Percentage Change',
    yaxis=dict(tickformat=".0%"),
    plot_bgcolor='white',
    width=800,  
    height=600,  
    legend=dict(
        orientation="h",  # Horizontal orientation
        yanchor="top",
        y=1.04,  
        xanchor="left",
        x=-0.05 
    ),
    annotations=[
        dict(
            text="Source: Zillow Observed Rent Index, Federal Reserve Economic Data | By: Gibson Hurst",
            showarrow=False,
            xref="paper",
            yref="paper",
            x=-0.05,
            y=-0.05,  
            yanchor='top',
            xanchor='left',
            font=dict(size=12, color="gray")
        )
    ],
    margin=dict(l=90, r=0, t=70, b=70) 
)

st.plotly_chart(fig2, use_container_width=True)


# In[805]:


st.header('Rent-to-Income Ratio by Metropolitan Area')

sort_by = st.selectbox('Sort By', ['Population', 'Rent-to-Income Ratio'])

if sort_by == 'Population':
    sort_by_column = 'SizeRank'
else:
    sort_by_column = 'Rent-to-Income Ratio'

rent_vs_income_sorted = rent_vs_income.sort_values(by=sort_by_column, ascending=False)

fig3 = go.Figure()

fig3.add_trace(
    go.Bar(
        x=rent_vs_income_sorted['MetroRegionName'],
        y=rent_vs_income_sorted['Rent-to-Income Ratio'],
        orientation='v'
    )
)

fig3.update_layout(
    #title='Rent to Income Per Capita Ratio',
    yaxis_title='Percentage',
    yaxis=dict(tickformat=".0%"),
    plot_bgcolor='white',
    width=800,  
    height=600,  
    annotations=[
        dict(
            text="Source: Zillow Observed Rent Index, Bureau of Economic Analysis | By: Gibson Hurst",
            showarrow=False,
            xref="paper",
            yref="paper",
            x=-0.05,
            y=-0.32,  
            yanchor='top',
            xanchor='left',
            font=dict(size=12, color="gray")
        )
    ],
    margin=dict(l=90, r=90, t=70, b=150) 
)

st.plotly_chart(fig3)


# In[ ]:




