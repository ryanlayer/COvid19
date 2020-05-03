import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import numpy as np
import pandas as pd
import uuid
import time

class MaxSizeCache:
    def __init__(self, size):
        self.cache = {}
        self.size = size
        self.birth_time = time.time()

    def in_cache(self, key):
        self.check_and_clear()
        return key in self.cache.keys()

    def add_to_cache(self, key, value):
        # if the max size have been reached delete the first 5 keys
        self.check_and_clear()
        self.manage_size()
        self.cache[key] = value

    def get(self, key):
        return self.cache[key]

    def check_and_clear(self):
        # check if the cache is older than 3 hours
        if self.birth_time + 10800 < time.time():
            print('Resenting Cache')
            self.cache = {}
            self.birth_time = time.time()

    def manage_size(self):
        if len(self.cache) == self.size:
            print('Removing Some Cache Items')
            keys = list(self.cache.keys())
            for i in range(5):
                del self.cache[keys[i]]

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = [dbc.themes.BOOTSTRAP]
default_point_color = '#69A0CB'
trend_session_cache = MaxSizeCache(100)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def get_map(lats, lons, lat, lon, index):
    mapbox_access_token = open(".mapbox_token").read()
    colors = [default_point_color] * len(lats)
    colors[index] = 'red'
    fig = go.Figure(go.Scattermapbox(\
            lat=lats,
            lon=lons,
            mode='markers',
            marker=go.scattermapbox.Marker( size=14,color=colors) ))

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


def move_index_to_end(items,index):
    val = items[index]
    del items[index]
    items.append(val)
    return items


def move_all_index_to_end(X,Y,df_indexes,index):
    X = move_index_to_end(X,index)
    Y = move_index_to_end(Y,index)
    df_indexes = move_index_to_end(df_indexes,index)
    return X, Y, df_indexes


@app.callback(
    [Output('slip_score', 'figure'),
    Output('weekend_score', 'figure'),
    Output('trend_lines', 'figure'),
    Output('map', 'figure')],
    [Input('week-slider', 'value'),
    Input('slip_score', 'clickData'),
    Input('weekend_score', 'clickData'),
    Input('trend_lines','clickData'),
    Input('session-id','children'),
    Input('map','clickData')])
def update_scatter_plots(selected_col_i,ss_data,ws_data,trend_data,session_id,map_data):
    lon = 40.588928
    lat = -112.071533
    lons = list(ws_df['lon'])
    lats = list(ws_df['lat'])
    ctx = dash.callback_context
    index = -1
    if ctx.triggered[0]['prop_id'] == 'weekend_score.clickData':
        index = int(ws_data['points'][0]['customdata'])
        lon = ws_df.iloc[index,:]['lon']
        lat = ws_df.iloc[index,:]['lat']
    elif ctx.triggered[0]['prop_id'] == 'slip_score.clickData':
        index = int(ss_data['points'][0]['customdata'])
        lon = ss_df.iloc[index,:]['lon']
        lat = ss_df.iloc[index,:]['lat']
    elif ctx.triggered[0]['prop_id'] == 'trend_lines.clickData':
        trend_index = trend_data['points'][0]['curveNumber']
        index = trend_session_cache.get(session_id)[trend_index]
        lon = trend_df.iloc[index,:]['lon']
        lat = trend_df.iloc[index,:]['lat']
    elif ctx.triggered[0]['prop_id'] == 'map.clickData':
        index = map_data['points'][0]['pointNumber']
        lon = ss_df.iloc[index,:]['lon']
        lat = ss_df.iloc[index,:]['lat']

    return slip_score_callback(selected_col_i,ss_data,index),  \
           weekend_score_callback(selected_col_i,ws_data,index), \
           make_trend(index,session_id), get_map(lons, lats, lon, lat, index)


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
        X,Y,df_indexes = move_all_index_to_end(X,Y,df_indexes,point_index)

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
        X,Y,df_indexes = move_all_index_to_end(X,Y,df_indexes,point_index)

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
    return { 'data' : [{ 'x' :ws_df[selected_col], 'type': 'histogram' } ]}


def make_trend(index,session_id):
    dow_date_time= [ x.split()[1:] for x in trend_df.columns[6:]]
    date_time = [x[1:] for x in dow_date_time]

    b = np.array(trend_df.baseline_density.tolist())
    b_norm = 1 + (5*((b - np.min(b)) / np.max(b)))

    fig = go.Figure()
    traces = []
    indexes = list(range(trend_df.shape[0]))
    for idx,row in trend_df.iterrows():
        line_color = default_point_color
        if idx == index:
            line_color = 'red'
        y = row.tolist()[6:]
        x = [i for i in range(len(y))]
        loc = str(row.lat) + ',' + str(row.lon)
        traces.append(go.Scatter(x=x,
                                 y=y,
                                 text=loc,
                                 opacity=0.5,
                                 line=dict(width=b_norm[idx],
                                           color=line_color)))
        if idx == 100:
            break
    traces = move_index_to_end(traces,index)
    trace_indexes = list(range(len(traces)))
    trace_indexes = move_index_to_end(trace_indexes,index)
    trend_session_cache.add_to_cache(session_id,trace_indexes)
    for t in traces:
        fig.add_trace(t)
    fig.update_layout(showlegend=False)
    return fig


ss_df = pd.read_csv('slip.csv')
ws_df = pd.read_csv('ws.csv')
trend_df = pd.read_csv('trend.csv')

y_min = ss_df.iloc[:,5:].min().min()
y_max = ss_df.iloc[:,5:].max().max()


num_weeks = len(ss_df.columns[5:])
pretty_weeks = ['Week ' + str(i+1) for i in range(num_weeks)]

hists = make_ws_hists(num_weeks, ws_df)

marks={i:pretty_weeks[i] for i in range(num_weeks)}

def layout():
    session_id = str(uuid.uuid4())
    return html.Div([
        dbc.Col([
            dbc.Row( [
                dbc.Col( dcc.Graph(id='map',
                                   figure=get_map([40.588928],[-112.071533],40.588928, -112.071533,0)))
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id='trend_lines'))
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
                                   marks=marks,
                                   step=None)),
            ]),
        ]),
        # Hidden div inside the app that stores the intermediate value
        html.Div(session_id,id='session-id', style={'display': 'none'})
    ])

app.layout = layout


if __name__ == '__main__':
    app.run_server(debug=True)
