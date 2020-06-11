import  sys
import numpy as np
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import argparse
import csv
from operator import add
import datetime

shape_i = 0
baseline_range = {'start':3, 'end':24}
crisis_range = {'start':24}


#{{{ def get_datetime(ymd_str):
def get_datetime(ymd_str):
    y,m,d = [int(x) for x in ymd_str.split('-')]
    return datetime.datetime(year=y, month=m, day=d)
#}}}
    
#{{{def clear_ax(ax):
def clear_ax(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(True)
    ax.yaxis.set_tick_params(width=0.0, labelsize=4)
    ax.xaxis.set_tick_params(width=0.0, labelsize=4)
#}}}

#{{{ def shade_weekends(ax, header):
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
#}}}

#{{{def label_days(ax, header):
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
#}}}

#{{{def show_legend(ax):
def show_legend(ax):
    ax.legend(frameon=False,
              loc='lower left',
              bbox_to_anchor=(0,1),
              fontsize=4,
              ncol=2)
#}}}

#{{{def mark_weeks(ax, header):
def mark_weeks(ax, header):

    week_start = None

    x_i = 0

    for field in header:
        timepoint = field.split(' ')

        if timepoint[0] == 'crisis':
            if week_start is None:
                week_start = (timepoint[1], timepoint[3])
                ax.axvline(x=x_i, ls='--', c='gray', lw=0.5)
            elif timepoint[1] == week_start[0] \
                    and timepoint[3] == week_start[1]:
                ax.axvline(x=x_i, ls='--', c='gray', lw=0.5)
        x_i+=1
#}}}

#{{{parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser()

parser.add_argument('-i',
                    dest='infile',
                    required=True,
                    help='Output file name')

parser.add_argument('-o',
                    dest='outfile',
                    required=True,
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

parser.add_argument('--color',
                    dest='color',
                    default='tab:blue',
                    help='Line color (default tab:blue)')

parser.add_argument('--start_date',
                    dest='start_date',
                    required=True,
                    help='Start of date range (YYYY-MM-DD)')

parser.add_argument('--end_date',
                    dest='end_date',
                    required=True,
                    help='End of date range (YYYY-MM-DD)')

parser.add_argument('--baseline',
                    dest='baseline',
                    action='store_true',
                    help='Plot baseline values')

args = parser.parse_args()
#}}}


input_file = csv.reader(open(args.infile), delimiter='\t')
header = None
crisis_header = None
baseline_header = None
B = []
C = []
loc = []
for row in input_file:
    if header is None:
        header = row
        baseline_header = row[baseline_range['start']:baseline_range['end']]
        crisis_header = row[crisis_range['start']:]
        continue

    if args.shapename and row[shape_i] == args.shapename:

        loc.append(row[1:3])
         
        b = row[baseline_range['start']:baseline_range['end']]
        c = row[crisis_range['start']:]

        B.append([float(x) for x in b])
        C.append([float(x) for x in c])

start_date = get_datetime(args.start_date)
end_date = get_datetime(args.end_date)

range_start = None
range_end = None
in_range = []
for i in range(len(crisis_header)):
    t,dow,date,time = crisis_header[i].split()
    curr = get_datetime(date)
    if curr >= start_date and curr <= end_date:
        in_range.append(i)
date_rate_idx = (min(in_range), max(in_range))

to_plot = [0]

if args.n:
    if args.n == '-1':
        to_plot = range(len(B))
    else:
        to_plot = [int(x)-1 for x in args.n.split(',')]


fig = plt.figure(figsize=(args.width,args.height), dpi=300)

rows=1
cols=1

outer_grid = gridspec.GridSpec(rows, cols, wspace=0.0, hspace=0.1)

T_C = None
T_B = None
for i in to_plot:
    curr = [c for c in C[i][date_rate_idx[0]:date_rate_idx[1]+1]]
    if not T_C:
        T_C = curr
    else:
        T_C = list( map(add, T_C, curr) )

    if not T_B:
        T_B = [b for b in B[i]]
    else:
        T_B = list( map(add, T_B, B[i]) )

inner_grid = gridspec.GridSpecFromSubplotSpec(\
        1,
        1,
        subplot_spec=outer_grid[0],
        wspace=0.0,
        hspace=0.0)

ax = fig.add_subplot(inner_grid[0])

start_x = 0
if args.baseline:
    ax.plot(range(len(T_B)),
            T_B,
            lw=0.5,
            label='Baseline')
    start_x = len(T_B)

ax.plot(range(start_x,start_x + len(T_C)),
        T_C,
        lw=0.5,
        label='Current')

ax.set_ylabel('Density', fontsize=4)

plot_header = crisis_header[date_rate_idx[0]:date_rate_idx[1]+1]

if args.baseline:
    plot_header = baseline_header + plot_header


clear_ax(ax)
shade_weekends(ax, plot_header)
#mark_weeks(ax, crisis_header[date_rate_idx[0]:date_rate_idx[1]+1])
ax.set_xlim((0,start_x + len(T_C)))
label_days(ax, plot_header)
show_legend(ax)


plt.savefig(args.outfile,bbox_inches='tight')
