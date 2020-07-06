import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import numpy as np
import pandas as pd
import uuid
import time
import copy
import datetime
import json
import argparse
from flask import request

with open('boulder_config.json') as config_file:
    config = json.load(config_file)

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result
    return timed

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
external_stylesheets = [dbc.themes.BOOTSTRAP,'style.css']
default_point_color = '#69A0CB'
trend_session_cache = MaxSizeCache(300)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


def x_round(x):
    return round(x*4)/4

def make_unique_trends_df(tdf):
    df = tdf.iloc[:,5:]
    vals = list(df.iloc[:,-1])

    rounded_vals = [x_round(x) for x in vals]

    keepers = [rounded_vals.index(x) for x in set(rounded_vals)]

    sub = tdf[tdf.index.isin(keepers)]
    return sub


def prep_session_data(session_id,url_path_name):
    if url_path_name is None:
        return

    id = str(session_id)
    if trend_session_cache.in_cache(id+'_ss') and trend_session_cache.in_cache(id+'_ws') and trend_session_cache.in_cache(id+'_trends') and trend_session_cache.in_cache(id+'_unique_ss') and trend_session_cache.in_cache(id+'_unique_ws') and trend_session_cache.in_cache(id+'_unique_trends'):
        return

    cities_df = pd.read_csv('cities.tsv',sep='\t')

    if url_path_name[0] == '/':
        if len(url_path_name) == 1:
            print("Choosing Boulder as Default")
            url_path_name = 'boulder'
        else:
            print("Exchanging city...")
            url_path_name = url_path_name[1:]
        print(url_path_name)

    sub = cities_df[cities_df['url'] == url_path_name]

    trend_session_cache.add_to_cache(id+'_ss',pd.read_csv(list(sub['ss'])[0]))
    trend_session_cache.add_to_cache(id+'_ws',pd.read_csv(list(sub['ws'])[0]))
    trend_session_cache.add_to_cache(id+'_trends',pd.read_csv(list(sub['trend'])[0]))
    trend_session_cache.add_to_cache(id+'_unique_ss',pd.read_csv(list(sub['unique_ss'])[0],index_col = 0))
    trend_session_cache.add_to_cache(id+'_unique_ws',pd.read_csv(list(sub['unique_ws'])[0],index_col = 0))
    trend_session_cache.add_to_cache(id+'_unique_trends',make_unique_trends_df(trend_session_cache.get(id+'_trends')))

#@timeit
def get_map(lats, lons, lat, lon, indexes):
    mapbox_access_token = open(".mapbox_token").read()
    #mapbox_access_token = "pk.eyJ1IjoiZGV2aW5idXJrZTAiLCJhIjoiY2tiMWE3MXA5MDRnajJ4bjBrNmFhNzI2NyJ9.SfMDEZ1udv4QJOSnof4l1A"
    ###### ---- ######
    colors = [default_point_color] * len(lats)
    opacity = [0.25] * len(lats)
    for index in indexes:
        if index == -1:
            continue
        colors[index] = 'red'
        opacity[index] = 1.0
    fig = go.Figure(go.Scattermapbox(\
            lat=lats,
            lon=lons,
            mode='markers',
            marker=go.scattermapbox.Marker(size=14,
                                           opacity=opacity,
                                           color=colors) ))

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
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
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
    Input('map','clickData'),
    Input('map','selectedData'),
    Input('url', 'pathname')],
    [State('trend_lines', 'figure')])
