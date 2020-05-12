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

def get_country_data(country):
    country_data = World_data[World_data["countriesAndTerritories"]==country]
    country_data.index = (range(len(country_data)))
    country_data.index = country_data.index[::-1]
    country_data['dateRep'] = pd.to_datetime(country_data[["year", "month", "day"]])
    return country_data

Swiss_data = get_country_data("Switzerland").sort_index()
UK_data = get_country_data("United_Kingdom").sort_index()
US_data = get_country_data("United_States_of_America").sort_index()
Sweden_data = get_country_data("Sweden").sort_index()
Brazil_data = get_country_data("Brazil").sort_index()


def create_cumulative_data(country):

    country["cum_cases"] = None
    country.cum_cases.iloc[0] = country.cases.iloc[0]
    country["cum_deaths"] = None
    country.cum_deaths.iloc[0] = country.deaths.iloc[0]

    for i in range(1,len(country)):
        country.cum_cases.iloc[i] = country.cases.iloc[i] + country.cum_cases.iloc[i-1]
        country.cum_deaths.iloc[i] = country.deaths.iloc[i] + country.cum_deaths.iloc[i-1]
    # country.cum_cases = country.cum_cases.rolling(moving_average, center=True).mean()
    # country.cum_deaths = country.cum_deaths.rolling(moving_average, center=True).mean()

    return country

# moving_average = 5

UK_data = create_cumulative_data(UK_data)
Swiss_data = create_cumulative_data(Swiss_data)
US_data = create_cumulative_data(US_data)
Sweden_data = create_cumulative_data(Sweden_data)
Brazil_data = create_cumulative_data(Brazil_data)


def create_smooth_data(country, window):
    country["smooth_cases"] = country.cases.rolling(window).mean()
    country["smooth_deaths"] = country.deaths.rolling(window).mean()
    return country

UK_data = create_smooth_data(UK_data, 7)
Swiss_data = create_smooth_data(Swiss_data, 7)
US_data = create_smooth_data(US_data, 7)
Sweden_data = create_smooth_data(Sweden_data, 7)
Brazil_data = create_smooth_data(Brazil_data, 7)

def create_ordinal_data(country):
    country["date_ordinal"] = country['dateRep'].apply(lambda x: x.toordinal())
    return country

UK_data = create_ordinal_data(UK_data)


def create_spline_data(country):
    tck_cum_cases = interpolate.splrep(country.date_ordinal, country.cum_cases)
    tck_cum_deaths = interpolate.splrep(country.date_ordinal, country.cum_deaths)
    tck_cases = interpolate.splrep(country.date_ordinal, country.cases)
    tck_deaths = interpolate.splrep(country.date_ordinal, country.deaths)
    country["spline_cum_cases"] = interpolate.splev(country.date_ordinal, tck_cum_cases, der=0)
    country["spline_cum_deaths"] = interpolate.splev(country.date_ordinal, tck_cum_deaths, der=0)
    country["spline_cases"] = interpolate.splev(country.date_ordinal, tck_cases, der=1)
    country["spline_deaths"] = interpolate.splev(country.date_ordinal, tck_deaths, der=1)
    return country

UK_data = create_spline_data(UK_data) 

country_data = UK_data
n=28

# def last_n_day_regression(country_data, n):

#     model = LinearRegression(fit_intercept=True)
    
#     country_data["datetime"] = pd.to_datetime(country_data["dateRep"])
#     country_data["datetime"] = country_data["datetime"].map(datetime.datetime.toordinal)

#     country_data["log_case"] = np.log(country_data["datetime"])
    
#     # linear_dates = np.array((country_data.datetime[-(n+1):-1])))
#     linear_dates = np.array((country_data.log_case[-(n+1):-1]))
#     last_28_case_values = np.array(country_data.cum_cases[-(n+1):-1])
    
#     # numdays = 100 
#     # base = datetime.datetime.today()
#     # prediction_dates = np.array([base - datetime.timedelta(days=x) for x in range(numdays)])
    
#     datelist = pd.date_range(end = datetime.date.today(), periods=len(country_data))
#     datelist = datelist.map(datetime.datetime.toordinal)
    
#     datelist_log = np.log(datelist)
    
    # linear_fit = model.fit(linear_dates[:, np.newaxis], last_28_case_values)
    # linear_plot = linear_fit.predict(datelist_log[:, np.newaxis])
    
    # dt=[]
    # for i in range(len(datelist)):
    #     dt.append(datetime.datetime.fromordinal(datelist[i]))
    
    # # regression_array = pd.Series(country_data.dateRep[-29:-1])
    # regression_array = pd.concat([pd.Series(dt), 
    #                               pd.Series(linear_plot)],
    #                               axis=1)
    # regression_array.columns = ["Date", "Fit"]
    
    # return regression_array

# UK_regression_7days = last_n_day_regression(UK_data, 7)
# UK_regression_28days = last_n_day_regression(UK_data, 28)


# regression_points["dates"] = country_data.dateRep[-29:-1]
# regression_points["regres_fit"] = linear_plot

# plt.plot(UK_data.dateRep[-29:-1], linear_plot, label="last 28 days")
# plt.plot(UK_regression.Date, UK_regression.Fit, label="UK last 28 days")

