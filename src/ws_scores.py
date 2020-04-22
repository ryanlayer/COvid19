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

def get_ws(scores, header):
    wd = []
    we = []
    for i in range(len(header)):
        timepoint = header[i].split(' ')
        day = timepoint[1]
        time = timepoint[-1]
        if day in ['Saturday', 'Sunday']:
            we.append(scores[i])
        else:
            wd.append(scores[i])

    wd_u = np.mean(wd)
    we_u = np.mean(we)
    ws = np.log2(wd_u/we_u)

    return wd_u,we_u,ws

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
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(True)
    ax.yaxis.set_tick_params(width=0.0, labelsize=4)
    ax.xaxis.set_tick_params(width=0.0, labelsize=4)

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
                ax.axvline(x=x_i, ls='--', c='gray', lw=0.5)
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
B = []
C = []
loc = []
i = 1
for row in input_file:
    if header is None:
        header = row
        continue

    if args.shapename is None or row[shape_i] == args.shapename:

        loc.append(row[1:3])

         
        b = row[baseline_range['start']:baseline_range['end']]
        b = [float(x) for x in b]

        b_header = header[baseline_range['start']:baseline_range['end']]
        b_wd_u, b_we_u, b_ws = get_ws(b, b_header)

        O = [i] + row[0:3] + [b_ws]

        c = row[crisis_range['start']:]
        c = [float(x) for x in c]

        week_i = 0
        for j in range(crisis_range['start'],len(header),21):
            c_header = header[j:j+21]
            if len(c_header) < 21:
                continue
            c_wd_u, c_we_u, c_ws = get_ws(c[week_i*21:week_i*21+21], c_header)
            O.append(c_ws)
            week_i += 1

        print('\t'.join([str(o) for o in O]))


        B.append([float(x) for x in b])
        C.append([float(x) for x in c])

        i += 1

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
            1,
            1,
            subplot_spec=outer_grid[plot_i],
            wspace=0.0,
            hspace=0.0)

    ax = fig.add_subplot(inner_grid[0])

    ax.plot(range(len(B[i])),
            B[i],
            lw=0.5,
            label='baseline')

    b_header = header[baseline_range['start']:baseline_range['end']]
    b_wd_u, b_we_u, b_ws = get_ws(B[i], b_header)
    curr_x = 0
    curr_x = plot_ws(ax, b_header, b_wd_u, b_we_u, b_ws, curr_x)

    ax.plot(range(len(B[i]), len(B[i]) + len(C[i])),
            C[i],
            lw=0.5,
            label='current')

    week_i = 0
    for j in range(crisis_range['start'],len(header),21):
        c_header = header[j:j+21]
        if len(c_header) < 21:
            continue
        c_wd_u, c_we_u, c_ws = get_ws(C[i][week_i*21:week_i*21+21], c_header)
        curr_x = plot_ws(ax, c_header, c_wd_u, c_we_u, c_ws, curr_x)
        week_i += 1


    ax.set_ylabel('Density', fontsize=4)

    clear_ax(ax)
    shade_weekends(ax, header)


    mark_weeks(ax, header)

    if i == to_plot[0]:
        show_legend(ax)

    if i == to_plot[-1]:
        label_days(ax, header)

    plot_i += 1

plt.savefig(args.outfile,bbox_inches='tight')