def update_scatter_plots(selected_week,
                         ss_data,
                         ws_data,
                         trend_data,
                         session_id,
                         map_data,
                         map_selection,
                         url_path_name,
                         trend_figure):
    prep_session_data(session_id,url_path_name)

    # default lon and lat to be the center of the data being plotted
    try:
        ss_df = trend_session_cache.get(str(session_id) + '_ss')
        ws_df = trend_session_cache.get(str(session_id) + '_ws')
        trend_df = trend_session_cache.get(session_id+'_trends')
        unique_trend_df = trend_session_cache.get(session_id+'_unique_trends')
        lat = sum(ss_df['lat']) / ss_df.shape[0]
        lon = sum(ss_df['lon']) / ss_df.shape[0]
        lons = list(ws_df['lon'])
        lats = list(ws_df['lat'])
    except KeyError:
        lat = 0
        lon = 0
        lons = []
        lats = []

    ctx = dash.callback_context
    indexes = [-1]
    if ctx.triggered[0]['prop_id'] == 'weekend_score.clickData':
        indexes = [int(ws_data['points'][0]['customdata'])]
        lon = ws_df.iloc[indexes[0],:]['lon']
        lat = ws_df.iloc[indexes[0],:]['lat']
    elif ctx.triggered[0]['prop_id'] == 'slip_score.clickData':
        indexes = [int(ss_data['points'][0]['customdata'])]
        lon = ss_df.iloc[indexes[0],:]['lon']
        lat = ss_df.iloc[indexes[0],:]['lat']
    elif ctx.triggered[0]['prop_id'] == 'trend_lines.clickData':
        trend_index = trend_data['points'][0]['curveNumber']
        indexes = [trend_session_cache.get(session_id)[trend_index]]
        lon = trend_df.iloc[indexes[0],:]['lon']
        lat = trend_df.iloc[indexes[0],:]['lat']
    elif ctx.triggered[0]['prop_id'] == 'map.clickData':
        indexes = [map_data['points'][0]['pointNumber']]
        lon = ss_df.iloc[indexes[0],:]['lon']
        lat = ss_df.iloc[indexes[0],:]['lat']
    elif ctx.triggered[0]['prop_id'] == 'map.selectedData':
        indexes = [x['pointNumber'] for x in map_selection['points']]
        lon = ss_df.iloc[indexes[0],:]['lon']
        lat = ss_df.iloc[indexes[0],:]['lat']
    return slip_score_callback(selected_week,session_id,indexes),  \
           weekend_score_callback(selected_week,session_id,indexes), \
           make_trend(selected_week,indexes,session_id,trend_figure), \
           get_map(lons, lats, lon, lat, indexes)

#@timeit
def slip_score_callback(selected_week,session_id,point_indexes):
    try:
        unique_ss = trend_session_cache.get(str(session_id) + '_unique_ss')
        ss_df = trend_session_cache.get(str(session_id) + '_ss')
    except KeyError:
        return go.Figure()
    slip_weeks = unique_ss.columns[5:]
    selected_col = slip_weeks[selected_week]
    df_indexes = list(unique_ss.index)
    point_color = default_point_color
    filtered_df = unique_ss[['baseline_density',selected_col]]

    X = list(filtered_df['baseline_density'])
    Y = list(filtered_df[selected_col])
    hist_X = list(ss_df['baseline_density'])
    hist_Y = list(ss_df[selected_col])

    marker_colors = [default_point_color] * len(X)
    # if there are points selected, add them!
    if len(point_indexes) > 0 and point_indexes[0] != -1:
        for i in point_indexes:
            X.append(ss_df['baseline_density'][i])
            Y.append(ss_df[selected_col][i])
            df_indexes.append(i)
            marker_colors.append('red')

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

    week_1 = 'Week ' + str(selected_week) if selected_week > 0 else 'Baseline'
    week_2 = 'week ' +str(selected_week+1)
    y_label = week_1 + ' to ' + week_2 + ' slip'

    #fig = go.Figure()

    fig = make_subplots(rows=2, cols=2,
                        row_heights=[0.15, 0.85],
                        column_widths=[0.85, 0.15],
                        horizontal_spacing = 0.0,
                        vertical_spacing = 0.0)

    fig.add_trace(go.Histogram(x=hist_X,marker_color=default_point_color), row=1, col=1)
    fig.update_xaxes(showticklabels=False,
                     row=1, col=1)
    fig.update_yaxes( title_text='Freq',
                     row=1, col=1)
    fig.add_trace(go.Histogram(y=hist_Y,marker_color=default_point_color), row=2, col=2)
    fig.update_yaxes(showticklabels=False,
                     row=2, col=2)
    fig.update_xaxes(title_text='Freq',
                     row=2, col=2)

    fig.add_trace(traces[0], row=2, col=1)

    fig.update_layout(dict(
        #xaxis={'title':'Baseline density'},
        #yaxis={'title':y_label},
        hovermode='closest',
        transition = {'duration': 500},
        # margin={'t':10,'l':50,'r':0}
        margin={'t':0,'b':0,'r':0,'l':0}
    ))
    min_y = round(min(hist_Y), 2)
    max_y = round(max(hist_Y), 2)
    min_x = int(round(min(hist_X)))
    max_x = int(round(max(hist_X)))
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title_text='Baseline density', row=2, col=1, range=[min_x, max_x])
    fig.update_yaxes(title_text=y_label, row=2, col=1, range=[min_y, max_y])

    return fig

