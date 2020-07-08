import numpy as np
import pandas as pd
import uuid
import time
import copy
import datetime
import math
import sys

"""
Command line arguments
1. slip score file
2. weekend score file
"""

def get_dist(p1,p2):
    return math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )


def subset_df(df,col1,col2,treshold,filename):
    indexes = list(range(df.shape[0]))
    keep_or_done_dict = { i:0 for i in indexes}
    for i in indexes:
        if i % 100 == 0:
            print(i)
        for j in indexes:
            if i == j:
                continue
            else:
                dist = get_dist([df.iloc[i,col1],df.iloc[i,col2]],[df.iloc[j,col1],df.iloc[j,col2]])
                if dist < treshold and keep_or_done_dict[i] >= 0:
                    keep_or_done_dict[j] = -1
                    keep_or_done_dict[i] = 1
    sum([ key for key in keep_or_done_dict if keep_or_done_dict[key] >= 0])
    final_indexes = [ key for key in keep_or_done_dict if keep_or_done_dict[key] >= 0]
    df[df.index.isin(final_indexes)].to_csv(filename)


ss_df = pd.read_csv(sys.argv[3] + sys.argv[1])
ws_df = pd.read_csv(sys.argv[3] + sys.argv[2])

ss_final = sys.argv[4] + 'unique_' + sys.argv[1]
ws_final = sys.argv[4] + 'unique_' + sys.argv[2]

subset_df(ss_df,4,5,.75, ss_final)
subset_df(ws_df,-2,-1,.05, ws_final)
