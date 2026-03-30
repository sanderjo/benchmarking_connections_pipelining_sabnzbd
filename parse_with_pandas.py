#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

#connections = [5, 10, 20, 80]
#pipelining = [1, 2, 5, 10, 20]

# Create a DataFrame with the specified index and columns
df = pd.DataFrame()

# Name the index and columns
df.index.name = "Connections"
df.columns.name = "Pipelining Articles"

#df.loc[5, 10] = 333 # so handy!

# filename is first argument
import sys
if len(sys.argv) < 2:
    print("Please provide a filename with benchmark results as an argument.")
    sys.exit(1)
filename = sys.argv[1]

nzb_size_printed = False

# read the file and fill the DataFrame with the values
with open(filename, 'r') as f:
    for line in f:
        line = line.strip()
        if "Using server:" in line or "Ping time" in line or "Internet speed" in line:
            print(line)
        if "Download has started" in line and not nzb_size_printed:
            print("test NZB size (MB): " + line.split(" ")[-1].strip()) # print the size of the NZB file
            nzb_size_printed = True
            print("\n")
        
        if "Average Speed:" in line:
            # servername: news.iad.newshosting.com, Connections 10, Pipelining 2: Average Speed: 53.6
            line = line.replace(",","").replace(":","")
            elements = line.split()
            #print(elements)
            # ['servername', 'news.iad.newshosting.com', 'Connections', '10', 'Pipelining', '2', 'Average', 'Speed', '53.6']
            servername = elements[1]
            connections = int(elements[3])
            pipelining = int(elements[5])
            speed = float(elements[8])
            df.loc[connections, pipelining] = speed


# set the index and columns to be in the order of connections_list and pipelining_list
# sort index and columns
df = df.sort_index()
df = df.sort_index(axis=1)

print(df)