#@timeit
def weekend_score_callback(selected_week,session_id,point_indexes):
    try:
        unique_ws = trend_session_cache.get(str(session_id) + '_unique_ws')
        ws_df = trend_session_cache.get(str(session_id) + '_ws')
    except KeyError:
        return go.Figure()

    ws_weeks = unique_ws.columns[6:]
    selected_col = ws_weeks[selected_week]
    point_color = default_point_color
    X = list(unique_ws['baseline_ws'])
    Y = list(unique_ws[selected_col])
    hist_X = list(ws_df['baseline_ws'])
    hist_Y = list(ws_df[selected_col])
    df_indexes = list(unique_ws.index)

    marker_colors = [default_point_color] * len(X)

    if point_indexes[0] != -1:
        point_color = 'red'
        for index in point_indexes:
            X.append(ws_df['baseline_ws'][index])
            Y.append(ws_df[selected_col][index])
            df_indexes.append(index)
            marker_colors.append('red')

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
            'color':marker_colors
        },
    ))

    y_label = 'Week ' + str(selected_week+1) + ' weekend score'
    x_label = 'Week ' + str(selected_week) + ' weekend score'
    if selected_week == 0:
        x_label = 'Baseline weekend score'

    fig = make_subplots(rows=2, cols=2,
                        row_heights=[0.15, 0.85],
                        column_widths=[0.85, 0.15],
                        horizontal_spacing = 0.0,
                        vertical_spacing = 0.0)


    fig.add_trace(go.Histogram(x=hist_Y, marker_color=default_point_color), row=1, col=1)
    fig.update_xaxes(showticklabels=False,
                     row=1, col=1)
    fig.update_yaxes( title_text='Freq',
                     row=1, col=1)

    fig.add_trace(go.Histogram(y=hist_X, marker_color=default_point_color), row=2, col=2)
    fig.update_yaxes(showticklabels=False,
                     row=2, col=2)
    fig.update_xaxes(title_text='Freq',
                     row=2, col=2)

    fig.add_trace(traces[0], row=2, col=1)

    min_y = round(min(hist_Y), 2)
    max_y = round(max(hist_Y), 2)
    min_x = round(min(hist_X), 2)
    max_x = round(max(hist_X), 2)
    fig.update_layout(dict(
        hovermode='closest',
        transition = {'duration': 500},
        margin={'t':0,'b':0,'r':0,'l':0}
    ))
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title_text=x_label, row=2, col=1, range=[min_x,max_x])
    fig.update_yaxes(title_text=y_label, row=2, col=1, range=[min_y,max_y])

    return fig


def get_date_time(header):
    date_time = []
    for dow_date_time in header:
        state,dow,date,time = dow_date_time.split()
        Y,M,D = date.split('-')
        h = time[:2]
        m = time[2:]
        date_time.append(datetime.datetime(int(Y),
                                           int(M),
                                           int(D),
                                           int(h),
                                           int(m) ))
    return date_time

def update_trend_week(fig, week,session_id):
    try:
        trend_df = trend_session_cache.get(session_id+'_trends')
        unique_trend_df = trend_session_cache.get(session_id+'_unique_trends')
    except KeyError:
        return go.Figure()
    dow_date_time= [ x.split()[1:] for x in trend_df.columns[6:]]
    date_time = get_date_time(trend_df.columns[6:])
    if isinstance(fig, dict):
        fig['layout']['shapes'][0]['x0'] = date_time[week*21]
        fig['layout']['shapes'][0]['x1'] = date_time[min(week*21+21,
                                                         len(date_time)-1)]
    else:
        fig.update_layout(shapes=[
                dict(
                    type='rect',
                    xref='x',
                    x0=date_time[week*21],
                    x1=date_time[min(week*21+21, len(date_time)-1)],
                    yref='paper', y0=0, y1=1,
                    fillcolor='grey',
                    opacity=0.15,
                    layer='below',
                    line_width=0)
        ])

#@timeit
def make_base_trend_plot(session_id):
    try:
        trend_df = trend_session_cache.get(session_id+'_trends')
        unique_trend_df = trend_session_cache.get(session_id+'_unique_trends')
    except KeyError:
        return go.Figure()
    fig = go.Figure()
    dow_date_time= [ x.split()[1:] for x in unique_trend_df.columns[6:]]
    date_time = get_date_time(unique_trend_df.columns[6:])

    b = np.array(unique_trend_df.baseline_density.tolist())
    b_norm = 1 + (5*((b - np.min(b)) / np.max(b)))

    traces = []
    for idx,row in unique_trend_df.iterrows():
        line_color = default_point_color
        opactiy = 0.2
        y = row.tolist()[6:]
        x = date_time
        loc = str(row.lat) + ',' + str(row.lon)
        try:
            index = list(unique_trend_df.index).index(idx)
        except ValueError:
            index = 0
        traces.append(go.Scatter(x=x,
                                 y=y,
                                 text=loc,
                                 opacity=opactiy,
                                 line=dict(width=b_norm[index],
                                           color=line_color)))
    trace_indexes = list(range(len(traces)))
    trend_session_cache.add_to_cache(session_id,list(unique_trend_df.index))
    for t in traces:
        fig.add_trace(t)

    fig.update_layout(showlegend=False,
                      yaxis_title="Trend",
                      margin={'t':10,'l':50,'r':0})

    return fig

