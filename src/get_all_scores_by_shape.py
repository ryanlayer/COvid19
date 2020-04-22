import sqlite3
import sys
import numpy as np
from optparse import OptionParser
import datetime
from sklearn.linear_model import LinearRegression
import math


import geopandas as gpd
import fb

parser = OptionParser()

parser.add_option("--db",
                  dest="db",
                  help="Path to database file")

parser.add_option("--shapefile",
                  dest="shapefile",
                  help="Path to shapefile")

parser.add_option("--shapename",
                  dest="shapename",
                  help="Shapefile column name")

(options, args) = parser.parse_args()
if not options.db:
    parser.error('DB file not given')

D = fb.get_db_fields(options.db, ['n_baseline','n_crisis'] )

dates_times = {}
for pos in D:
    for date in D[pos]:
        for time in D[pos][date]:
            if (date,time) not in dates_times:
                dates_times[(date,time)] = 1

dates_times = sorted(dates_times.keys())

def get_vals(D, pos, dates_times, field):
    vals  = []
    for date,time in dates_times:
        if date not in D[pos]:
            return None
        if time not in D[pos][date]:
            return None

        vals.append(float(D[pos][date][time][field]))
 
    return vals

header = ['shape','lat','lon']
for date,time in dates_times[:21]:
    header.append(' '.join(['baseline',
                            fb.day_of_week(date),
                            time]))
for date,time in dates_times:
    header.append(' '.join(['crisis',
                            fb.day_of_week(date),
                            date,
                            time]))

print('\t'.join(header))

gdf = gpd.read_file(options.shapefile)

for pos in D:
    lat = float(pos[0])
    lon = float(pos[1])

    crisis = get_vals(D,pos,dates_times,'n_crisis')
    baseline = get_vals(D,pos,dates_times,'n_baseline')
    if crisis is not  None:
        shape = fb.get_bounding_shape(lat, lon, gdf, options.shapename)
        if shape is not None:
            o = [shape,lat,lon] + baseline[:21]  + crisis
            print('\t'.join([str(x) for x in o]))
