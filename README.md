Author: Brendon Wee
Date: 20/11/2024

Utilizing the Public https://github.com/r-spacex/SpaceX-API to fetch launch data to answer the following:

Based on the launch data for the different rocket types:
1. How many rockets have been launched each year?
2. How many launches were made from each launch site?

The Python code exports a Dash app that presents a table and stacked bar chart for the following data: Launches per year and Launches per Launch site.
The Python code also exports .csv files for each year, presenting every launch that year, the rocket that was launched and it's launch site.

The respective plots and .csv files that answer the above task questions are stored in the /results directory.

The following libraries are required:
 - requests
 - Pandas
 - Plotly
 - dash

Upon running the python code, opening http://127.0.0.1:8050/ will launch the Dash app.