latest_death_data = np.array([
    UK_data["cum_deaths"].iloc[-1],
    Swiss_data["cum_deaths"].iloc[-1],
    US_data["cum_deaths"].iloc[-1],
    Sweden_data["cum_deaths"].iloc[-1],
    Brazil_data["cum_deaths"].iloc[-1]
    ])

latest_cases_data = np.array([
    UK_data["cum_cases"].iloc[-1],
    Swiss_data["cum_cases"].iloc[-1],
    US_data["cum_cases"].iloc[-1],
    Sweden_data["cum_cases"].iloc[-1],
    Brazil_data["cum_cases"].iloc[-1]
    ])

latest_week_day_cases_data = pd.DataFrame({
    "Date" : UK_data["dateRep"].iloc[-8:-1],
    "UK_data" : UK_data["cum_cases"].iloc[-8:-1],
    "Swiss_data" : Swiss_data["cum_cases"].iloc[-8:-1],
    "US_data" : US_data["cum_cases"].iloc[-8:-1],
    "Sweden_data" : Sweden_data["cum_cases"].iloc[-8:-1],
    "Brazil_data" : Brazil_data["cum_cases"].iloc[-8:-1]
    }).reset_index().drop(["index"], axis=1)

latest_week_day_deaths_data = pd.DataFrame({
    "Date" : UK_data["dateRep"].iloc[-8:-1],
    "UK_data" : UK_data["cum_deaths"].iloc[-8:-1],
    "Swiss_data" : Swiss_data["cum_deaths"].iloc[-8:-1],
    "US_data" : US_data["cum_deaths"].iloc[-8:-1],
    "Sweden_data" : Sweden_data["cum_deaths"].iloc[-8:-1],
    "Brazil_data" : Brazil_data["cum_deaths"].iloc[-8:-1]
    }).reset_index().drop(["index"], axis=1)

    
latest_week_day_cases_data["date_ordinal"] = latest_week_day_cases_data['Date'].apply(lambda x: x.toordinal())
latest_week_day_deaths_data["date_ordinal"] = latest_week_day_deaths_data['Date'].apply(lambda x: x.toordinal())

latest_week_day_cases_data["UK_change"] = 0
latest_week_day_cases_data["Swiss_change"] = 0
latest_week_day_cases_data["US_change"] = 0
latest_week_day_cases_data["Sweden_change"] = 0
latest_week_day_cases_data["Brazil_change"] = 0

for i in range(len(latest_week_day_cases_data)):
    if i < 6:
        latest_week_day_cases_data["UK_change"].iloc[i+1] = 100*(latest_week_day_cases_data["UK_data"].iloc[i+1] - latest_week_day_cases_data["UK_data"].iloc[i])/latest_week_day_cases_data["UK_data"].iloc[i]
        latest_week_day_cases_data["Swiss_change"].iloc[i+1] = 100*(latest_week_day_cases_data["Swiss_data"].iloc[i+1] - latest_week_day_cases_data["Swiss_data"].iloc[i])/latest_week_day_cases_data["Swiss_data"].iloc[i]
        latest_week_day_cases_data["US_change"].iloc[i+1] = 100*(latest_week_day_cases_data["US_data"].iloc[i+1] - latest_week_day_cases_data["US_data"].iloc[i])/latest_week_day_cases_data["US_data"].iloc[i]
        latest_week_day_cases_data["Sweden_change"].iloc[i+1] = 100*(latest_week_day_cases_data["Sweden_data"].iloc[i+1] - latest_week_day_cases_data["Sweden_data"].iloc[i])/latest_week_day_cases_data["Sweden_data"].iloc[i]
        latest_week_day_cases_data["Brazil_change"].iloc[i+1] = 100*(latest_week_day_cases_data["Brazil_data"].iloc[i+1] - latest_week_day_cases_data["Brazil_data"].iloc[i])/latest_week_day_cases_data["Brazil_data"].iloc[i]

latest_week_day_deaths_data["UK_change"] = 0
latest_week_day_deaths_data["Swiss_change"] = 0
latest_week_day_deaths_data["US_change"] = 0
latest_week_day_deaths_data["Sweden_change"] = 0
latest_week_day_deaths_data["Brazil_change"] = 0

for i in range(len(latest_week_day_cases_data)):
    if i < 6:
        latest_week_day_deaths_data["UK_change"].iloc[i+1] = 100*(latest_week_day_deaths_data["UK_data"].iloc[i+1] - latest_week_day_deaths_data["UK_data"].iloc[i])/latest_week_day_deaths_data["UK_data"].iloc[i]
        latest_week_day_deaths_data["Swiss_change"].iloc[i+1] = 100*(latest_week_day_deaths_data["Swiss_data"].iloc[i+1] - latest_week_day_deaths_data["Swiss_data"].iloc[i])/latest_week_day_deaths_data["Swiss_data"].iloc[i]
        latest_week_day_deaths_data["US_change"].iloc[i+1] = 100*(latest_week_day_deaths_data["US_data"].iloc[i+1] - latest_week_day_deaths_data["US_data"].iloc[i])/latest_week_day_deaths_data["US_data"].iloc[i]
        latest_week_day_deaths_data["Sweden_change"].iloc[i+1] = 100*(latest_week_day_deaths_data["Sweden_data"].iloc[i+1] - latest_week_day_deaths_data["Sweden_data"].iloc[i])/latest_week_day_deaths_data["Sweden_data"].iloc[i]
        latest_week_day_deaths_data["Brazil_change"].iloc[i+1] = 100*(latest_week_day_deaths_data["Brazil_data"].iloc[i+1] - latest_week_day_deaths_data["Brazil_data"].iloc[i])/latest_week_day_deaths_data["Brazil_data"].iloc[i]


