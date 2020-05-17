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

import math

def get_dist(p1,p2):
    return math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )

ss_df = pd.read_csv('slip.csv')
ws_df = pd.read_csv('ws.csv')

def subset_df(df,col1,col2,treshold,filename):
    indexes = list(range(df.shape[0]))
    keep_or_done_dict = { i:0 for i in indexes}
    for i in indexes:
        if i % 100 == 0:
            print(i)
        for j in indexes:
            if i == j:
                continue
            else:
                dist = get_dist([df.iloc[i,col1],df.iloc[i,col2]],[df.iloc[j,col1],df.iloc[j,col2]])
                if dist < treshold and keep_or_done_dict[i] >= 0:
                    keep_or_done_dict[j] = -1
                    keep_or_done_dict[i] = 1
    sum([ key for key in keep_or_done_dict if keep_or_done_dict[key] >= 0])
    final_indexes = [ key for key in keep_or_done_dict if keep_or_done_dict[key] >= 0]
    df[df.index.isin(final_indexes)].to_csv(filename)

subset_df(ss_df,4,5,.75,'unique_ss.csv')
subset_df(ws_df,-2,-1,.05,'unique_ws.csv')
