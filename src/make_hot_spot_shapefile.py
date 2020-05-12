import  sys
import numpy as np
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import argparse
import csv
import collections
from sklearn.linear_model import LinearRegression
import geopandas as gpd
import pandas as pd
import os
import shutil

from shapely.geometry import Polygon, Point

Window = collections.namedtuple('Window', 'index dayofweek')

shape_i = 0
baseline_range = {'start':3, 'end':24}
crisis_range = {'start':24}

#{{{
def  make_lat_lon_tile(lat, lon, lat_d, lon_d):
    x_l = lon - lon_d
    x_r = lon + lon_d
    y_t = lat + lat_d
    y_b = lat - lat_d

    return Polygon( ((x_l, y_t), (x_r, y_t), (x_r,y_b), (x_l, y_b)) )

def get_windows(header, window):

    last_day = header[0].split(' ')[1]
    d = [(0,last_day)]
    header_i = 0
    D = []

    for field in header:
        state,day,date,time = field.split(' ')

        if day != last_day:
            #d.append((header_i,last_day))
            d.append( Window(index=header_i, dayofweek=last_day))
            last_day = day
            if d[1][0] - d[0][0] == window:
                D.append(d)
            #d = [(header_i,day)]
            d = [Window(index=header_i, dayofweek=day)]
        header_i += 1

    W = []
    for i in range(len(D)- window + 1):
        curr = D[i:i+window] #points in the current window
        W.append((curr[0][0],curr[-1][1]))

    return W
#}}}


#{{{parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser()

parser.add_argument('-i',
                    dest='infile',
                    required=True,
                    help='Output file name')

parser.add_argument('-o',
                    dest='outfile',
                    help='Output file name')

parser.add_argument('--shapename',
                    dest='shapename',
                    help='Shape to plot')

parser.add_argument('-w',
                    '--window',
                    dest='window',
                    default=3,
                    help='Window size in days')

args = parser.parse_args()
#}}}

input_file = csv.reader(open(args.infile), delimiter='\t')
header = None
crisis_header = None
L = []
B = []
C = []
row_i = 1
windows = None
for row in input_file:
    if header is None:
        header = row
        crisis_header = row[crisis_range['start']:]
        windows = get_windows(crisis_header, args.window)
        continue

    if args.shapename is None or row[shape_i] == args.shapename:

        L.append((float(row[1]),float(row[2])))
        
        b = row[baseline_range['start']:baseline_range['end']]
        b = [float(x) for x in b]

        c = row[crisis_range['start']:]
        c = [float(x) for x in c]

        B.append([float(x) for x in b])
        C.append([float(x) for x in c])

        row_i += 1

# get distance between points
lats = {}
lons = {}
for lat,lon in L:
    if lat not in lats:
        lats[lat] = []
    if lon not in lons:
        lons[lon] = []
    lats[lat].append(float(lon))
    lons[lon].append(float(lat))

d = []
for lon in lons:
    s_lats = sorted(lons[lon])
    d_curr = []
    if len(s_lats) > 10:
        for i in range(1,len(s_lats)):
            d_curr.append(abs(s_lats[i-1] - s_lats[i]))
        d.append(min(d_curr))
lat_u = np.mean(d)
lat_d = lat_u/2

d = []
for lat in lats:
    s_lons = sorted(lats[lat])
    d_curr = []
    if len(s_lons) > 10:
        for i in range(1,len(s_lons)):
            d_curr.append(abs(s_lons[i-1] - s_lons[i]))
        d.append(min(d_curr))
lon_u = np.mean(d)
lon_d = lon_u/2

# get a model for the stdev based on size
C_stats = []

for c in C:
    C_stats.append( ( np.mean(c), np.std(c) ) )

model = LinearRegression()
x=[[c[0]] for c in C_stats]
y=[[c[1]] for c in C_stats]
model.fit(x,y)


geometry =  []
data = []

for i in range(len(C)):
    c = C[i]

    dow_stats = {}

    for w in windows:
        start_day = w[0].dayofweek
        start = w[0].index
        end = w[1].index
        if start_day not in dow_stats:
            dow_stats[start_day] = []

        curr = c[start:end] 
        mean = np.mean(curr)
        stdev = np.std(curr)

        dow_stats[start_day].append((mean,stdev))
    
    last_w = windows[-1]
    start_day = last_w[0].dayofweek
    start = last_w[0].index
    end = last_w[1].index

    curr = c[start:end] 
    mean = np.mean(curr)
    stdev = model.predict([[mean]])[0][0]

    z = (mean - dow_stats[start_day][0][0] ) / stdev

    lat = L[i][0]
    lon = L[i][1]
    data.append( [z] )
    tile = make_lat_lon_tile(float(lat), float(lon), lat_d, lon_d)
    geometry.append(tile)

df = pd.DataFrame(data, columns = ['z'])
crs = {'init': 'epsg:4326'}
gdf = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)

os.mkdir(args.outfile)
gdf.to_file(driver='ESRI Shapefile', filename=args.outfile)
shutil.make_archive(args.outfile, 'zip', args.outfile)

