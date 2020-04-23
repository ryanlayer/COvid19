import  sys
import numpy as np
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import argparse
import csv

shape_i = 0
baseline_range = {'start':3, 'end':24}
crisis_range = {'start':24}

#{{{
def get_week_means(scores):
    week_i = 0
    week_means = []
    W = []
    for j in range(0,len(scores),21):
        c_week = scores[j:j+21]
        if len(c_week) < 21:
            continue
        W.append( np.mean(c_week) )
    return W

def plot_ws(ax, header, wd_u, we_u, ws, start_x):

    curr_x = start_x

    for i in range(len(header)):
        timepoint = header[i].split(' ')
        day = timepoint[1]
        time = timepoint[-1]
        score = wd_u
        color = 'black'
        if day in ['Saturday', 'Sunday']:
            score = we_u

        point1 = [curr_x - 0.5, score]
        point2 = [curr_x + 0.5, score]
        x_values = [point1[0], point2[0]]
        y_values = [point1[1], point2[1]]
        ax.plot(x_values, y_values, c=color, lw=0.5)
        curr_x+=1
    return curr_x

def clear_ax(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().set_visible(True)
    ax.get_yaxis().set_visible(True)
    ax.yaxis.set_tick_params(width=0.0, labelsize=6)
    ax.xaxis.set_tick_params(width=0.0, labelsize=6)

def shade_weekends(ax, header):
    x_i = 0
    for field in header[baseline_range['start']:]:
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
    for field in header[baseline_range['start']:]:
        timepoint = field.split(' ')
        if timepoint[-1] == '1000':
            ticks.append(x_i)
            labels.append(timepoint[1][0])
        x_i+=1

    ax.get_xaxis().set_visible(True)
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, fontsize=4)

def show_legend(ax):
    ax.legend(frameon=False,
              loc=0,
              fontsize=4)

def mark_weeks(ax, header):

    week_start = None

    x_i = 0

    for field in header[baseline_range['start']:]:
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

parser.add_argument('--alpha',
                    dest='alpha',
                    type=float,
                    default=0.5,
                    help='Alpha (default 0.5)')

parser.add_argument('--weeks',
                    dest='weeks',
                    default='1,2',
                    help='Weeks CSV (default 1,2)')

parser.add_argument('-x',
                    '--x_label',
                    dest='x_label',
                    help='X-axsis label')

parser.add_argument('-y',
                    '--y_label',
                    dest='y_label',
                    help='Y-axsis label')

parser.add_argument('--y_min',
                    dest='y_min',
                    type=float,
                    help='Min y-axsis bounds')

parser.add_argument('--y_max',
                    dest='y_max',
                    type=float,
                    help='Max y-axsis bounds')

args = parser.parse_args()


input_file = csv.reader(open(args.infile), delimiter='\t')
header = None
S = []
M = []
loc = []
for row in input_file:
    if header is None:
        header = row
        continue

    if args.shapename is None or row[shape_i] == args.shapename:

        loc.append(row[1:3])

        O = row[0:3] 

        b = row[baseline_range['start']:baseline_range['end']]
        b = [float(x) for x in b]

        baseline_mean = get_week_means(b)
        S += baseline_mean

        c = row[crisis_range['start']:]
        c = [float(x) for x in c]

        week_i = 0
        crisis_week_means = get_week_means(c)

        means = baseline_mean + crisis_week_means

        M.append(means)

if args.outfile is None:
    sys.exit(0)

fig = plt.figure(figsize=(args.width,args.height), dpi=300)

rows=1
cols=1

outer_grid = gridspec.GridSpec(rows, cols, wspace=0.0, hspace=0.1)

plot_i = 0

inner_grid = gridspec.GridSpecFromSubplotSpec(\
        1,
        1,
        subplot_spec=outer_grid[plot_i],
        wspace=0.0,
        hspace=0.0)

ax = fig.add_subplot(inner_grid[0])

week1,week2 = [int(i) for i in args.weeks.split(',')]
scores = [np.log2(m[week2]/m[week1]) for m in M]

ax.scatter(S,scores,alpha=args.alpha)

ax.axhline(y=0, lw=0.25, c='black')

ax.set_ylabel(args.y_label, fontsize=7)
ax.set_xlabel(args.x_label, fontsize=7)

if args.y_min and args.y_max:
    ax.set_ylim( ( args.y_min ,args.y_max) )

clear_ax(ax)

plt.savefig(args.outfile,bbox_inches='tight')
