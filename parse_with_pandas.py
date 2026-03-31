#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

# Create a DataFrame to hold the results, with connections as index and pipelining as columns
df = pd.DataFrame()
# Name the index and columns
df.index.name = "Connections"
df.columns.name = "Pipelining Articles"

#df.loc[5, 10] = 333 # so easy to fill out!

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
            nzb_size_mb = line.split(" ")[-1].strip()
            nzb_size_gb = float(nzb_size_mb) / 1024
            print(f"test NZB size (GB): {nzb_size_gb:.1f}")
            nzb_size_printed = True
            print("\n")
        
        # the real benchmark results:
        if "Average Speed:" in line:
            # servername: news.iad.newshosting.com, Connections 10, Pipelining 2: Average Speed: 53.6
            line = line.replace(",","").replace(":","") # remove commas and colons to make splitting easier
            elements = line.split()
            # ['servername', 'news.iad.newshosting.com', 'Connections', '10', 'Pipelining', '2', 'Average', 'Speed', '53.6']
            servername = elements[1]
            connections = int(elements[3])
            pipelining = int(elements[5])
            speed = float(elements[8])
            df.loc[connections, pipelining] = speed

print("unsorted DataFrame:")
print(df)
print("\n")

# sort index and columns
df = df.sort_index()
df = df.sort_index(axis=1)

print(df)