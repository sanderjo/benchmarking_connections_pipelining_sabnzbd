#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

connections = [5, 10, 20, 80]
pipelining = [1, 2, 5, 10, 20]

# Create a DataFrame with the specified index and columns
df = pd.DataFrame(index=connections, columns=pipelining)

# Name the index and columns
df.index.name = "Connections"
df.columns.name = "Pipelining"

print(df)

import numpy as np

# Fill the DataFrame with random integer values between 10 and 200
df[:] = np.random.randint(10, 201, size=df.shape)

print(df)

# Set the value at Connections=5 and Pipelining=10 to 333
df.loc[5, 10] = 333

print(df)