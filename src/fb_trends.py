import  sys
import numpy as np
import pandas as pd
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import argparse
import csv
from fbprophet import Prophet
import plotly

shape_i = 0
baseline_range = {'start':3, 'end':24}
crisis_range = {'start':24}

def clear_ax(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(True)
    ax.yaxis.set_tick_params(width=0.0, labelsize=4)
    ax.xaxis.set_tick_params(width=0.0, labelsize=4)

def shade_weekends(ax, header):
    x_i = 0
    for field in header:
        timepoint = field.split(' ')
        day = timepoint[1]
        time = timepoint[-1]
        alpha = 0.1
        if day in ['Saturday', 'Sunday']:
            alpha = 0.25

        start = x_i - 0.5
        end = x_i + 0.5
        if time == '0200':
            start = x_i - 0.45
        elif time == '1800':
            end = x_i + 0.45

        ax.axvspan(start, end, facecolor = 'gray', alpha = alpha)
        x_i += 1

def label_days(ax, header):
    x_i = 0
    ticks = []
    labels = []
    for field in header:
        timepoint = field.split(' ')
        if timepoint[-1] == '1000':
            ticks.append(x_i)
            labels.append(timepoint[1][0])
        x_i+=1

    ax.get_xaxis().set_visible(True)
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, fontsize=4)

def show_legend(ax, ps):
    labs = [l.get_label() for l in ps]
    #ax.legend(ps, labs, loc=0)
    ax.legend(ps, labs,
              frameon=False,
              bbox_to_anchor=(0.95,0.7),
              loc='center left',
              fontsize=4)

def mark_weeks(ax, header):

    week_start = None

    x_i = 0

    for field in header[baseline_range['start']:]:
        timepoint = field.split(' ')

        if timepoint[0] == 'crisis':
            if week_start is None:
                week_start = (timepoint[1], timepoint[3])
                ax.axvline(x=x_i - 0.5, ls='--', c='gray', lw=0.5)
            elif timepoint[1] == week_start[0] \
                    and timepoint[3] == week_start[1]:
                ax.axvline(x=x_i, ls='--', c='gray', lw=0.5)


        x_i+=1

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

parser.add_argument('-n',
                    dest='n',
                    type=str,
                    help='CSV of records to plot')

parser.add_argument('--width',
                    dest='width',
                    type=float,
                    default=5,
                    help='Plot width (default 5)')

parser.add_argument('--height',
                    dest='height',
                    type=float,
                    default=5,
                    help='Plot height (default 5)')

args = parser.parse_args()


input_file = csv.reader(open(args.infile), delimiter='\t')
header = None
crisis_header = None
crisis_days = []
B = []
C = []
M = []
row_i = 0
for row in input_file:
    if header is None:
        header = row
        crisis_header = row[crisis_range['start']:]
        for h in crisis_header:
            state,day,date,time = h.split()
            time = ':'.join([ time[:2], time[2:], '00'])
            crisis_days.append( date + ' ' + time )
        continue

    if args.shapename is None or row[shape_i] == args.shapename:

#        b = row[baseline_range['start']:baseline_range['end']]
#        b = [float(x) for x in b]

        c = row[crisis_range['start']:]
        c = [float(x) for x in c]
        C.append(c)

#        result_mul = seasonal_decompose(c,
#                                        period=21,
#                                        model='multiplicative',
#                                        extrapolate_trend='freq')
#        s  = result_mul.seasonal
#        t  = result_mul.trend
#
#        O = [row_i] + row[0:3] + [t[0]-t[-1], max(t)-min(t)]
#        print('\t'.join([str(o) for o in O]))
#        row_i += 1

if args.outfile is None:
    sys.exit(0)

to_plot = [0]
if args.n:
    if args.n == '-1':
        to_plot = range(len(B))
    else:
        to_plot = [int(x)-1 for x in args.n.split(',')]


fig = plt.figure(figsize=(args.width,args.height), dpi=300)

