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

def clear_ax(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().set_visible(True)
    ax.get_yaxis().set_visible(True)
    ax.yaxis.set_tick_params(width=0.25, labelsize=5)
    ax.xaxis.set_tick_params(width=0.25, labelsize=5)

    ax.set_xlabel('Baseline ws', fontsize=6)
    ax.set_ylabel('Week 1 ws', fontsize=6)

    #ax.set_xlabel('Week 1 ws', fontsize=6)
    #ax.set_ylabel('Week 2 ws', fontsize=6)

    #ax.set_xlabel('Week 2 ws', fontsize=6)
    #ax.set_ylabel('Week 3 ws', fontsize=6)

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

    loc.append(row[1:3])

    b = row[baseline_range['start']:baseline_range['end']]
    b = [float(x) for x in b]

    #BD.append(np.sqrt(np.mean(b)))
    BD.append(np.mean(b))

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

    X.append(b_ws)
    Y.append(c_wss[0])

    #X.append(c_wss[0])
    #Y.append(c_wss[1])

    #X.append(c_wss[1])
    #Y.append(c_wss[2])

    #draw_arrow(ax, c_wss[0], c_wss[1], c_wss[1], c_wss[2])


ax.scatter(X,Y,s=BD,alpha=args.alpha)
ax.set_ylim((-.75,1.75))
ax.set_xlim((-.75,1.75))

diag_line, = ax.plot(ax.get_xlim(), ax.get_ylim(), ls="--", lw=0.5, c='red')


clear_ax(ax)


plt.savefig(args.outfile,bbox_inches='tight')
