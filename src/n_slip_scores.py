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

def get_windows(header, window):

    last_day = header[0].split(' ')[1]
    d = [(0,last_day)]
    header_i = 0
    D = []

    for field in header:
        state,day,date,time = field.split(' ')

        if day != last_day:
            d.append((header_i,last_day))
            last_day = day
            if d[1][0] - d[0][0] == window:
                D.append(d)
            d = [(header_i,day)]
        header_i += 1

    W = []
    for i in range(len(D)- window + 1):
        curr = D[i:i+window]
        W.append((curr[0][0],curr[-1][1]))

    return W


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

def plot_ss(ax, header, mean, start_x):

    curr_x = start_x

    for i in range(len(header)):
        c='black'
        point1 = [curr_x - 0.5, mean]
        point2 = [curr_x + 0.5, mean]
        x_values = [point1[0], point2[0]]
        y_values = [point1[1], point2[1]]
        ax.plot(x_values, y_values, c=c, lw=0.5)
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
                ax.axvline(x=x_i - 0.5, ls='--', c='gray', lw=0.5)
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

parser.add_argument('-q',
                    '--quiet',
                    dest='quiet',
                    action='store_true',
                    default=False,
                    help='Do not print scoress')

parser.add_argument('-w',
                    '--window',
                    dest='window',
                    default=3,
                    help='Window size in days')


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
B = []
C = []
M = []
row_i = 1
windows = None
for row in input_file:
    if header is None:
        header = row
        crisis_header = row[crisis_range['start']:]
        windows = get_windows(crisis_header, args.window)
        continue


    if args.shapename is None or row[shape_i] == args.shapename:

        b = row[baseline_range['start']:baseline_range['end']]
        b = [float(x) for x in b]

        baseline_mean = get_week_means(b)

        c = row[crisis_range['start']:]
        c = [float(x) for x in c]

        crisis_week_means = get_week_means(c)

        means = baseline_mean + crisis_week_means

        M.append(means)

        o = [row_i] + row[0:3]
        for i in range(1,len(means)):
            o.append(np.log2(means[i]/means[i-1]))

        if not args.quiet:
            print('\t'.join([str(x) for x in o]))

        B.append([float(x) for x in b])
        C.append([float(x) for x in c])

        row_i += 1

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

    ax.plot([],[])
    ax.plot(range(len(C[i])),
            C[i],
            lw=0.5,
            label='current',
            alpha=0.5)

    ax2 = ax.twinx()

    window_stats = []

    dow_stats = {}
    for w in windows:
        start_day = w[0][1]
        start = w[0][0]
        end = w[1][0]
        if start_day not in dow_stats:
            dow_stats[start_day] = []

        curr =C[i][start:end] 
        mean = np.mean(curr)
        stdev = np.std(curr)

        dow_stats[start_day].append((mean,stdev))

    Z_x = []
    Z_y = []

    for w in windows:
        start_day = w[0][1]
        start = w[0][0]
        end = w[1][0]

        curr =C[i][start:end] 
        mean = np.mean(curr)

        for other_mean,stdev in dow_stats[start_day]:
            c='black'
            #point1 = [start-0.5, other_mean]
            #point2 = [end-1+0.5, other_mean]
            #x_values = [point1[0], point2[0]]
            #y_values = [point1[1], point2[1]]
            #ax.plot(x_values, y_values, c=c, lw=0.5)
            ax.plot([(start+end)/2],[other_mean],'o',c=c,markersize=0.5)

        c='black'
        point1 = [(start+end)/2, max([x[0] for x in dow_stats[start_day]])]
        point2 = [(start+end)/2, min([x[0] for x in dow_stats[start_day]])]
        x_values = [point1[0], point2[0]]
        y_values = [point1[1], point2[1]]
        ax.plot(x_values, y_values, c=c, lw=0.5)

        c='black'
        point1 = [start-0.5, mean]
        point2 = [end-1+0.5, mean]
        x_values = [point1[0], point2[0]]
        y_values = [point1[1], point2[1]]
        ax.plot(x_values, y_values, c=c, lw=0.5)

        c = 'red'
        dow_mean = np.mean( [ x[0] for x in dow_stats[start_day]] )
        dow_std = np.std( [ x[0] for x in dow_stats[start_day]] )
        z = (mean - dow_mean) / dow_std
        Z_x.append((start+end)/2)
        Z_y.append(z)
        #ax2.plot([(start+end)/2],[z],'o',marker='x',c=c,markersize=1)
    ax2.plot(Z_x,Z_y,'-o',marker='x',c=c,markersize=1)

    print(Z_y[-1] - Z_y[-2])

#    week_i = 0
#    curr_x = 0
#    for j in range(0,len(crisis_header),21):
#        c_header = crisis_header[j:j+21]
#        c_vals = C[i][j:j+21]
#        if len(c_header) < 21:
#            continue
#        curr_x = plot_ss(ax, c_header, np.mean(c_vals),curr_x)
#        week_i += 1

    ax.set_ylabel('Density', fontsize=4)

    clear_ax(ax2)
    clear_ax(ax)
    shade_weekends(ax, crisis_header)


    mark_weeks(ax, crisis_header)

    if i == to_plot[0]:
        show_legend(ax)

    if i == to_plot[-1]:
        label_days(ax, crisis_header)

    plot_i += 1

plt.savefig(args.outfile,bbox_inches='tight')
