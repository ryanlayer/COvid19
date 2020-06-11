import  sys
import numpy as np
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import argparse
import csv
import fb
import collections
from sklearn.linear_model import LinearRegression

Window = collections.namedtuple('Window', 'index dayofweek')

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

def show_legend(fig):
    fig.legend(frameon=False,
               loc='lower left',
               bbox_to_anchor=(0.075, 1.55),
               fontsize=4,
               ncol=4)


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

parser.add_argument('--ymin',
                    dest='ymin',
                    type=float,
                    default=-2)

parser.add_argument('--ymax',
                    dest='ymax',
                    type=float,
                    default=2)

args = parser.parse_args()


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

        L.append(row[0:3])
        
        b = row[baseline_range['start']:baseline_range['end']]
        b = [float(x) for x in b]

        c = row[crisis_range['start']:]
        c = [float(x) for x in c]

        B.append([float(x) for x in b])
        C.append([float(x) for x in c])

        row_i += 1

# get a model for the stdev based on size
C_stats = []

for c in C:
    C_stats.append( ( np.mean(c), np.std(c) ) )

model = LinearRegression()
x=[[c[0]] for c in C_stats]
y=[[c[1]] for c in C_stats]
model.fit(x,y)

C_plot_stats = []

c_i = 0
for c in C:
    
    c_stats = {}

    dow_stats = {}

    for w in windows:
        start_day = w[0][1]
        start = w[0][0]
        end = w[1][0]
        if start_day not in dow_stats:
            dow_stats[start_day] = []

        curr = c[start:end] 
        mean = np.mean(curr)
        stdev = np.std(curr)

        dow_stats[start_day].append((mean,stdev,start,end))

    c_stats['dow_stats'] = dow_stats

    Z_x = []
    Z_y = []

    window_means = [] 
    window_stdevs = [] 

    for w in windows:
        start_day = w[0][1]
        start = w[0][0]
        end = w[1][0]

        curr = c[start:end] 
        mean = np.mean(curr)
        stdev = model.predict([[mean]])[0][0]

        window_means.append(mean)
        window_stdevs.append(stdev)

        z = (mean - dow_stats[start_day][0][0] ) / stdev
        Z_x.append((start+end)/2)
        Z_y.append(z)

    c_stats['window_means'] = window_means
    c_stats['window_stdevs'] = window_stdevs

    c_stats['Z_x'] = Z_x
    c_stats['Z_y'] = Z_y

    if not args.quiet:
        O = [c_i] + L[c_i] + [np.mean(B[c_i]),Z_y[-1]]
        print('\t'.join([str(o) for o in O]))

    C_plot_stats.append(c_stats)
    c_i += 1

if args.outfile is None:
    sys.exit(0)

to_plot = [0]
if args.n:
    if args.n == '-1':
        to_plot = range(len(B))
    else:
        to_plot = [int(x) for x in args.n.split(',')]


fig = plt.figure(figsize=(args.width,args.height), dpi=300)

rows=len(to_plot)
cols=1

outer_grid = gridspec.GridSpec(rows, cols, wspace=0.0, hspace=0.1)


print(to_plot)
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
            label='Current',
            alpha=0.5)

    ax2 = ax.twinx()

    dow_stats = C_plot_stats[i]['dow_stats']

    #current
    start_day = windows[-1][0][1]
    start = windows[-1][0][0]
    end = windows[-1][1][0]

    mean = C_plot_stats[i]['window_means'][-1]
    stdev = C_plot_stats[i]['window_stdevs'][-1]

    c='black'
    point1 = [(start+end)/2, mean + stdev]
    point2 = [(start+end)/2, mean - stdev]
    x_values = [point1[0], point2[0]]
    y_values = [point1[1], point2[1]]
    ax.plot(x_values, y_values, c=c, lw=0.5)

    c='black'
    point1 = [start-0.5, mean]
    point2 = [end-1+0.5, mean]
    x_values = [point1[0], point2[0]]
    y_values = [point1[1], point2[1]]
    ax.plot(x_values, y_values, c=c, lw=0.5, label='Curr mean')

    c='red'
    bl_start = dow_stats[start_day][0][2]
    bl_end = dow_stats[start_day][0][3]
    bl_point1 = [bl_start-0.5, dow_stats[start_day][0][0]]
    bl_point2 = [bl_end-1+0.5, dow_stats[start_day][0][0]]
    x_values = [bl_point1[0], bl_point2[0]]
    y_values = [bl_point1[1], bl_point2[1]]
    ax.plot(x_values, y_values, c=c, lw=0.5, label='Week 1 mean')

    x_values = [bl_point1[0], point2[0]]
    y_values = [bl_point1[1], bl_point2[1]]
    ax.plot(x_values, y_values, c=c, ls='--', alpha = 0.5, lw=0.5)

    hs_x = [C_plot_stats[i]['Z_x'][-1]]
    hs_y = [C_plot_stats[i]['Z_y'][-1]]

    ax2.scatter(hs_x,hs_y,2,c='blue', label='Hot-spot score')
    ax2.set_ylim([args.ymin,args.ymax])
    ax2.set_ylabel('Hot-spot', fontsize=4)

    ax.set_ylabel('Density', fontsize=4)

    clear_ax(ax2)
    clear_ax(ax)
    shade_weekends(ax, crisis_header)

    mark_weeks(ax, crisis_header)

    ax.set_xlim((0,len(C[i])))

    if i == to_plot[0]:
        show_legend(fig)

    if i == to_plot[-1]:
        label_days(ax, crisis_header)

    plot_i += 1

plt.savefig(args.outfile,bbox_inches='tight')
