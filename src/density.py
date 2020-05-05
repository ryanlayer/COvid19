import  sys
import numpy as np
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import argparse
import csv
from sklearn.linear_model import LinearRegression

def clear_ax(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.spines['left'].set_visible(True)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().set_visible(True)
    ax.get_yaxis().set_visible(True)
    ax.yaxis.set_tick_params(labelsize=8)
    ax.xaxis.set_tick_params(labelsize=8)



shape_i = 0
baseline_range = {'start':3, 'end':24}
crisis_range = {'start':24}

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
        continue


    if args.shapename is None or row[shape_i] == args.shapename:

        b = row[baseline_range['start']:baseline_range['end']]
        b = [float(x) for x in b]

        c = row[crisis_range['start']:]
        c = [float(x) for x in c]

        B.append([float(x) for x in b])
        C.append([float(x) for x in c])

        row_i += 1

C_stats = []
for c in C:
    C_stats.append( ( np.mean(c), np.std(c) ) )

C_stats.sort(key=lambda x:x[0])

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

ax.scatter([c[0] for c in C_stats],
           [c[1] for c in C_stats],
           3,
           alpha=0.25)

model = LinearRegression()
x=[[c[0]] for c in C_stats]
y=[[c[1]] for c in C_stats]
model.fit(x,y)
r = model.score(x,y)
print(r, model.predict([[100]]))
x_new = np.linspace(0, max([c[0] for c in C_stats]), 10)
y_new = model.predict(x_new[:, np.newaxis])
ax.plot(x_new,
        y_new,
        '-',
        linewidth=1,
        c='black')

ax.set_xlabel('$\mu$')
ax.set_ylabel('$\sigma$')

clear_ax(ax)

plt.savefig(args.outfile,bbox_inches='tight')
