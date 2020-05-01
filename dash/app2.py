import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

import pandas as pd

def get_map(lat, lon):
    mapbox_access_token = open(".mapbox_token").read()

    fig = go.Figure(go.Scattermapbox( lat=[lat],
                                      lon=[lon],
                                      mode='markers',
                                      marker=go.scattermapbox.Marker( size=14),
    ))

    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=lat,
                lon=lon
            ),
            pitch=0,
            zoom=10,
        )
    )

    return fig

def make_ws_hists(num_weeks, ws_df):
    fig = make_subplots(rows=1, cols=num_weeks)
    ws_weeks = ws_df.columns[6:]

    week_i = 1
    for week in ws_weeks:
        h = go.Histogram(x=ws_df[week],
                         name='Week ' + str(week_i))
        fig.append_trace( h, 1, week_i)

        week_i += 1
    return fig


ss_df = pd.read_csv('slip.csv')
ws_df = pd.read_csv('ws.csv')

y_min = ss_df.iloc[:,5:].min().min()
y_max = ss_df.iloc[:,5:].max().max()

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = [dbc.themes.BOOTSTRAP]


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


num_weeks = len(ss_df.columns[5:])
pretty_weeks = ['Week ' + str(i+1) for i in range(num_weeks)]

hists = make_ws_hists(num_weeks, ws_df)

app.layout = html.Div([
    dbc.Col([
        dbc.Row( [
            dbc.Col( dcc.Graph(figure=get_map(40.588928, -112.071533)))
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='weekend_hist'), width=4),
            dbc.Col(dcc.Graph(id='weekend_score'), width=4),
            dbc.Col(dcc.Graph(id='slip_score'), width=4)
        ],no_gutters=True,),
        dbc.Row( [
            dbc.Col(dcc.Slider(id='week-slider',
                               min=0,
                               max=num_weeks-1,
                               value=num_weeks-1,
                               marks={i:pretty_weeks[i] for i in range(num_weeks)},
                               step=None)),
        ]),
    ])
])


@app.callback(
    Output('slip_score', 'figure'),
    [Input('week-slider', 'value')])
def slip_score(selected_col_i):
    slip_weeks = ss_df.columns[5:]
    selected_col = slip_weeks[selected_col_i]

    filtered_df = ss_df[['baseline_density',selected_col]]
    traces = []
    traces.append(dict(
        x=filtered_df['baseline_density'],
        y=filtered_df[selected_col],
        mode='markers',
        opacity=0.7,
        marker={
            'size': 15,
            'line': {'width': 0.5, 'color': 'white'}
        },
    ))

    return {
        'data': traces,
        'layout': dict(
            xaxis={'title':'Baseline density'},
            yaxis={'title':'Slip score'},
            hovermode='closest',
            transition = {'duration': 500},
        )
    }

@app.callback(
    Output('weekend_score', 'figure'),
    [Input('week-slider', 'value')])
def weekend_score(selected_col_i):
    ws_weeks = ws_df.columns[6:]
    selected_col = ws_weeks[selected_col_i]

    traces = []
    traces.append(dict(
        x=ws_df['baseline_ws'],
        y=ws_df[selected_col],
        mode='markers',
        opacity=0.7,
        marker={
            'size': 15,
            'line': {'width': 0.5, 'color': 'white'}
        },
    ))

    return {
        'data': traces,
        'layout': dict(
            xaxis={'title':'Baseline ws'},
            yaxis={'title':'Week ' + str(selected_col_i+1) + ' score'},
            hovermode='closest',
            transition = {'duration': 500},
        )
    }

@app.callback(
    Output('weekend_hist', 'figure'),
    [Input('week-slider', 'value')])
def make_ws_hist(selected_col_i):
    ws_weeks = ws_df.columns[6:]
    selected_col = ws_weeks[selected_col_i]
    #h = go.Histogram(x=ws_df[selected_col],
                     #name='Week ' + str(selected_col_i + 1))
    #fig = go.Figure(data=[h])
    return { 'data' : [ 
            { 'x' :ws_df[selected_col], 
              'type': 'histogram' } 
            ]}


if __name__ == '__main__':
    app.run_server(debug=True)