#@timeit
def make_new_trends(indexes,session_id):
    trend_df = trend_session_cache.get(session_id+'_trends')
    dow_date_time= [ x.split()[1:] for x in trend_df.columns[6:]]
    date_time = get_date_time(trend_df.columns[6:])

    b = np.array(trend_df.baseline_density.tolist())
    b_norm = 1 + (5*((b - np.min(b)) / np.max(b)))

    traces = []
    for idx,row in trend_df.iloc[indexes,:].iterrows():
        line_color = 'red'
        opactiy = 1.0
        y = row.tolist()[6:]
        x = date_time
        loc = str(row.lat) + ',' + str(row.lon)
        traces.append(dict(x=x,
                            y=y,
                            text=loc,
                            opacity=opactiy,
                            line=dict(width=b_norm[idx],
                            color=line_color),
                            type='scatter'))
    return traces

#@timeit
def make_trend(selected_week, indexes, session_id, trend_figure):
    try:
        unique_trend_df = trend_session_cache.get(session_id+'_unique_trends')
    except KeyError:
        return go.Figure()
    # check if the base figures already exists in memory
    if trend_figure is not None and len(trend_figure) != 0:
        # add more traces on top of the base plot
        traces = make_new_trends(indexes,session_id)
        trace_indexes = list(unique_trend_df.index)
        # remove the traces previously added to highlight specific traces
        trend_figure['data'] = trend_figure['data'][:len(trace_indexes)]
        for i in indexes:
            trace_indexes.append(i)
        for t in traces:
            trend_figure['data'].append(t)
        trend_session_cache.add_to_cache(session_id, trace_indexes)

        update_trend_week(trend_figure, selected_week, session_id)
        return trend_figure
    else:
        trendlines_fig = make_base_trend_plot(session_id)
        update_trend_week(trendlines_fig, selected_week, session_id)
        return trendlines_fig


@app.callback(
    [Output('week-slider', 'min'),
    Output('week-slider', 'max'),
    Output('week-slider', 'value'),
    Output('week-slider', 'marks')],
    [Input('url', 'pathname'),
    Input('session-id','children')])
def make_slider(url_path_name,session_id):
    if url_path_name is None:
        return 0,0,0,{}
    cities_df = pd.read_csv('cities.tsv',sep='\t') #cities dataframe
    if url_path_name[0] == '/':
        if len(url_path_name) == 1:
            print("Choosing Boulder as Default")
            url_path_name = 'boulder'
        else:
            print('Exchanging city...')
            url_path_name = url_path_name[1:]
        print(url_path_name)

    sub = cities_df[cities_df['url'] == url_path_name]
    print(sub)
    ss_df = pd.read_csv(list(sub['unique_ss'])[0],index_col=0)

    num_weeks = len(ss_df.columns[5:])
    pretty_weeks = ['Week ' + str(i+1) for i in range(num_weeks)]

    marks={i:pretty_weeks[i] for i in range(num_weeks)}

    return 0, num_weeks-1,num_weeks-1, marks


def layout():
    session_id = str(uuid.uuid4())
    return html.Div([
        dcc.Location(id='url', refresh=False),
        dbc.Row([
            html.Div([
                html.H1('COvid-19'),
            ],style={'grid-row': '1','grid-column': '2'}),
            html.Div([
                html.Img(src='assets/covid19.png', height=50),
                html.Img(src='assets/cu.png', height=50),
                html.Img(src='assets/csu.jpg', height=50)
            ], style={'grid-row': '1','grid-column': '3'})
        ],style={'display': 'grid', 'grid-template-columns': 'auto auto auto'}),
        dbc.Col([
            dbc.Row( [
                dbc.Col( dcc.Graph(id='map',
                                   figure=get_map([0],
                                                  [0],
                                                  None,
                                                  None,[]),
                                   style={'height':'47vh'})),
            ],no_gutters=True),
            dbc.Row([
                dbc.Col(dcc.Graph(id='trend_lines',style={'height':'47vh'}))
            ],no_gutters=True),
        ],width=8,style={'float': 'left','height':'100vh','padding':'0'}),
        dbc.Col([
            dcc.Graph(id='weekend_score',style={'height':'44vh'}),
            dcc.Graph(id='slip_score',style={'height':'44vh'}),
            dcc.Slider(id='week-slider',
                       min=0,
                       max=0,
                       value=0,
                   step=None)
        ],width=4,style={'float': 'left','height':'90vh'}),
        # Hidden div inside the app that stores the intermediate value
        html.Div(session_id,id='session-id', style={'display': 'none'})
    ])


app.layout = layout
app.title = 'COvid-19'

if __name__ == '__main__':
    app.run_server(debug=True)
