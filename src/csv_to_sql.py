#!/usr/bin/env python
import sys
import glob
import subprocess
import sqlite3
import os

from optparse import OptionParser
parser = OptionParser()

parser.add_option("--csv",
                  dest="csv_path",
                  help="path to dir of csvs")

parser.add_option("--db",
                  dest="db_path",
                  help="Path to database file")

(options, args) = parser.parse_args()
if not options.db_path:
    parser.error('DB file not given')

if not options.csv_path:
    parser.error('Path to csvs not given')

f = open('tmp.sql', 'w')
f.write(".mode csv\n")

if os.path.exists(options.db_path):
    conn = sqlite3.connect(options.db_path)
    c = conn.cursor()
    c.execute('SELECT MAX(date_time) FROM pop_tile')
    last_db_date = c.fetchone()[0]

    for n in glob.glob(options.csv_path + '/*csv'):
        date_stamp = n.split('_')[-1].split('.')[0]

        if date_stamp > last_db_date:
            f.write(".import '| tail -n+2 \"" + n + "\"' pop_tile\n")

    f.close()
    print('sqlite3 ' + options.db_path + ' < tmp.sql')
else:
    first = True
    for n in glob.glob(options.csv_path + '/*csv'):
        if first:
            f.write('.import "' + n + '" pop_tile\n')
            first = False
        else:
            f.write(".import '| tail -n+2 \"" + n + "\"' pop_tile\n")

    f.close()
    bashCommand = 'rm -f ' + options.db_path + ';sqlite3 ' + options.db_path + ' < tmp.sql'
    print(bashCommand)
    #process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    #output, error = process.communicate()
