# Import required libraries
import pandas as pd
import dash
#import dash_html_components as html
#import dash_core_components as dcc
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
# Extract unique launch site names from the DataFrame
launch_sites = spacex_df['Launch Site'].unique()


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options = [{'label': 'All Sites', 'value': 'ALL'}] + 
                                              [{'label': site, 'value': site} for site in launch_sites],
                                    value = 'ALL',
                                    placeholder = "Select a Launch Site here",
                                    searchable = True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=min_payload,
                                    max=max_payload,
                                    step=1000,
                                    marks={i: f'{i} kg' for i in range(int(min_payload), int(max_payload)+1000, 2000)},
                                    value = [min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Aggregate success counts for all sites
        success_counts = spacex_df.groupby('class').size().reset_index(name='count')
        fig = px.pie(success_counts, 
                     values='count', 
                     names='class', 
                     title='Total Successful Launches for All Sites',
                     color='class', 
                     color_discrete_map={0: 'red', 1: 'green'})  # Red for failure, Green for success
    else:
        # Filter dataframe for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count success (1) and failure (0)
        site_success_counts = filtered_df.groupby('class').size().reset_index(name='count')
        fig = px.pie(site_success_counts, 
                     values='count', 
                     names='class', 
                     title=f'Success vs Failure for {entered_site}',
                     color='class',
                     color_discrete_map={0: 'red', 1: 'green'})

    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

# Callback to update the scatter plot based on site selection and payload range
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    # Filter data based on payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]

    if selected_site == 'ALL':
        # Create scatter plot for all sites
        fig = px.scatter(filtered_df, 
                         x='Payload Mass (kg)', 
                         y='class', 
                         color='Booster Version Category', 
                         title='Payload vs. Launch Success for All Sites',
                         labels={'class': 'Launch Outcome'},
                         hover_data=['Launch Site'])  # Show launch site on hover
    else:
        # Filter data for the selected launch site
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        
        # Create scatter plot for the selected site
        fig = px.scatter(site_filtered_df, 
                         x='Payload Mass (kg)', 
                         y='class', 
                         color='Booster Version Category', 
                         title=f'Payload vs. Launch Success for {selected_site}',
                         labels={'class': 'Launch Outcome'},
                         hover_data=['Launch Site'])  # Show launch site on hover
    
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(port=8051)