rows=len(to_plot)
cols=1

outer_grid = gridspec.GridSpec(rows, cols, wspace=0.0, hspace=0.1)

plot_i = 0
for i in to_plot:
    inner_grid = gridspec.GridSpecFromSubplotSpec(\
            7,
            1,
            subplot_spec=outer_grid[plot_i],
            #height_ratios = [1,1,1,1],
            wspace=0.0,
            hspace=0.1)

    ax = fig.add_subplot(inner_grid[0])
    top_ax = ax

    ax.plot([],[])
    p1 = ax.plot(range(len(C[i])),
            C[i],
            lw=0.5,
            label='current')

    ax.set_ylabel('Density', fontsize=4)
    clear_ax(ax)
    shade_weekends(ax, crisis_header)
    mark_weeks(ax, crisis_header)

  
    result_mul = seasonal_decompose(C[i],
                                     period=21,
                                     model='multiplicative',
                                     extrapolate_trend='freq')
    s  = result_mul.seasonal
    t  = result_mul.trend

    ax = fig.add_subplot(inner_grid[1])
    p2 = ax.plot(range(len(s)), s, lw=0.5, label='season')
    clear_ax(ax)
    shade_weekends(ax, crisis_header)
    mark_weeks(ax, crisis_header)

    ax = fig.add_subplot(inner_grid[2])
    p3 = ax.plot(range(len(t)), t, lw=0.5, c='black', label='trend')
    clear_ax(ax)
    shade_weekends(ax, crisis_header)
    mark_weeks(ax, crisis_header)
    label_days(ax, crisis_header)

######################
    df = pd.DataFrame(data={'ds':crisis_days, 'y':C[i]})
    m = Prophet()

    m.fit(df)
    future = m.make_future_dataframe(periods=0)
    forecast = m.predict(future)
    fb_trend = forecast.trend.tolist()
    fb_weekly = forecast.weekly.tolist()


    ax = fig.add_subplot(inner_grid[3])
    p4 = ax.plot(range(len(fb_weekly)),
                 fb_weekly,
                 lw=0.5,
                 c='red',
                 label='fb trend')
    clear_ax(ax)
    shade_weekends(ax, crisis_header)
    mark_weeks(ax, crisis_header)
    label_days(ax, crisis_header)

    ax = fig.add_subplot(inner_grid[4])
    p4 = ax.plot(range(len(fb_trend)),
                 fb_trend,
                 lw=0.5,
                 c='green',
                 label='fb trend')
    clear_ax(ax)
    shade_weekends(ax, crisis_header)
    mark_weeks(ax, crisis_header)
    label_days(ax, crisis_header)
#######################

    m = Prophet()
    m.add_seasonality(name='hourly',
                      period=7,
                      fourier_order=20)

    m.fit(df)
    future = m.make_future_dataframe(periods=0)
    forecast = m.predict(future)
    fb_trend = forecast.trend.tolist()
    fb_weekly = forecast.weekly.tolist()


    ax = fig.add_subplot(inner_grid[5])
    p4 = ax.plot(range(len(fb_weekly)),
                 fb_weekly,
                 lw=0.5,
                 c='red',
                 label='fb trend')
    clear_ax(ax)
    shade_weekends(ax, crisis_header)
    mark_weeks(ax, crisis_header)
    label_days(ax, crisis_header)

    ax = fig.add_subplot(inner_grid[6])
    p4 = ax.plot(range(len(fb_trend)),
                 fb_trend,
                 lw=0.5,
                 c='green',
                 label='fb trend')
    clear_ax(ax)
    shade_weekends(ax, crisis_header)
    mark_weeks(ax, crisis_header)
    label_days(ax, crisis_header)






    if i == to_plot[0]:
        ps = p1 + p2 + p3
        show_legend(top_ax, ps)


    if i == to_plot[-1]:
        label_days(ax, crisis_header)

    plot_i += 1

plt.savefig(args.outfile,bbox_inches='tight')
