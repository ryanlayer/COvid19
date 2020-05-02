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
default_point_color = '#69A0CB'

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


num_weeks = len(ss_df.columns[5:])
pretty_weeks = ['Week ' + str(i+1) for i in range(num_weeks)]

hists = make_ws_hists(num_weeks, ws_df)

app.layout = html.Div([
    dbc.Col([
        dbc.Row( [
            dbc.Col( dcc.Graph(id='map',figure=get_map(40.588928, -112.071533)))
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
    Output('map', 'figure'),
    [Input('weekend_score', 'clickData'),
    Input('slip_score', 'clickData')])
def map_callback(ws_data,ss_data):
    lon = 40.588928
    lat = -112.071533

    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = 'No clicks yet'
    elif ctx.triggered[0]['prop_id'] == 'weekend_score.clickData':
        lon = ws_df.iloc[int(ws_data['points'][0]['customdata']),:]['lon']
        lat = ws_df.iloc[int(ws_data['points'][0]['customdata']),:]['lat']
    else:
        lon = ss_df.iloc[int(ss_data['points'][0]['customdata']),:]['lon']
        lat = ss_df.iloc[int(ss_data['points'][0]['customdata']),:]['lat']

    return get_map(lon, lat)


def move_index_to_end(X,Y,df_indexes,index):
    x_val = X[index]
    y_val = Y[index]
    df_index_val = df_indexes[index]
    del X[index]
    del Y[index]
    del df_indexes[index]
    X.append(x_val)
    Y.append(y_val)
    df_indexes.append(df_index_val)
    return X, Y, df_indexes


@app.callback(
    [Output('slip_score', 'figure'),
    Output('weekend_score', 'figure')],
    [Input('week-slider', 'value'),
    Input('slip_score', 'clickData'),
    Input('weekend_score', 'clickData')])
def update_scatter_plots(selected_col_i,ss_data,ws_data):
    ctx = dash.callback_context

    point_index = -1
    if ctx.triggered[0]['prop_id'] == 'weekend_score.clickData':
        point_index = int(ws_data['points'][0]['customdata'])
    elif ctx.triggered[0]['prop_id'] == 'slip_score.clickData':
        point_index = int(ss_data['points'][0]['customdata'])

    return slip_score_callback(selected_col_i,ss_data,point_index), weekend_score_callback(selected_col_i,ws_data,point_index)


def slip_score_callback(selected_col_i,ss_data,point_index):
    slip_weeks = ss_df.columns[5:]
    selected_col = slip_weeks[selected_col_i]
    df_indexes = list(range(ss_df.shape[0]))
    point_color = default_point_color
    filtered_df = ss_df[['baseline_density',selected_col]]

    X = list(filtered_df['baseline_density'])
    Y = list(filtered_df[selected_col])
    df_indexes = list(range(len(X)))

    if point_index != -1:
        point_color = 'red'
        # move the point of interest to the end so it displays on top
        X,Y,df_indexes = move_index_to_end(X,Y,df_indexes,point_index)

    marker_colors = [default_point_color] * len(X)
    marker_colors[-1] = point_color
    traces = []
    traces.append(dict(
        x=X,
        y=Y,
        customdata=df_indexes,
        mode='markers',
        opacity=0.7,
        marker={
            'size': 15,
            'line': {'width': 0.5, 'color': 'white'},
            'color': marker_colors
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


def weekend_score_callback(selected_col_i,ws_data,point_index):
    ws_weeks = ws_df.columns[6:]
    selected_col = ws_weeks[selected_col_i]
    point_color = default_point_color
    X = list(ws_df['baseline_ws'])
    Y = list(ws_df[selected_col])
    df_indexes = list(range(len(X)))

    if point_index != -1:
        point_color = 'red'
        # move the point of interest to the end so it displays on top
        X,Y,df_indexes = move_index_to_end(X,Y,df_indexes,point_index)

    traces = []
    marker_colors = [default_point_color] * len(ws_df[selected_col])
    marker_colors[-1] = point_color
    traces.append(dict(
        x=X,
        y=Y,
        customdata=df_indexes,
        mode='markers',
        opacity=0.7,
        marker={
            'size': 15,
            'line': {'width': 0.5, 'color': 'white'},
            'color':marker_colors
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
    return { 'data' : [
            { 'x' :ws_df[selected_col],
              'type': 'histogram' }
            ]}


if __name__ == '__main__':
    app.run_server(debug=True)