# UK_change_cases = np.mean(latest_week_day_cases_data.UK_change[1:-1])
# UK_change_cases = (latest_week_day_cases_data.UK_data.iloc[-1]-latest_week_day_cases_data.UK_data.iloc[0])/latest_week_day_cases_data.UK_data.iloc[0]
UK_change_cases = (UK_data.smooth_cases.iloc[-1]-UK_data.smooth_cases.iloc[-8])/UK_data.smooth_cases.iloc[-8]
Swiss_change_cases = (Swiss_data.smooth_cases.iloc[-1]-Swiss_data.smooth_cases.iloc[-8])/Swiss_data.smooth_cases.iloc[-8]
US_change_cases = (US_data.smooth_cases.iloc[-1]-US_data.smooth_cases.iloc[-8])/US_data.smooth_cases.iloc[-8]
Sweden_change_cases = (Sweden_data.smooth_cases.iloc[-1]-Sweden_data.smooth_cases.iloc[-8])/Sweden_data.smooth_cases.iloc[-8]
Brazil_change_cases = (Brazil_data.smooth_cases.iloc[-1]-Brazil_data.smooth_cases.iloc[-8])/Brazil_data.smooth_cases.iloc[-8]


# Swiss_change_cases = (latest_week_day_cases_data.Swiss_data.iloc[-1]-latest_week_day_cases_data.Swiss_data.iloc[0])/latest_week_day_cases_data.Swiss_data.iloc[0]
# US_change_cases = (latest_week_day_cases_data.US_data.iloc[-1]-latest_week_day_cases_data.US_data.iloc[0])/latest_week_day_cases_data.US_data.iloc[0]


# UK_change_deaths = (latest_week_day_deaths_data.UK_data.iloc[-1]-latest_week_day_deaths_data.UK_data.iloc[0])/latest_week_day_deaths_data.UK_data.iloc[0]
UK_change_deaths = (UK_data.smooth_deaths.iloc[-1]-UK_data.smooth_deaths.iloc[-8])/UK_data.smooth_deaths.iloc[-8]
Swiss_change_deaths = (Swiss_data.smooth_deaths.iloc[-1]-Swiss_data.smooth_deaths.iloc[-8])/Swiss_data.smooth_deaths.iloc[-8]
US_change_deaths = (US_data.smooth_deaths.iloc[-1]-US_data.smooth_deaths.iloc[-8])/US_data.smooth_deaths.iloc[-8]
Sweden_change_deaths = (Sweden_data.smooth_deaths.iloc[-1]-Sweden_data.smooth_deaths.iloc[-8])/Sweden_data.smooth_deaths.iloc[-8]
Brazil_change_deaths = (Brazil_data.smooth_deaths.iloc[-1]-Brazil_data.smooth_deaths.iloc[-8])/Brazil_data.smooth_deaths.iloc[-8]


# Swiss_change_deaths = (latest_week_day_deaths_data.Swiss_data.iloc[-1]-latest_week_day_deaths_data.Swiss_data.iloc[0])/latest_week_day_deaths_data.Swiss_data.iloc[0]
# US_change_deaths = (latest_week_day_deaths_data.US_data.iloc[-1]-latest_week_day_deaths_data.US_data.iloc[0])/latest_week_day_deaths_data.US_data.iloc[0]



def Fits(latest_data_cases, latest_data_deaths):
    index = ["UK_cases_fit", "UK_deaths_fit", "Swiss_cases_fit", "Swiss_deaths_fit", "US_cases_fit", "US_deaths_fit", "Sweden_cases_fit", "Sweden_deaths_fit", "Brazil_cases_fit", "Brazil_deaths_fit"]
    Fits = pd.DataFrame([
        np.polyfit(latest_data_cases["date_ordinal"].astype("float"), latest_data_cases["UK_data"].astype("float"), 1),
        np.polyfit(latest_data_deaths["date_ordinal"].astype("float"), latest_data_deaths["UK_data"].astype("float"), 1),
        np.polyfit(latest_data_cases["date_ordinal"].astype("float"), latest_data_cases["Swiss_data"].astype("float"), 1),
        np.polyfit(latest_data_deaths["date_ordinal"].astype("float"), latest_data_deaths["Swiss_data"].astype("float"), 1),
        np.polyfit(latest_data_cases["date_ordinal"].astype("float"), latest_data_cases["US_data"].astype("float"), 1),
        np.polyfit(latest_data_deaths["date_ordinal"].astype("float"), latest_data_deaths["US_data"].astype("float"), 1),
        np.polyfit(latest_data_cases["date_ordinal"].astype("float"), latest_data_cases["Sweden_data"].astype("float"), 1),
        np.polyfit(latest_data_deaths["date_ordinal"].astype("float"), latest_data_deaths["Sweden_data"].astype("float"), 1),
        np.polyfit(latest_data_cases["date_ordinal"].astype("float"), latest_data_cases["Brazil_data"].astype("float"), 1),
        np.polyfit(latest_data_deaths["date_ordinal"].astype("float"), latest_data_deaths["Brazil_data"].astype("float"), 1)

        ], index=index)
    return Fits

