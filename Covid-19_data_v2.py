#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 10:33:40 2020

@author: nathanmasters
"""

import pandas as pd
import numpy as np
import calendar
import datetime

import time
from scipy import interpolate
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from matplotlib.text import OffsetFrom
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Bokeh

from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.layouts import column, gridplot


#Covid_cases_data = pd.read_excel("/Users/nathanmasters/Documents/Covid-19_data/Historic_COVID-19_Dashboard_Data.xlsx", sheet_name="UK Cases", header=8)
#Covid_deaths_data = pd.read_excel("/Users/nathanmasters/Documents/Covid-19_data/Historic_COVID-19_Dashboard_Data.xlsx", sheet_name="UK Deaths", header=7)

#World_data = pd.read_csv("world_data.csv", header=0, parse_dates=[[3,2,1]])
# World_data = pd.read_csv("world_data.csv", header=0)
World_data = pd.read_csv("https://opendata.ecdc.europa.eu/covid19/casedistribution/csv", header=0)

World_data.to_csv("latest_world_data.csv",index=False)
World_data['dateRep'] = pd.to_datetime(World_data[["year", "month", "day"]])



Country_groups = World_data.groupby('countriesAndTerritories')

Cumulative_deaths = Country_groups["deaths"].sum()

# plt.bar(Cumulative_deaths.index[Cumulative_deaths > 10000],Cumulative_deaths[Cumulative_deaths > 10000])


countries = ["United_Kingdom",
             "Switzerland",
             "United_States_of_America",
             "Brazil",
             "Sweden"]

date_form = DateFormatter("%m-%d")

def death_plot(country):

    
    fig=plt.figure(figsize=(10,6))
    ax = fig.add_subplot(111)
    
    for c in countries:
        latest_death = int(Country_groups.get_group(c)["deaths"].rolling(7).mean().shift(-7).iloc[0])
        
        ax.plot(Country_groups.get_group(c)["dateRep"],
                Country_groups.get_group(c)["deaths"].rolling(7).mean().shift(-7),
                alpha= 0.4,
                label=(c+" ({:,})").format(int(Country_groups.get_group(c)["deaths"].rolling(7).mean().shift(-7).iloc[0])));
        if c == country:
            ax.plot(Country_groups.get_group(c)["dateRep"],
                Country_groups.get_group(c)["deaths"].rolling(7).mean().shift(-7),
                alpha= 1)
            ax.annotate('Recent Deaths: {:,}'.format(latest_death),
                        xy=((datetime.date.today()- datetime.timedelta(days=5)), latest_death), xycoords='data',
                        xytext=(-1, 0), textcoords='offset points',
                        horizontalalignment='right', verticalalignment='bottom')
            
            
        ax.set_xticklabels(Country_groups.get_group(c)["dateRep"], rotation=45);
        
    ax.set_yscale('log')
    ax.legend(loc='upper left', frameon=False)
    ax.set(ylabel="Deaths",
            # ylim = [1, 50000],
            # yscale = "log",
            xlabel = "Date",
            xlim = [datetime.date(2020, 3, 1), datetime.date.today()],
            title = "Daily Deaths (7-day rolling average)",
            )
    ax.xaxis.set_major_formatter(date_form)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))



