#!/usr/bin/env python
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import random
from optparse import OptionParser
import argparse

#{{{
parser = argparse.ArgumentParser()

parser.add_argument("--rows",
                    dest="rows",
                    type=int,
                    default=1,
                    help="Nubmer of rows in figure")


parser.add_argument("--xticks",
                    dest="xticks",
                    help="CSV ints to tick and label")

parser.add_argument("--xtick_names",
                    dest="xtick_names",
                    help="CSV of xtick lables")


parser.add_argument("--numyticks",
                    dest="numyticks",
                    help="Number of Y ticks")

parser.add_argument("-t",
                    "--title",
                    dest="title",
                    help="Title")

parser.add_argument("-x",
                    "--xlabel",
                    dest="xlabel",
                    help="X axis label")

parser.add_argument("-y",
                    "--ylabel",
                    dest="ylabel",
                    help="Y axis label")

parser.add_argument("-o",
                    "--output_file",
                    dest="output_file",
                    required=True,
                    help="Data file")

parser.add_argument("-b",
                    "--bins",
                    dest="bins",
                    type=int,
                    default=10,
                    help="Number of fins")

parser.add_argument("--x_max",
                    dest="max_x",
                    type=float,
                    help="Max x value")


parser.add_argument("--x_min",
                    dest="min_x",
                    type=float,
                    help="Min x value")

parser.add_argument("--y_max",
                    dest="max_y",
                    type=float,
                    help="Max y value")


parser.add_argument("--y_min",
                    dest="min_y",
                    type=float,
                    help="Min y value")

parser.add_argument("--color",
                    dest="color",
                    default=None,
                    help="Bar color")

parser.add_argument("-d",
                    "--delim",
                    dest="delim",
                    default="\t",
                    help="Field delimiter")

parser.add_argument("-l",
                    "--ylog",
                    action="store_true",
                    default=False,
                    dest="ylog",
                    help="Field delimiter")

parser.add_argument("--x_sci",
                    action="store_true",default=False,
                    dest="x_sci",
                    help="Use scientific notation for x-axis")

parser.add_argument("--y_sci",
                    action="store_true",default=False,
                    dest="y_sci",
                    help="Use scientific notation for y-axis")

parser.add_argument("--width",
                    dest="width",
                    type=float,
                    default=5,
                    help="Figure width")

parser.add_argument("--height",
                    dest="height",
                    type=float,
                    default=5,
                    help="Figure height")

parser.add_argument("--black",
                    action="store_true", 
                    default=False,
                    dest="black",
                    help="black background")

args = parser.parse_args()
#}}}

Y=[]
for l in sys.stdin:
    y = [float(x) for x in  l.rstrip().split(args.delim)]
    Y.append(y)

fig = None
if args.black:
    fig = plt.figure(figsize=(args.width,args.height),
                      dpi=300,
                      facecolor='black')
else:
    fig = plt.figure(figsize=(args.width,args.height),
                      dpi=300)


x_max = max(Y)
x_min = min(Y)

if args.max_x:
    x_max = args.max_x
if args.min_x:
    x_min = args.min_x

rows=1
cols=1
outer_grid = gridspec.GridSpec(rows, cols, wspace=0.0, hspace=0.0)

inner_grid = gridspec.GridSpecFromSubplotSpec(\
        1,
        len(Y),
        subplot_spec=outer_grid[0],
        wspace=0.25,
        hspace=0.0)

plot_i = 0
axs = []
max_freqs = []
min_bins = []
max_bins = []
for y in Y:

    ax = None

    if args.black:
        ax = fig.add_subplot(inner_grid[plot_i], facecolor='k')
    else:
        ax = fig.add_subplot(inner_grid[plot_i])

    axs.append(ax)

    n, bins, patches = ax.hist(y,
                               args.bins,
                               log=args.ylog, 
                               histtype='bar', 
                               rwidth=1, 
                               color=args.color)
    max_freqs.append(max(n))
    min_bins.append(min(bins))
    max_bins.append(max(bins))

    plot_i += 1

plot_i = 0
for y in Y:
    ax = axs[plot_i]

    ax.set_ylim(ymax=max(max_freqs))
    ax.set_xlim((min(min_bins),max(max_bins)))

    median = np.median(y)
    ax.axvline(x=median, lw=1.0, ls='--', c = 'black')
    #ax.axvline(x=0, lw=1.0, ls='-', c = 'black')
    ax.text(median,
            ax.get_ylim()[1],
            str(round(median,3)),
            verticalalignment='top',
            fontsize=8)

    if args.max_x:
        ax.set_xlim(xmax=args.max_x)
    if args.min_x:
        ax.set_xlim(xmin=args.min_x)
    if args.max_y:
        ax.set_ylim(ymax=args.max_y)
    if args.min_y:
        ax.set_ylim(ymin=args.min_y)

    if args.x_sci:
        formatter = matplotlib.ticker.ScalarFormatter()
        formatter.set_powerlimits((-2,2))
        ax.xaxis.set_major_formatter(formatter)

    if args.y_sci:
        formatter = matplotlib.ticker.ScalarFormatter()
        formatter.set_powerlimits((-2,2))
        ax.yaxis.set_major_formatter(formatter)

    if args.xlabel:
        ax.set_xlabel(args.xlabel.split(',')[plot_i])

    if plot_i == 0 and args.ylabel:
        ax.set_ylabel(args.ylabel)

    if args.title:
        ax.set_title(args.title)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    if args.xticks:
        xticks = [int(x) for x in args.xticks.split(',')]
        xmajorlocator = matplotlib.ticker.FixedLocator(xticks)
        ax.xaxis.set_major_locator(xmajorlocator)

    if args.xtick_names:
        xtick_locs = []
        xtick_names = []

        i = 0
        for xtick_name in args.xtick_names.split(','):
            if xtick_name != '':
                xtick_locs.append(i)
                xtick_names.append(xtick_name)
            i+=1

        xmajorlocator = matplotlib.ticker.FixedLocator(xtick_locs)
        ax.xaxis.set_major_locator(xmajorlocator)
        ax.set_xticklabels(xtick_names)

    if args.black:
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.title.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.xaxis.label.set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

    plot_i+=1

if args.black:
    plt.savefig(args.output_file,
                 bbox_inches='tight',
                 facecolor=fig.get_facecolor(),
                 transparent=True)
else:
    plt.savefig(args.output_file,
                bbox_inches='tight')
