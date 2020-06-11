import  sys
import numpy as np
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import argparse
import csv
import math

shape_i = 0
baseline_range = {'start':3, 'end':24}
crisis_range = {'start':24}

def shortest_distance(x1, y1, a, b, c):
    d = abs((a * x1 + b * y1 + c)) / (math.sqrt(a * a + b * b))
    return(d)

def draw_arrow(ax, x1, y1, x2, y2):
    ax.arrow( x1, y1, x2 - x1, y2 - y1,
             lw = 0.25,
             head_width=0.02,
             head_length=0.02,
             color='black',
             alpha=0.25)

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

def clear_ax(ax, x_label, y_label):
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().set_visible(True)
    ax.get_yaxis().set_visible(True)
    ax.yaxis.set_tick_params(width=0.25, labelsize=5)
    ax.xaxis.set_tick_params(width=0.25, labelsize=5)

    ax.set_xlabel(x_label, fontsize=6)
    ax.set_ylabel(y_label, fontsize=6)

    ax.axvline(x=0,lw=0.25, c='black')
    ax.axhline(y=0,lw=0.25, c='black')

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


parser.add_argument("--x_min", dest="x_min", type=float)
parser.add_argument("--x_max", dest="x_max", type=float)
parser.add_argument("--y_min", dest="y_min", type=float)
parser.add_argument("--y_max", dest="y_max", type=float)

parser.add_argument("--x_axis",
                    dest="x_axis_i",
                    type=int,
                    required=True,
                    help="Week for x-axsis ( 0 is baseline )")

parser.add_argument("--y_axis",
                    dest="y_axis_i",
                    type=int,
                    required=True,
                    help="Week for y-axsis ( 0 is baseline )")

parser.add_argument("-x",
                    "--xlabel",
                    dest="x_label",
                    required=True,
                    help="X axis label")

parser.add_argument("-y",
                    "--ylabel",
                    dest="y_label",
                    required=True,
                    help="Y axis label")

parser.add_argument('--alpha',
                    dest='alpha',
                    default=0.5,
                    help='file name')

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
BD = []
B = []
C = []
loc = []
for row in input_file:
    if header is None:
        header = row
        continue

    if args.shapename is None or row[shape_i] == args.shapename:
        loc.append(row[1:3])

        b = row[baseline_range['start']:baseline_range['end']]
        b = [float(x) for x in b]

        BD.append(np.sqrt(np.mean(b)))
        #BD.append(np.mean(b))

        c = row[crisis_range['start']:]
        c = [float(x) for x in c]

        B.append([float(x) for x in b])
        C.append([float(x) for x in c])

fig = plt.figure(figsize=(args.width,args.height), dpi=300)

rows=1
cols=1

outer_grid = gridspec.GridSpec(rows, cols, wspace=0.0, hspace=0.1)

inner_grid = gridspec.GridSpecFromSubplotSpec(\
        1,
        1,
        subplot_spec=outer_grid[0],
        wspace=0.0,
        hspace=0.0)

ax = fig.add_subplot(inner_grid[0])

X = []
Y = []
for i in range(len(B)):
    b_header = header[baseline_range['start']:baseline_range['end']]
    b_wd_u, b_we_u, b_ws = get_ws(B[i], b_header)


    week_i = 0
    c_wss = []
    for j in range(crisis_range['start'],len(header),21):
        c_header = header[j:j+21]
        if len(c_header) < 21:
            continue
        c_wd_u, c_we_u, c_ws = get_ws(C[i][week_i*21:week_i*21+21], c_header)
        c_wss.append(c_ws)
        week_i += 1

    v = [b_ws] + c_wss

    X.append(v[args.x_axis_i])
    Y.append(v[args.y_axis_i])

    #draw_arrow(ax, c_wss[0], c_wss[1], c_wss[1], c_wss[2])

D = []
for i in range(len(X)):
    D.append(shortest_distance(X[i], Y[i], 1, -1, 0))

max_d = max(D)
sum_sqr = sum([d**2 for d in D])

alphas = [ (d/max_d)**2 for d in D ]

rgba_colors = np.zeros((len(Y),4))
rgba_colors[:,0] = 31.0/255.0
rgba_colors[:,1] = 119.0/255.0
rgba_colors[:,2] = 180.0/255.0
rgba_colors[:, 3] = alphas

#ax.scatter(X,Y,s=BD,linewidths=0.5,color=rgba_colors)#alpha=args.alpha)
ax.scatter(X,Y,s=BD,linewidths=0.5,color=rgba_colors)#alpha=args.alpha)

if args.y_min and args.y_max:
    ax.set_ylim((args.y_min,args.y_max))
if args.x_min and args.x_max:
    ax.set_xlim((args.x_min,args.x_max))

print(ax.get_ylim(), ax.get_xlim())

x_vals = np.array(ax.get_xlim())
b=0
m=1
y_vals = m * x_vals + b
ax.plot(x_vals,y_vals, ls="--", lw=0.5, c='red')

ax.text(ax.get_xlim()[1],
        ax.get_ylim()[0],
        str(round(sum_sqr,3)),
        fontsize=6,
        verticalalignment='bottom',
        horizontalalignment='right')



clear_ax(ax, args.x_label, args.y_label)
ax.ticklabel_format(useOffset=False)

plt.savefig(args.outfile,bbox_inches='tight')
