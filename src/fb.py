import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point
from geopandas.tools import sjoin
import sqlite3
#from datetime import datetime, timezone
import datetime

def weighted_sum(vals, weights):
    r = 0.0
    for i in range(len(vals)):
        r += vals[i] * weights[i]
    return r/sum(weights)

def scatter(ax, X, Y, exp, markersize, y_min, y_max):
    alphas = [abs(y) for y in Y]
    max_a = max(alphas)

    if y_min and y_max:
        max_y = max(abs(y_min),abs(y_max))
        alphas = [ (a/max_y)**exp for a in alphas ]
    else:
        alphas = [ (a/max_a)**exp for a in alphas ]

    rgba_colors = np.zeros((len(Y),4))
    rgba_colors[:,0] = 31.0/255.0
    rgba_colors[:,1] = 119.0/255.0
    rgba_colors[:,2] = 180.0/255.0
    rgba_colors[:, 3] = alphas

    ax.scatter(X,
               Y,
               s=markersize,
               linewidths=0.5,
               color=rgba_colors)
    #ax.set_xscale('log')

    ws = weighted_sum(Y, X)
    ax.axhline(y=ws,ls='-', lw=0.5, c='red')
    ax.text(ax.get_xlim()[0],
            ws,
            str(round(ws,3)),
            fontsize=6,
            verticalalignment='top',
            horizontalalignment='left')

    ax.axhline(y=0, lw=0.25, c='black')


    if y_min and y_max:
        ax.set_ylim( ( y_min , y_max) )


def day_of_week(date):
    year,month,day = date.split('-')
    ans = datetime.date(int(year), int(month), int(day))
    day_of_week = ans.strftime("%A")
    return day_of_week

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

def switch_tz(date, time):
    year, month, day = date.split('-')
    hour = time[:2]
    minute = time[2:]

    utc = datetime.datetime( int(year), int(month), int(day), int(hour), int(minute) )
    mnt = utc_to_local(utc)
    return ('-'.join([mnt.strftime('%Y'), mnt.strftime('%m'), mnt.strftime('%d')]) , \
            mnt.strftime('%H') + mnt.strftime('%M'))


def get_bounding_shape(lat, lon, gdf, name):
    h=pd.DataFrame({'Lat':[lat], 'Lon':[lon]})
    geometry = [Point(xy) for xy in zip([lon], [lat])]
    hg = gpd.GeoDataFrame(h, geometry=geometry)
    hg.crs = {'init' :'epsg:4326'}
    hg_1 = hg.to_crs(gdf.crs)
    r = sjoin(gdf,hg_1)
    if r.empty:
        return None
    else:
        return r[name].tolist()[0]


co_county_sf = '/Users/rl/scratch/covid-19/facebook/co_counties/co_counties.shp'
def get_co_county(lat, lon, gdf=None):
    if gdf is None:
        gdf = gpd.read_file(co_county_sf)
    return get_bounding_shape(lat, lon, gdf, 'NAME')


boulder_county_zone_sf = '/Users/rl/scratch/covid-19/facebook/boulder_county_zoning/Zoning__Zoning_Districts.shp'
def get_boulder_co_zone(lat, lon, gdf=None):
    if gdf is None:
        gdf = gpd.read_file(boulder_county_zone_sf)
    return get_bounding_shape(lat, lon, gdf, 'ZONEDESC')

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_db_fields(db_path, fields, local_tz=True):

    c = sqlite3.connect(db_path)
    c.row_factory = dict_factory

    D = {}
    dates = []

    #for row in c.execute('SELECT * FROM pop_tile'):
    for row in c.execute('SELECT * FROM pop_tile WHERE n_crisis != "\\N"'):
        lat = row['lat']
        lon = row['lon']
        if (lat,lon) not  in D:
            D[(lat,lon)] = {}

        date, time = row['date_time'].split()

        if local_tz:
            date, time = switch_tz(date,time)

        if date not in dates:
            dates.append(date)

        if date not in D[(lat,lon)]:
            D[(lat,lon)][date] = {}

        d = {}
        for field in fields:
            d[field] = row[field]

        D[(lat,lon)][date][time] = d

    return D
