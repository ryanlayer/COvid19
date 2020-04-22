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

    for field in header:
        timepoint = field.split(' ')

        if timepoint[0] == 'crisis':
            if week_start is None:
                week_start = (timepoint[1], timepoint[3])
                #ax.axvline(x=x_i - 0.5, ls='--', c='gray', lw=0.5)
            if timepoint[1] == week_start[0] \
                    and timepoint[3] == week_start[1]:
                ax.axvline(x=x_i, ls='--', c='gray', lw=0.5)
                ax.text(x_i,
                        ax.get_ylim()[1],
                        timepoint[2],
                        verticalalignment='top',
                        fontsize=4)
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

parser.add_argument('-t',
                    dest='titel',
                    help='Plot title')

parser.add_argument('--shapename',
                    dest='shapename',
                    help='Shape to plot')

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

parser.add_argument('--title',
                    dest='title',
                    help='Plot title')



args = parser.parse_args()


input_file = csv.reader(open(args.infile), delimiter='\t')
header = None
crisis_header = None
baseline_header = None
B = []
C = []
for row in input_file:
    if header is None:
        header = row
        baseline_header = row[baseline_range['start']:baseline_range['end']]
        crisis_header = row[crisis_range['start']:]
        continue

    if args.shapename is None or row[shape_i] == args.shapename:

        b = row[baseline_range['start']:baseline_range['end']]
        b = [float(x) for x in b]
        B.append(b)

        c = row[crisis_range['start']:]
        c = [float(x) for x in c]
        C.append(c)

if args.outfile is None:
    sys.exit(0)

fig = plt.figure(figsize=(args.width,args.height), dpi=300)

rows=1
cols=1

outer_grid = gridspec.GridSpec(rows, cols, wspace=0.0, hspace=0.0)

inner_grid = gridspec.GridSpecFromSubplotSpec(1,
                                              1,
                                              subplot_spec=outer_grid[0],
                                              wspace=0.0,
                                              hspace=0.0)

ax = fig.add_subplot(inner_grid[0])


ax.axhline(y=0, c='black', lw=0.5)

baseline_mean = np.array([np.mean(b) for b in B])
baseline_mean_norm =  \
    (baseline_mean - np.min(baseline_mean))/ np.max(baseline_mean)

T = []
for i in range(len(C)):
    result_mul = seasonal_decompose(C[i],
                                    period=21,
                                    model='multiplicative',
                                    extrapolate_trend='freq')
    t  = np.array(result_mul.trend)
    t = t - t[0]

    T.append(t)

    c = 'blue'
    alpha = 0.25
    if t[0] < t[-1]:
        c = 'red'
        alpha = 0.5

    ax.plot(range(len(t)),
            t,
            '-',
            lw=baseline_mean_norm[i],
            alpha=alpha,
            c=c)

T_mean = np.average(T, axis=0, weights=baseline_mean_norm)

print('\t'.join([args.shapename] + [str(x) for x in T_mean]))

ax.plot(range(len(T_mean)),
        T_mean,
        '-',
        lw=1,
        c='black')

ax.set_ylabel('Change in density', fontsize=6)

if args.title:
    ax.set_title(args.title)

clear_ax(ax)
shade_weekends(ax, crisis_header)
mark_weeks(ax, crisis_header)
label_days(ax, crisis_header)

plt.savefig(args.outfile,bbox_inches='tight')