Latest_fit = Fits(latest_week_day_cases_data, latest_week_day_deaths_data)

# last_thirty_days = pd.DataFrame(pd.date_range(end = datetime.date.today(), periods=30), columns=["dates"])
# last_thirty_days["dates"] = last_thirty_days["dates"].apply(lambda x: x.toordinal())
# last_thirty_days["UK_cases_regression"] = last_thirty_days["dates"]*Fits[0].loc["UK_cases_fit"] + Fits[1].loc["UK_cases_fit"]
# last_thirty_days["UK_deaths_regression"] = last_thirty_days["dates"]*Fits[0].loc["UK_deaths_fit"] + Fits[1].loc["UK_deaths_fit"]
# last_thirty_days["Swiss_cases_regression"] = last_thirty_days["dates"]*Fits[0].loc["Swiss_cases_fit"] + Fits[1].loc["Swiss_cases_fit"]
# last_thirty_days["Swiss_deaths_regression"] = last_thirty_days["dates"]*Fits[0].loc["Swiss_deaths_fit"] + Fits[1].loc["Swiss_deaths_fit"]
# last_thirty_days["US_cases_regression"] = last_thirty_days["dates"]*Fits[0].loc["US_cases_fit"] + Fits[1].loc["US_cases_fit"]
# last_thirty_days["US_deaths_regression"] = last_thirty_days["dates"]*Fits[0].loc["US_deaths_fit"] + Fits[1].loc["US_deaths_fit"]


# test_x =  pd.DataFrame(pd.date_range(end = datetime.date.today(), periods=30), columns=["date"])
# test_x["x"] = test_x["date"].apply(lambda x: x.toordinal())

# for x in test_x:
#     test_x["days"] = -(test_x["x"].iloc[0]-test_x["x"])

# test_x["y"] = 2*np.exp(test_x["days"].astype("float"))




