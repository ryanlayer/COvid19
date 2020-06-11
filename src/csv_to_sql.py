#!/usr/bin/env python
import sys
import glob
import subprocess
import sqlite3
import os
import tempfile
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--csv",
                  dest="csv_path",
                  help="path to dir of csvs")

parser.add_argument("--db",
                    dest="db_path",
                    help="Path to database file")

args = parser.parse_args()

if not args.db_path:
    parser.error('DB file not given')

if not args.csv_path:
    parser.error('Path to csvs not given')

tmp_file = tempfile.gettempdir() + '/' \
        + os.path.basename(args.db_path) \
        + '.sql'

f = open(tmp_file, 'w')
f.write(".mode csv\n")

if os.path.exists(args.db_path):
    conn = sqlite3.connect(args.db_path)
    c = conn.cursor()
    c.execute('SELECT MAX(date_time) FROM pop_tile')
    last_db_date = c.fetchone()[0]

    for n in glob.glob(args.csv_path + '/*csv'):
        date_stamp = n.split('_')[-1].split('.')[0]

        if date_stamp > last_db_date:
            f.write(".import '| tail -n+2 \"" + n + "\"' pop_tile\n")

    f.close()
    print('sqlite3 ' + args.db_path + ' < ' + tmp_file)
else:
    first = True
    for n in glob.glob(args.csv_path + '/*csv'):
        if first:
            f.write('.import "' + n + '" pop_tile\n')
            first = False
        else:
            f.write(".import '| tail -n+2 \"" + n + "\"' pop_tile\n")

    f.close()
    print('rm -f ' + args.db_path + ';sqlite3 ' \
            + args.db_path + ' < ' + tmp_file)

