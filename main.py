# JLR Coding Assessment - Senior Software Developer Role 2024
# Task: The task is based on fetching data from a publicly hosted server and processing data to produce a
#       result which can answer a specific query. Based on the launch data for the different rocket types:
#           1. How many rockets have been launched each year?
#           2. How many launches were made from each launch site?
#
# Author: Brendon Wee
# Date: 20/11/2024

# Import libraries
from datetime import datetime
import requests
import os

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output

# Establishing Dash app
app = dash.Dash(__name__)

# Fetches data for a given URL with a GET Request
def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return []

# Creates a dictionary of all launch data for each year
def categorise_year(cl):
    years = {}
    for entry in cl:
        # Parse the date and extract the year
        try: # Extract the year from each launch's `date_utc` field
            year = datetime.strptime(entry["date_utc"], '%Y-%m-%dT%H:%M:%S.%fZ').year
        except ValueError:
            year = datetime.strptime(entry["date_utc"], '%Y-%m-%dT%H:%M:%SZ').year

        if year not in years:
            years[year] = []
        years[year].append(entry)

    return years

# Returns a list of a count of the number of launch attempts and successful launches for each year
def launches_per_year(years):
    data = []
    # Loop through each key-value pair in the dictionary
    for key, values in years.items():
        # Count the number of items in the list (value) for each key
        data.append([key, len(values), len(list(filter(lambda x: x['success'] == True, values)))])
        #print(key," : Number of launch attempts:", len(values), ", Number of successful launches:", len(list(filter(lambda x: x["success"] == True, values))))

    return data

# Returns a list of the number of launch attempts and successful launches at each launch site
def launches_per_site(cl):
    data = []
    # Loop through each key-value pair in the dictionary
    for entry in cl:
        # Count the number of items in the list (value) for each key
        data.append([entry['id'], entry['name'],entry['full_name'],entry['launch_attempts'],entry['launch_successes']])
        #print("Launch Site: ",entry["name"],"(",entry["id"],")", "Number of Launch attempts: ",entry["launch_attempts"],"Number of Successful Launches: ",entry["launch_successes"])

    return data

# Collates rockets, launches and launchpads data and returns a list of all launches, the rockets that was launched, where they were launched from, number of launch attempts and successful launches for that year
def launches_per_rocket(years, sites, rockets):
    data = {}
    #Loop through each year
    for key, values in years.items():
        #Count the number of items in the list (value) for each key
        year = []
        #Loop through each launch data, find the corresponding rocket name
        for value in values:
            rocket_name = next(filter(lambda x: x['id'] == value['rocket'], rockets))['name']

            success = "Failed"
            if value['success']:
                success = "Success"

            year.append([value['rocket'],rocket_name,value['launchpad'],sites['id' == value['launchpad']]['name'],success])
            #print(value['rocket'],rocket_name,value['launchpad'],sites['id' == value['launchpad']]['name'],success)

        df_rocket = pd.DataFrame(year)
        df_rocket.columns = ['Rocket ID','Rocket Name','Launch Site ID','Launch Site Name','Launch Status']
        data[key] = df_rocket

    return data

# Create Plotly Figures containing 2 subplots
def make_fig(df, title1, title2, legend1, legend2, index, legend_x):
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.35, 0.65],
        shared_xaxes=True,
        horizontal_spacing=0.1,
        vertical_spacing=0.1,
        specs=[[{'type': 'table'}, {'type': 'bar'}]],
        subplot_titles=(title1,
                        title2)
    )

    fig.add_trace(go.Bar(
        name=legend1,
        x=df[index],
        y=df['Number of Launch Attempts'],
        marker=go.bar.Marker(color='RGB(217, 42, 11)')),
        row=1, col=2)

    fig.add_trace(go.Bar(
        name=legend2,
        x=df[index],
        y=df['Number of Successful Launches'],
        marker=go.bar.Marker(color='RGB(28, 217, 11)')),
        row=1, col=2)

    fig.update_layout(xaxis_title=index.title(),
                      yaxis_title='Number of Launches',
                      legend=dict(y=0.99, x=legend_x, orientation='h'),
                      xaxis=dict(tickmode='linear'),
                      barmode='overlay')

    fig.add_trace(go.Table(
        header=dict(values=df.columns,
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=df.transpose().values.tolist(),
                   fill_color='lavender',
                   align='left')),
        row=1, col=1)

    fig.update_layout(
        autosize=True,
        margin=dict(l=10, r=10, t=40, b=10),
        #height=1000,
        #width=1400
    )

    return fig