def plot_figure(month, day, plot_number):
    """ 
    Function to show plot deaths and cases from specified start date. 
    First argument: month
    Second argument: day
    """
    if plot_number==1:    

        output_file('/Users/nathanmasters/Documents/GitHub/nathan-masters.github.io/assets/img/Bokeh/UK-CH_corona.html')
        
        legend_alpha=0.2
        
        p1 = figure(title = "UK Cumulative Cases/Deaths", 
                   plot_height=350, 
                   plot_width=500,
                   y_axis_type="log", 
                   x_axis_type='datetime', 
                   x_range = (datetime.date(2020, month, day), datetime.date.today()),
                   sizing_mode='scale_width', 
                   tools=["pan,reset,wheel_zoom"])
    
        p1.xaxis.axis_label = 'Date'
        p1.yaxis.axis_label = 'Cumulative Cases/Deaths'
        p1.line(UK_data["dateRep"], UK_data["cum_cases"]+1, line_color="tomato", legend_label="Cases ({:,})".format(UK_data["cum_cases"].iloc[-1]))
        p1.line(UK_data["dateRep"], UK_data["cum_deaths"]+1, line_color="blue", legend_label="Deaths ({:,})".format(UK_data["cum_deaths"].iloc[-1]))
        p1.legend.location = "top_left"
        p1.legend.background_fill_alpha = legend_alpha
        
        p2 = figure(title = "UK Daily (7-day moving average) Today: {:,}".format(UK_data["cases"].iloc[-1]), 
                   plot_height=350, 
                   plot_width=500,
                   x_axis_type='datetime', 
                   x_range = (datetime.date(2020, month, day), datetime.date.today()),
                   sizing_mode='scale_width', 
                   tools=["pan,reset,wheel_zoom"])
    
        p2.xaxis.axis_label = 'Date'
        p2.yaxis.axis_label = 'Daily Cases/Deaths'
        p2.line(UK_data["dateRep"], UK_data["smooth_cases"]+1, line_color="tomato", legend_label="Cases ({:,})".format(int(UK_data["smooth_cases"].iloc[-1])))
        p2.line(UK_data["dateRep"], UK_data["smooth_deaths"]+1, line_color="blue", legend_label="Deaths ({:,})".format(int(UK_data["smooth_deaths"].iloc[-1])))
        p2.legend.location = "top_left"
        p2.legend.background_fill_alpha = legend_alpha
        
        p3 = figure(title = "Swiss Cumulative Cases/Deaths", 
                   plot_height=350, 
                   plot_width=500,
                   y_axis_type="log", 
                   x_axis_type='datetime', 
                   x_range = (datetime.date(2020, month, day), datetime.date.today()),
                   sizing_mode='scale_width', 
                   tools=["pan,reset,wheel_zoom"])
    
        p3.xaxis.axis_label = 'Date'
        p3.yaxis.axis_label = 'Cumulative Cases/Deaths'
        p3.line(Swiss_data["dateRep"], Swiss_data["cum_cases"]+1, line_color="tomato", legend_label="Cases ({:,})".format(Swiss_data["cum_cases"].iloc[-1]))
        p3.line(Swiss_data["dateRep"], Swiss_data["cum_deaths"]+1, line_color="blue", legend_label="Deaths ({:,})".format(Swiss_data["cum_deaths"].iloc[-1]))
        p3.legend.location = "top_left"
        p3.legend.background_fill_alpha = legend_alpha
        
        p4 = figure(title = "Swiss Daily (7-day moving average) Today: {:,}".format(Swiss_data["cases"].iloc[-1]), 
                   plot_height=350, 
                   plot_width=500,
                   x_axis_type='datetime', 
                   x_range = (datetime.date(2020, month, day), datetime.date.today()),
                   sizing_mode='scale_width', 
                   tools=["pan,reset,wheel_zoom"])
    
        p4.xaxis.axis_label = 'Date'
        p4.yaxis.axis_label = 'Daily Cases/Deaths'
        p4.line(Swiss_data["dateRep"], Swiss_data["smooth_cases"]+1, line_color="tomato", legend_label="Cases ({:,})".format(int(Swiss_data["smooth_cases"].iloc[-1])))
        p4.line(Swiss_data["dateRep"], Swiss_data["smooth_deaths"]+1, line_color="blue", legend_label="Deaths ({:,})".format(int(Swiss_data["smooth_deaths"].iloc[-1])))
        p4.legend.location = "top_left"
        p4.legend.background_fill_alpha = legend_alpha
        
        grid = gridplot([p1,p3,p2,p4], ncols=2, sizing_mode="scale_width")
    
        
        show(grid)
    
    if plot_number==2:
        output_file('/Users/nathanmasters/Documents/GitHub/nathan-masters.github.io/assets/img/Bokeh/corona-comparisons.html')
        legend_alpha=0.2
    
        
        TOOLTIPS = [
            ("Deaths", "$y{,}")
            ]

        
        p_comp = figure(title = "Cumulative Death Comparisons", 
                   plot_height=350, 
                   plot_width=500,
                   y_axis_type="log", 
                   x_axis_type='datetime', 
                   x_range = (datetime.date(2020, month, day), datetime.date.today()),
                   sizing_mode='scale_width', 
                   tools=["hover,pan,reset,wheel_zoom"],
                   tooltips = TOOLTIPS)
        
        p_comp.xaxis.axis_label = 'Date'
        p_comp.yaxis.axis_label = 'Cumulative Deaths'
        p_comp.line(UK_data["dateRep"], UK_data["cum_deaths"]+1, line_color="blue", legend_label="UK ({:,})".format(UK_data["cum_deaths"].iloc[-1]))
        p_comp.line(Swiss_data["dateRep"], Swiss_data["cum_deaths"]+1, line_color="red", legend_label="CH ({:,})".format(Swiss_data["cum_deaths"].iloc[-1]))
        p_comp.line(US_data["dateRep"], US_data["cum_deaths"]+1, line_color="green", legend_label="US ({:,})".format(US_data["cum_deaths"].iloc[-1]))
        p_comp.line(Sweden_data["dateRep"], Sweden_data["cum_deaths"]+1, line_color="orange", legend_label="SW ({:,})".format(Sweden_data["cum_deaths"].iloc[-1]))
        p_comp.line(Brazil_data["dateRep"], Brazil_data["cum_deaths"]+1, line_color="purple", legend_label="BR ({:,})".format(Brazil_data["cum_deaths"].iloc[-1]))
        p_comp.legend.location = "top_left"
        p_comp.legend.background_fill_alpha = legend_alpha
        
        show(p_comp)
        
        
    
    if plot_number==3:
        
        countries = np.array([
            "UK: ",
            "CH: ",
            "US: ",
            "SW: ",
            "BR: "
            ])
        
        country_number = np.array(list(range(5)))
        
        fig=plt.figure(figsize=(25,10))
        
        ax1 = fig.add_subplot(251)
        ax2 = fig.add_subplot(252)
        ax3 = fig.add_subplot(253)
        ax4 = fig.add_subplot(254)
        ax5 = fig.add_subplot(255)
        
        
        ax1_2 = fig.add_subplot(256)
        ax2_2 = fig.add_subplot(257)
        ax3_2 = fig.add_subplot(258)
        ax4_2 = fig.add_subplot(259)
        ax5_2 = fig.add_subplot(2,5,10)
        
        ax1.plot(UK_data["dateRep"], UK_data["cum_cases"]+1, label="UK Cases")
        ax1.plot(UK_data["dateRep"], UK_data["cum_deaths"]+1, label="UK Deaths")
        # ax1.plot(UK_data["dateRep"], UK_data["spline_cum_cases"], label="UK Cases Spline")
        
        # ax1_2 = ax1.twinx() 
        # ax1_2.plot(last_thirty_days[0], last_thirty_days["UK_cases_regression"], label="Last 5 Days Trend")
        
        ax2.plot(Swiss_data["dateRep"], Swiss_data["cum_cases"]+1, label="Swiss Cases")
        ax2.plot(Swiss_data["dateRep"], Swiss_data["cum_deaths"]+1, label="Swiss Deaths")
        
        ax3.plot(US_data["dateRep"], US_data["cum_cases"]+1, label="US Cases")
        ax3.plot(US_data["dateRep"], US_data["cum_deaths"]+1, label="US Deaths")
        
        ax4.plot(Sweden_data["dateRep"], Sweden_data["cum_cases"]+1, label="Sweden Cases")
        ax4.plot(Sweden_data["dateRep"], Sweden_data["cum_deaths"]+1, label="Sweden Deaths")
    
        ax5.plot(Brazil_data["dateRep"], Brazil_data["cum_cases"]+1, label="Brazil Cases")
        ax5.plot(Brazil_data["dateRep"], Brazil_data["cum_deaths"]+1, label="Brazil Deaths")
    
        
        
        ax1_2.plot(UK_data["dateRep"], UK_data["smooth_cases"]+1, label="UK Cases")
        ax1_2.plot(UK_data["dateRep"], UK_data["smooth_deaths"]+1, label="UK Deaths")
        # ax1_2.plot(UK_data["dateRep"], UK_data["spline_cases"]+1, label="UK Spline Cases")
        
        ax2_2.plot(Swiss_data["dateRep"], Swiss_data["smooth_cases"]+1, label="Swiss Cases")
        ax2_2.plot(Swiss_data["dateRep"], Swiss_data["smooth_deaths"]+1, label="Swiss Deaths")
        
        ax3_2.plot(US_data["dateRep"], US_data["smooth_cases"]+1, label="US Cases")
        ax3_2.plot(US_data["dateRep"], US_data["smooth_deaths"]+1, label="US Deaths")
        
        ax4_2.plot(Sweden_data["dateRep"], Sweden_data["smooth_cases"]+1, label="Sweden Cases")
        ax4_2.plot(Sweden_data["dateRep"], Sweden_data["smooth_deaths"]+1, label="Sweden Deaths")
    
        ax5_2.plot(Brazil_data["dateRep"], Brazil_data["smooth_cases"]+1, label="Brazil Cases")
        ax5_2.plot(Brazil_data["dateRep"], Brazil_data["smooth_deaths"]+1, label="Brazil Deaths")
        
        
        # ax.plot(UK_regression_7days["Date"], UK_regression_7days.Fit, label="UK 7 day trend")
        # ax.plot(UK_regression_28days["Date"], UK_regression_28days.Fit, label="UK 28 day trend")
        
        # latest_data = np.array([
        #     UK_data["cum_deaths"].iloc[-1],
        #     Swiss_data["cum_deaths"].iloc[-1],
        #     US_data["cum_deaths"].iloc[-1],
        #     ])
        # print(latest_data)
        
        ax1.set_xticklabels(UK_data["dateRep"], rotation=45)
        ax2.set_xticklabels(UK_data["dateRep"], rotation=45)
        ax3.set_xticklabels(UK_data["dateRep"], rotation=45)
        ax4.set_xticklabels(UK_data["dateRep"], rotation=45)
        ax5.set_xticklabels(UK_data["dateRep"], rotation=45)
        
        
        ax1_2.set_xticklabels(UK_data["dateRep"], rotation=45)
        ax2_2.set_xticklabels(UK_data["dateRep"], rotation=45)
        ax3_2.set_xticklabels(UK_data["dateRep"], rotation=45)
        ax4_2.set_xticklabels(UK_data["dateRep"], rotation=45)
        ax5_2.set_xticklabels(UK_data["dateRep"], rotation=45)
        
        ax1.set(
            ylabel="Cumulative Cases/Deaths",
            ylim = [1, 5000000],
            yscale = "log",
            xlabel = "Date",
            xlim = [datetime.date(2020, month, day), datetime.date.today()],
            title = "UK Data",
            )
        ax1.legend(loc="upper left")
        
        # ax1_2.set(
        #     ylabel="Cumulative Cases/Deaths",
        #     ylim = [1, 150000],
        #     # yscale = "log",
        #     xlabel = "Date",
        #     xlim = [datetime.date(2020, month, day), datetime.date.today()],
        #     # title = "UK Data",
        #     )
        # ax1.legend(loc="upper left")
        
        ax2.set(
        ylabel="Cumulative Cases/Deaths",
        ylim = [1, 5000000],
        yscale = "log",
        xlabel = "Date",
        xlim = [datetime.date(2020, month, day), datetime.date.today()],
        title = "Swiss Data",
            )
        ax2.legend(loc="upper left")
        
        ax3.set(
        ylabel="Cumulative Cases/Deaths",
        ylim = [1, 5000000],
        yscale = "log",
        xlabel = "Date",
        xlim = [datetime.date(2020, month, day), datetime.date.today()],
        title = "US Data",
            )
        ax3.legend(loc="upper left")
     
        ax4.set(
        ylabel="Cumulative Cases/Deaths",
        ylim = [1, 5000000],
        yscale = "log",
        xlabel = "Date",
        xlim = [datetime.date(2020, month, day), datetime.date.today()],
        title = "Sweden Data",
            )
        ax4.legend(loc="upper left")
      
        ax5.set(
        ylabel="Cumulative Cases/Deaths",
        ylim = [1, 5000000],
        yscale = "log",
        xlabel = "Date",
        xlim = [datetime.date(2020, month, day), datetime.date.today()],
        title = "Brazil Data",
            )
        ax5.legend(loc="upper left")
        
        ax1_2.set(
            ylabel="Cases/Deaths per day",
            # ylim = [1, 10000],
            # yscale = "log",
            xlabel = "Date",
            xlim = [datetime.date(2020, month, day), datetime.date.today()],
            title = "UK Data",
            )
        ax1_2.legend(loc="upper left")
        
        ax2_2.set(
            ylabel="Cases/Deaths per day",
            # ylim = [1, 10000],
            # yscale = "log",
            xlabel = "Date",
            xlim = [datetime.date(2020, month, day), datetime.date.today()],
            title = "Swiss Data",
            )
        ax2_2.legend(loc="upper left")
        
        ax3_2.set(
            ylabel="Cases/Deaths per day",
            # ylim = [1, 50000],
            # yscale = "log",
            xlabel = "Date",
            xlim = [datetime.date(2020, month, day), datetime.date.today()],
            title = "US Data",
            )
        ax3_2.legend(loc="upper left")
        
        ax4_2.set(
            ylabel="Cases/Deaths per day",
            # ylim = [1, 50000],
            # yscale = "log",
            xlabel = "Date",
            xlim = [datetime.date(2020, month, day), datetime.date.today()],
            title = "Sweden Data",
            )
        ax4_2.legend(loc="upper left")
        
        ax5_2.set(
            ylabel="Cases/Deaths per day",
            # ylim = [1, 50000],
            # yscale = "log",
            xlabel = "Date",
            xlim = [datetime.date(2020, month, day), datetime.date.today()],
            title = "Brazil Data",
            )
        ax5_2.legend(loc="upper left")
        
    
        date_form = DateFormatter("%m-%d")
        ax1.xaxis.set_major_formatter(date_form)
        ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        ax2.xaxis.set_major_formatter(date_form)
        ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        ax3.xaxis.set_major_formatter(date_form)
        ax3.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        ax4.xaxis.set_major_formatter(date_form)
        ax4.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        ax5.xaxis.set_major_formatter(date_form)
        ax5.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        
        ax1_2.xaxis.set_major_formatter(date_form)
        ax1_2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        ax2_2.xaxis.set_major_formatter(date_form)
        ax2_2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        ax3_2.xaxis.set_major_formatter(date_form)
        ax3_2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        ax4_2.xaxis.set_major_formatter(date_form)
        ax4_2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        ax5_2.xaxis.set_major_formatter(date_form)
        ax5_2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        
        for i, j, k in zip(latest_death_data, latest_cases_data, country_number):
            if k == 0:
                ax1.annotate('%.0f' %i,
                    xy=((datetime.date.today()- datetime.timedelta(days=1)), i), xycoords='data',
                    xytext=(-1, 0), textcoords='offset points',
                    # arrowprops=dict(facecolor='black', shrink=0.05),
                    horizontalalignment='right', verticalalignment='bottom')
                ax1.annotate('%.0f' %j,
                    xy=((datetime.date.today()- datetime.timedelta(days=1)), j), xycoords='data',
                    xytext=(-1, 0), textcoords='offset points',
                    # arrowprops=dict(facecolor='black', shrink=0.05),
                    horizontalalignment='right', verticalalignment='bottom')
                ax1.annotate("Death/Case Ratio: %.2f" %(i/j),
                    xy=(0.5, 0.5), xycoords = 'axes fraction',
                    xytext=(0.03, 0.83), textcoords='axes fraction',
                    horizontalalignment='left', verticalalignment='top')
                
            if k == 1:
                ax2.annotate('%.0f' %i,
                    xy=((datetime.date.today()- datetime.timedelta(days=1)), i), xycoords='data',
                    xytext=(-1, 0), textcoords='offset points',
                    # arrowprops=dict(facecolor='black', shrink=0.05),
                    horizontalalignment='right', verticalalignment='bottom')
                ax2.annotate('%.0f' %j,
                    xy=((datetime.date.today()- datetime.timedelta(days=1)), j), xycoords='data',
                    xytext=(-1, 0), textcoords='offset points',
                    # arrowprops=dict(facecolor='black', shrink=0.05),
                    horizontalalignment='right', verticalalignment='bottom')
                ax2.annotate("Death/Case Ratio: %.2f" %(i/j),
                    xy=(0.5, 0.5), xycoords = 'axes fraction',
                    xytext=(0.03, 0.83), textcoords='axes fraction',
                    horizontalalignment='left', verticalalignment='top')
                
            if k == 2:
                ax3.annotate('%.0f' %i,
                    xy=((datetime.date.today()- datetime.timedelta(days=1)), i), xycoords='data',
                    xytext=(-1, 0), textcoords='offset points',
                    # arrowprops=dict(facecolor='black', shrink=0.05),
                    horizontalalignment='right', verticalalignment='bottom')
                ax3.annotate('%.0f' %j,
                    xy=((datetime.date.today()- datetime.timedelta(days=1)), j), xycoords='data',
                    xytext=(-1, 0), textcoords='offset points',
                    # arrowprops=dict(facecolor='black', shrink=0.05),
                    horizontalalignment='right', verticalalignment='bottom')
                ax3.annotate("Death/Case Ratio: %.2f" %(i/j),
                    xy=(0.5, 0.5), xycoords = 'axes fraction',
                    xytext=(0.03, 0.83), textcoords='axes fraction',
                    horizontalalignment='left', verticalalignment='top')
                
            if k == 3:
                ax4.annotate('%.0f' %i,
                    xy=((datetime.date.today()- datetime.timedelta(days=1)), i), xycoords='data',
                    xytext=(-1, 0), textcoords='offset points',
                    # arrowprops=dict(facecolor='black', shrink=0.05),
                    horizontalalignment='right', verticalalignment='bottom')
                ax4.annotate('%.0f' %j,
                    xy=((datetime.date.today()- datetime.timedelta(days=1)), j), xycoords='data',
                    xytext=(-1, 0), textcoords='offset points',
                    # arrowprops=dict(facecolor='black', shrink=0.05),
                    horizontalalignment='right', verticalalignment='bottom')
                ax4.annotate("Death/Case Ratio: %.2f" %(i/j),
                    xy=(0.5, 0.5), xycoords = 'axes fraction',
                    xytext=(0.03, 0.83), textcoords='axes fraction',
                    horizontalalignment='left', verticalalignment='top')
                
            if k == 4:
                ax5.annotate('%.0f' %i,
                    xy=((datetime.date.today()- datetime.timedelta(days=1)), i), xycoords='data',
                    xytext=(-1, 0), textcoords='offset points',
                    # arrowprops=dict(facecolor='black', shrink=0.05),
                    horizontalalignment='right', verticalalignment='bottom')
                ax5.annotate('%.0f' %j,
                    xy=((datetime.date.today()- datetime.timedelta(days=1)), j), xycoords='data',
                    xytext=(-1, 0), textcoords='offset points',
                    # arrowprops=dict(facecolor='black', shrink=0.05),
                    horizontalalignment='right', verticalalignment='bottom')
                ax5.annotate("Death/Case Ratio: %.2f" %(i/j),
                    xy=(0.5, 0.5), xycoords = 'axes fraction',
                    xytext=(0.03, 0.83), textcoords='axes fraction',
                    horizontalalignment='left', verticalalignment='top')
    
        ax1_2.annotate("7 day change: \ncases: "+"{:.1%}".format(UK_change_cases)+"\ndeaths: "+"{:.1%}".format(UK_change_deaths),
                    xy=(0.5, 0.5), xycoords = 'axes fraction',
                    xytext=(0.03, 0.83), textcoords='axes fraction',
                    horizontalalignment='left', verticalalignment='top')
    
        ax2_2.annotate("7 day change: \ncases: "+"{:.1%}".format(Swiss_change_cases)+"\ndeaths: "+"{:.1%}".format(Swiss_change_deaths),
                     xy=(0.5, 0.5), xycoords = 'axes fraction',
                     xytext=(0.03, 0.83), textcoords='axes fraction',
                     horizontalalignment='left', verticalalignment='top')
       
        ax3_2.annotate("7 day change: \ncases: "+"{:.1%}".format(US_change_cases)+"\ndeaths: "+"{:.1%}".format(US_change_deaths),
                     xy=(0.5, 0.5), xycoords = 'axes fraction',
                     xytext=(0.03, 0.83), textcoords='axes fraction',
                     horizontalalignment='left', verticalalignment='top')
        
        ax4_2.annotate("7 day change: \ncases: "+"{:.1%}".format(Sweden_change_cases)+"\ndeaths: "+"{:.1%}".format(Sweden_change_deaths),
                     xy=(0.5, 0.5), xycoords = 'axes fraction',
                     xytext=(0.03, 0.83), textcoords='axes fraction',
                     horizontalalignment='left', verticalalignment='top')
        
        ax5_2.annotate("7 day change: \ncases: "+"{:.1%}".format(Brazil_change_cases)+"\ndeaths: "+"{:.1%}".format(Brazil_change_deaths),
                     xy=(0.5, 0.5), xycoords = 'axes fraction',
                     xytext=(0.03, 0.83), textcoords='axes fraction',
                     horizontalalignment='left', verticalalignment='top')
        
        fig.tight_layout(pad=3.0)
    
        plt.savefig("Latest Plot.pdf", dpi=300)    
        # plt.xlabel("Date")
        # plt.ylabel("Cumulative Cases/Deaths")
        # plt.xlim([datetime.date(2020, month, day), datetime.date.today()])
        # plt.ylim([1,1000000])
        # plt.yscale = "log"
 
plot_figure(3,1,2)



