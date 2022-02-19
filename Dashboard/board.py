""" hive_functions.py
    Author:         Carl Winkler
    Date:           03. December 2021
    Description:    A simple dash-server solution for a visula web-dashboard of a fake-news data warehouse
"""



import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
import hive_functions
from pyhive import hive

#establish connection
conn = hive.Connection(host="localhost", port=10000, username="cloudera")
cursor = conn.cursor()

# Load data for time series
df = hive_functions.get_time_series(cursor)

# Initialize the app
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

#Data for the bar chart with authors
cnt_class = hive_functions.entries_by_labels(cursor)

#Data for most represented authors
auth_cnt = hive_functions.get_10_pop_auth(cursor)

result = ''

#helper function for the timeseries visualization
def get_options(elem):
    dict_list = []

    for i in elem:
        dict_list.append({'label': i, 'value': i})

    return dict_list

colors = {
    'background': '#737373',
    'text': '#7FDBFF'
}

#HTML/CSS Layout of the dashboard page
app.layout = html.Div(
    children=[
        html.Div(className='row',
                children=[
                    #Right side of the dashboard
                    html.Div(className='four columns div-user-controls',
                            children=[
                                html.H1('Fake-News Data Warehouse Dashboard'),
                                html.P('Provided by: Carl Winkler - ID: 20207528'),
                                html.P('Mail: carl.winkler@ucdconnect.ie'),

                                html.H2('Number of entries - Select Author'),
                                html.P('Select authors of the claims to plot the number of entries by month'),
                                html.Div(
                                    className='div-for-dropdown',
                                    children=[
                                        dcc.Dropdown(id='stockselector', options=get_options(df['stock'].unique()),
                                                    multi=True, value=[df['stock'].sort_values()[0]],
                                                    style={'backgroundColor': '#666699'},
                                                    className='stockselector'
                                        ),
                                         
                                    ],
                                    style={'color': '#1E1E1E'}),
                                
                                dcc.Graph(id='authors',
                                                    figure={
                                            'data': [go.Bar(x=hive_functions.column(auth_cnt,1), 
                                                            y=hive_functions.column(auth_cnt,0),
                                                            orientation='h')
                                            ],
                                            'layout': go.Layout(
                                                colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                                                template='plotly_dark',
                                                paper_bgcolor='rgba(0, 0, 0, 0)',
                                                plot_bgcolor='rgba(0, 0, 0, 0)',
                                                title={'text': 'Authors by entries in this Data Warehouse', 'font': {'color': 'white'}, 'x': 0.5}
                                                )
        
                                            }),
                                html.Div(dcc.Input(id='input-on-submit', type='text')),
                                html.Button('Submit', id='submit-val', n_clicks=0),
                                html.Div(id='container-button-basic',
                                children='Enter a content ID and press submit')
                            ]
                    ),
                    #Left side of the dashboard
                    html.Div(className='eight columns div-for-charts bg-grey',
                            children=[
                                dcc.Graph(id='timeseries', config={'displayModeBar': False}, animate=True),
                                
                                html.Div(className='eight columns div-for-charts bg-grey',
                                    children=[
                                        dcc.Graph(
                                            figure={
                                                    'data': [
                                                        {'x': hive_functions.column(cnt_class,0), 'y':hive_functions.column(cnt_class,1), 'type': 'bar', 'name': 'SF'},
                                                    ],
                                                    'layout': go.Layout(
                                                            colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                                                            template='plotly_dark',
                                                            paper_bgcolor='rgba(0, 0, 0, 0)',
                                                            plot_bgcolor='rgba(0, 0, 0, 0)',
                                                            title={'text': 'Number of entries by label*', 'font': {'color': 'white'}, 'x': 0.5}
                                                        )                                                    
                                            }
                                        )
                                    ], style={'width': '80%', 'display': 'inline-block'}),
                                html.P('*The value 0 relates to false and the reliability goes up to 5 which stands for true'),

                                html.H2('Run a query on Hive'),
                                dcc.Input(id='input-2-state', type='text', value='SELECT * FROM userdb.label', style={'backgroundColor': '#5E0DAC'},),
                                html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
                                html.Button("Download Result", id="btn-download-txt"),
                                dcc.Download(id="download-text"),
                                html.Div(id='output-state')
                        ])
                    
                ])
        ]
)
######################################################
#Callbacks for the elements of the dashboard
######################################################

#return the length of an input
@app.callback(
    Output('container-button-basic', 'children'),
    Input('submit-val', 'n_clicks'),
    State('input-on-submit', 'value'),
    prevent_initial_call=True
)
def update_output(n_clicks, value):
    res = str(hive_functions.getlength(cursor, value))
    return u'''
        Length for ID: {} is: {}
    '''.format(value, res)

#return the result of the user-defined query as text in the dashboard
@app.callback(Output('output-state', 'children'),
              Input('submit-button-state', 'n_clicks'),
              State('input-2-state', 'value'))
def update_output(n_clicks, input2):
    result = str(hive_functions.run_query(cursor, input2))
    return u'''
        clicks: {} query:{} result:{}
    '''.format(n_clicks, input2, result)
    
#let the user download the results of a user-defined query
@app.callback(
    Output("download-text", "data"),
    Input("btn-download-txt", "n_clicks"),
    State('input-2-state', 'value'),
    prevent_initial_call=True,
)
def func(n_clicks, input2) :
    result = str(hive_functions.run_query(cursor, input2))
    return dict(content=result, filename="QueryResult.txt")

# Callback for timeseries
@app.callback(Output('timeseries', 'figure'),
              [Input('stockselector', 'value')])

#this also creates the graph for all authors that are involved by iterating over every author
#The original code of this special graph can be found in several sources in the internet
def update_graph(selected_dropdown_value):
    trace1 = []
    df_sub = df
    for stock in selected_dropdown_value:
        trace1.append(go.Scatter(x=df_sub[df_sub['stock'] == stock].index,
                                 y=df_sub[df_sub['stock'] == stock]['value'],
                                 mode='lines',
                                 opacity=0.7,
                                 name=stock,
                                 textposition='bottom center'))  

    traces = [trace1]
    data = [val for sublist in traces for val in sublist]
    figure = {'data': data,
              'layout': go.Layout(
                  colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  title={'text': 'Monthly claims by selected Top-Authors', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [df_sub.index.min(), df_sub.index.max()]},
              )
              }
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