#Fetching Data
cl_launch = fetch_data("https://api.spacexdata.com/v5/launches")
cl_pad = fetch_data("https://api.spacexdata.com/v4/launchpads")
cl_rocket = fetch_data("https://api.spacexdata.com/v4/rockets")

# Forming dictionary containing launch data for each year
years = categorise_year(cl_launch)

# 1. Displays how many rockets have been launched each year
df_launch = pd.DataFrame(launches_per_year(years))
df_launch.columns = ['Year', 'Number of Launch Attempts', 'Number of Successful Launches']

# Adding in missing years and replace null with N/A
df_year_range = pd.DataFrame({'Year': range(df_launch['Year'].min(), datetime.today().year+1)})
df_launch = pd.merge(df_year_range, df_launch, how='left',on='Year')
df_launch = df_launch.fillna('N/A')
#print("Grouped Data by Year:")
#print(df_launch)

# Create the Plotly figure for Launches per Year
fig_year = make_fig(df_launch,
                    'Table presenting number of Launch Attempts and<br>Successful Launches per year',
                    'Bar Chart presenting number of Launch Attempts and<br>Successful Launches over time',
                    'Failed Launch Attempts',
                    'Successful Launches',
                    'Year',
                    0.42)
plot_year = fig_year.to_html(full_html=False)

# 2. Displays how many launches were made from each launch site
df_site = pd.DataFrame(launches_per_site(cl_pad))
df_site.columns = ['Launch Site ID','Launch Site','Launch Site Full Name','Number of Launch Attempts','Number of Successful Launches']
df_site = df_site.fillna('N/A')
#print("Grouped Data by Launch Site:")
#print(df_site)

# Create the Plotly figure for Launches per Launch Site
fig_site = make_fig(df_site.iloc[:, 1:],
                    'Table presenting number of Launch Attempts and<br>Successful Launches per Launch site',
                    'Bar Chart presenting number of Launch Attempts and<br>Successful Launches at each Launch site',
                    'Failed Launch Attempts',
                    'Successful Launches',
                    'Launch Site',
                    0.755)

plot_site = fig_site.to_html(full_html=False)

# MORE. Exports for each year: rockets launched, their launch site, number of launch attempts and successful launches
# Create a 'results' directory if it doesn't already exist
if not os.path.exists('results'):
    os.makedirs('results')

rockets = launches_per_rocket(years, cl_pad, cl_rocket)
# Export data to .csv file
for key, values in rockets.items():
    file_path = f"results/SpaceX_Rockets_launched_{str(key)}.csv"
    values.to_csv(file_path, encoding='utf-8', index=False, header=True)


# Define the layout of the Dash app with Tabs
app.layout = html.Div([
    html.H1("JLR Take Home Coding Assessment"),
    html.P("Author: Brendon Wee, Date: 20/11/2024",className="author"),
    html.P("The task is based on fetching data from a publicly hosted server and processing data to produce a result which can answer a specific query.",className="subtitle"),
    html.P("Based on the launch data for the different rocket types:", className="subtitle"),
    html.P("1. How many rockets have been launched each year? See Launches per Year Tab",className="subtitle"),
    html.P("2. How many launches were made from each launch site? See Launches per Launch Site Tab",className="subtitle"),

    # Tabs component
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Launches per Year', value='tab-1'),
        dcc.Tab(label='Launches per Launch Site', value='tab-2'),
    ]),

    # Tab content
    html.Div(id='tabs-content')
])

# Callback to update the content based on the selected tab
@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value')
)
def render_tab_content(tab):
    if tab == 'tab-1':
        return dcc.Graph(figure=fig_year, className='graph-container')  # Show the bar chart
    elif tab == 'tab-2':
        return dcc.Graph(figure=fig_site, className='graph-container')  # Show the scatter plot

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

#END