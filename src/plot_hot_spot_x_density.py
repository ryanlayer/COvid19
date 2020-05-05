import  sys
import numpy as np
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import argparse
import csv
import collections
from sklearn.linear_model import LinearRegression

Window = collections.namedtuple('Window', 'index dayofweek')

shape_i = 0
baseline_range = {'start':3, 'end':24}
crisis_range = {'start':24}

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


def clear_ax(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().set_visible(True)
    ax.get_yaxis().set_visible(True)
    ax.yaxis.set_tick_params(width=0.0, labelsize=6)
    ax.xaxis.set_tick_params(width=0.0, labelsize=6)

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

c_i = 0
X = []
Y = []
for c in C:

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
    
    x = np.mean(B[c_i])

    last_w = windows[-1]
    start_day = last_w[0].dayofweek
    start = last_w[0].index
    end = last_w[1].index

    curr = c[start:end] 
    mean = np.mean(curr)
    stdev = model.predict([[mean]])[0][0]

    z = (mean - dow_stats[start_day][0][0] ) / stdev

    X.append(x)
    Y.append(z)

    c_i+=1

ax.scatter(X,Y,alpha=args.alpha)

mean = np.mean(Y)

ax.axhline(y=mean, ls='-', lw=0.5, c='red')

ax.text(ax.get_xlim()[1],
        mean,
        str(round(mean,2)),
        fontsize=8,
        verticalalignment='top',
        horizontalalignment='right')

ax.axhline(y=0, lw=0.25, c='black')

ax.set_ylabel(args.y_label, fontsize=7)
ax.set_xlabel(args.x_label, fontsize=7)

if args.y_min and args.y_max:
    ax.set_ylim( ( args.y_min ,args.y_max) )

clear_ax(ax)

plt.savefig(args.outfile,bbox_inches='tight')
